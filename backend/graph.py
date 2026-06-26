"""LangGraph workflow for shopping advisor.

Defines four nodes: preference_node, retrieval_node, comparison_node, recommendation_node.
Connects them in sequence for the information flow.
"""

import copy
import json
import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Gemini Client
from google import genai

gemini_client = None
if os.environ.get("GEMINI_API"):
    gemini_client = genai.Client(api_key=os.environ["GEMINI_API"].strip('"'))
    MODEL_ID = "gemini-3.1-flash-lite"
else:
    print("WARNING: GEMINI_API key not found in environment.")
    MODEL_ID = None

from pymongo import MongoClient
from state import State, initialize_state, update_user_preferences, add_matched_products, add_recommendations
import re


def preference_node(state: State) -> State:
    """Extract user preferences from query text using LLM."""
    query = state["metadata"]["query_text"]
    print(f"Preference Node: Processing query '{query}' with LLM")

    prompt = f"""
Identify and structure user shopping preferences from this query: "{query}".

CRITICAL INSTRUCTIONS:
1. CATEGORY: If the user mentions a product (e.g., "laptop", "phone", "monitor"), set this as the 'category'. 
2. BUDGET: Convert shorthand like '200k' or '100k' into full numbers (e.g., 200000).
3. AVOID: If the user is looking for a main device (like a laptop or phone), automatically add accessory keywords to the 'avoid' list (e.g., ["case", "cover", "sticker", "decal", "charger", "sleeve", "protector"]) unless they explicitly ask for an accessory.
4. JSON ONLY: Output strictly a JSON object. No markdown, no "here is the json", no backticks.

Expected JSON Schema:
{{
  "budget": number or null,
  "category": string or null,
  "brand": string or null,
  "ram": string or null,
  "storage": string or null,
  "must_have": [],
  "avoid": []
}}
"""

    try:
        if gemini_client:
            response = gemini_client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            extracted = response.text.strip()
        else:
            raise ValueError("Gemini client is not configured")
        
        print(f"LLM Response: {extracted}")

        # Extract the first JSON object found in the response text.
        json_match = re.search(r"\{.*\}", extracted, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in LLM response")

        prefs = json.loads(json_match.group(0))
        if not isinstance(prefs, dict) or 'category' not in prefs:
            raise ValueError("Parsed JSON did not contain expected preference keys")

        update_user_preferences(state, **prefs)
    except Exception as e:
        print(f"Error extracting preferences: {e}. Falling back to simple parsing.")
        # Fallback to simple parsing
        if "under" in query.lower() and "k" in query.lower():
            budget_str = query.split("under")[1].split("k")[0].strip()
            try:
                budget = int(budget_str) * 1000
                update_user_preferences(state, budget=budget)
            except ValueError:
                pass

        # Generic category fallback based on common phrasing
        fallback_match = re.search(
            r"\b(?:for|need|want|looking for|search for|find me|find a|find an)\s+(?:a |an |the )?([a-z0-9 ]+?)(?: under| with| from| near| for|$)",
            query.lower()
        )
        if fallback_match:
            fallback_category = fallback_match.group(1).strip()
            if fallback_category:
                update_user_preferences(state, category=fallback_category)

    return state


from sqlalchemy import select, and_, or_, cast, Float, func
from db import engine, get_clean_products_table

def retrieval_node(state: State) -> State:
    """Retrieve products based on all parsed preferences directly from PostgreSQL."""
    print("Retrieval Node: Fetching products from database")
    prefs = state["user_preferences"]
    
    try:
        clean_products = get_clean_products_table()
    except Exception as e:
        print(f"Database error: {e}")
        return state
        
    stmt = select(clean_products)
    where_clauses = []
    
    if prefs.get("category"):
        category = prefs["category"].strip().lower()
        
        # Map specific items to strict database categories
        category_map = {
            "laptops": "laptops",
            "laptop": "laptops",
            "smartphones": "smartphones",
            "smartphone": "smartphones",
            "phones": "smartphones",
            "phone": "smartphones",
            "cameras": "cameras",
            "camera": "cameras",
            "headphones": "headphones",
            "headphone": "headphones",
            "smartwatches": "smartwatches",
            "watches": "smartwatches",
            "watch": "smartwatches",
            "accessories": "accessories",
            "accessory": "accessories"
        }
        
        mapped = category_map.get(category)
        
        if mapped:
            db_cat = mapped
            # Strict match: Must be in the correct DB category
            where_clauses.append(clean_products.c.category == db_cat)
        else:
            # Fallback: loose search
            where_clauses.append(or_(
                func.word_similarity(category, clean_products.c.category) > 0.3,
                func.word_similarity(category, clean_products.c.name) > 0.3,
                func.word_similarity(category, clean_products.c.specs_summary) > 0.3
            ))
        
    if prefs.get("brand"):
        brand = prefs["brand"].strip().lower()
        where_clauses.append(or_(
            func.word_similarity(brand, clean_products.c.brand) > 0.3,
            func.word_similarity(brand, clean_products.c.name) > 0.3,
            func.word_similarity(brand, clean_products.c.specs_summary) > 0.3
        ))

    if prefs.get("ram"):
        ram = prefs["ram"].strip().lower()
        where_clauses.append(or_(
            clean_products.c.ram.ilike(f"%{ram}%"),
            clean_products.c.specs_summary.ilike(f"%{ram}%"),
            clean_products.c.name.ilike(f"%{ram}%")
        ))

    if prefs.get("storage"):
        storage = prefs["storage"].strip().lower()
        where_clauses.append(or_(
            clean_products.c.storage.ilike(f"%{storage}%"),
            clean_products.c.specs_summary.ilike(f"%{storage}%"),
            clean_products.c.name.ilike(f"%{storage}%")
        ))

    if prefs.get("budget") is not None:
        try:
            budget = float(prefs["budget"])
            where_clauses.append(clean_products.c.price_usd <= budget)
            where_clauses.append(clean_products.c.price_usd.is_not(None))
        except (TypeError, ValueError):
            pass

    if prefs.get("must_have"):
        must_have = [str(item).strip().lower() for item in prefs["must_have"] if str(item).strip()]
        for keyword in must_have:
            where_clauses.append(or_(
                clean_products.c.name.ilike(f"%{keyword}%"),
                clean_products.c.brand.ilike(f"%{keyword}%"),
                clean_products.c.category.ilike(f"%{keyword}%"),
                clean_products.c.specs_summary.ilike(f"%{keyword}%")
            ))

    if prefs.get("avoid"):
        avoid = [str(item).strip().lower() for item in prefs["avoid"] if str(item).strip()]
        for keyword in avoid:
            where_clauses.append(and_(
                ~clean_products.c.name.ilike(f"%{keyword}%"),
                ~clean_products.c.brand.ilike(f"%{keyword}%"),
                ~clean_products.c.category.ilike(f"%{keyword}%"),
                ~clean_products.c.specs_summary.ilike(f"%{keyword}%")
            ))

    if where_clauses:
        stmt = stmt.where(and_(*where_clauses))
    
    stmt = stmt.limit(1000)

    matched = []
    with engine.connect() as conn:
        results = conn.execute(stmt)
        for row in results.mappings():
            matched.append(dict(row))

    add_matched_products(state, matched)
    return state


def comparison_node(state: State) -> State:
    """Compare retrieved products using price, features, and ratings."""
    print("Comparison Node: Comparing products")
    matched = state["system_findings"]["matched_products"]
    if not matched:
        return state

    prefs = state["user_preferences"]
    must_have = [str(item).strip().lower() for item in prefs.get("must_have", []) if str(item).strip()]

    # --- Agentic Reranking ---
    target_category = prefs.get("category")
    if target_category and gemini_client:
        import random
        candidates_pool = list(matched)
        random.shuffle(candidates_pool)
        
        # Take up to 60 items to ensure we get a good mix before filtering
        top_candidates = candidates_pool[:60]
        query_text = state.get("metadata", {}).get("query_text", "")
        
        print(f"Comparison Node: Running Agentic Reranking on {len(top_candidates)} candidates")
        prompt = f"""
        User Query: "{query_text}"
        Target Category: "{target_category}"
        
        Below are {len(top_candidates)} products retrieved from our database using keyword matching.
        Because keyword matching is imperfect, some of these are HALLUCINATIONS.
        For example:
        - If Target Category is 'laptops' or 'laptop', a 'laptop stand' or 'laptop case' is a HALLUCINATION.
        - If Target Category is 'cameras' or 'camera', a 'smartphone' with a camera is a HALLUCINATION.
        
        Your task is to strictly filter out any product that is NOT exactly what the user is looking for.
        Keep only the true primary devices matching the target category.
        
        Candidates:
        """
        for i, p in enumerate(top_candidates):
            prompt += f"\n[{i}] Name: {p.get('name')} | Specs: {p.get('specs_summary')}"
            
        prompt += """
        
        Output ONLY a valid JSON list of integers representing the indices of the products that are TRULY relevant. 
        Example output: [0, 2, 5]
        If none are relevant, output: []
        Output strictly JSON. Do not include markdown formatting or backticks.
        """
        
        try:
            response = gemini_client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            extracted = response.text.strip()
            
            import re
            json_match = re.search(r"\[.*\]", extracted, re.DOTALL)
            if json_match:
                valid_indices = json.loads(json_match.group(0))
                filtered_products = [top_candidates[i] for i in valid_indices if 0 <= i < len(top_candidates)]
                
                # Trust the AI filter
                if len(filtered_products) > 0:
                    matched = filtered_products
                else:
                    print("Agentic Reranking rejected all candidates. Setting matched to empty.")
                    matched = []
            else:
                print("Failed to parse JSON from LLM reranker.")
        except Exception as e:
            print(f"Agentic reranking error: {e}")

    # Get max price for normalization
    prices = [p["price_usd"] for p in matched if p.get("price_usd") is not None]
    max_price = max(prices) if prices else 1
    def calculate_score(product):
        # Price score: lower price is better (normalized 0-1)
        price = product.get("price_usd")
        if price is None:
            price = max_price
        price_score = 1 - (price / max_price) if max_price > 0 else 0

        # Feature score: fraction of must_have keywords matched in specs_summary
        specs = str(product.get("specs_summary", "")).lower()
        feature_matches = sum(1 for keyword in must_have if keyword in specs)
        feature_score = feature_matches / len(must_have) if must_have else 0

        # Rating score: rating out of 5, normalized 0-1
        rating = product.get("rating")
        if rating is None:
            rating = 3.0
        rating_score = float(rating) / 5.0

        # Composite score: weighted average (adjust weights as needed)
        composite = 0.4 * price_score + 0.3 * feature_score + 0.3 * rating_score
        return composite

    # Sort by composite score descending (highest first)
    sorted_products = sorted(matched, key=calculate_score, reverse=True)
    state["system_findings"]["matched_products"] = sorted_products
    return state


def recommendation_node(state: State) -> State:
    """Generate recommendations with justifications."""
    print("Recommendation Node: Generating recommendations")
    matched = state["system_findings"]["matched_products"]
    selected = matched[:3] if len(matched) >= 3 else matched
    recommendations = [copy.deepcopy(product) for product in selected]

    prefs = state["user_preferences"]
    query = state["metadata"]["query_text"]

    for product in recommendations:
        # Build justification using LLM
        product_details = f"""
Product: {product.get('name', 'Unknown')}
Brand: {product.get('brand', 'Unknown')}
Category: {product.get('category', 'Unknown')}
Price: {product.get('price_usd', 'Unknown')} USD
RAM: {product.get('ram', 'Unknown')}
Storage: {product.get('storage', 'Unknown')}
Rating: {product.get('rating', 'Unknown')}
Specs: {product.get('specs_summary', 'Unknown')}
"""

        prompt = f"""
User query: "{query}"
User preferences: {prefs}
Product details: {product_details}

Explain in 2-3 sentences why this product is recommended based on the query and preferences. Be concise and highlight key matches.
"""

        try:
            if gemini_client:
                response = gemini_client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                justification = response.text.strip()
            else:
                raise ValueError("Gemini client not configured")
        except Exception as e:
            justification = f"This product matches your preferences for {prefs.get('category', 'category')} within budget."

        product["justification"] = justification

    add_recommendations(state, recommendations)
    return state


# Simple flow without LangGraph for now
def run_workflow(query: str, direct_category: str = None) -> State:
    state = initialize_state(query, data_source=None)
    
    if direct_category:
        print(f"Bypassing LLM Extraction: Using direct category '{direct_category}'")
        
        avoid_list = []
        if direct_category in ["laptops", "smartphones", "cameras", "smartwatches"]:
            avoid_list = ["sticker", "case", "cover", "protector", "decal", "charger", "cable", "sleeve", "strap", "band"]

        state["user_preferences"] = {
            "budget": None,
            "category": direct_category,
            "brand": None,
            "ram": None,
            "storage": None,
            "must_have": [],
            "avoid": avoid_list
        }
    else:
        state = preference_node(state)
        
    state = retrieval_node(state)
    state = comparison_node(state)
    state = recommendation_node(state)
    return state


if __name__ == "__main__":
    # Test the workflow with Supabase PostgreSQL integration
    result = run_workflow("Find me appliances under 10 dollars")
    print("Final State:")
    import json
    
    # We serialize the state safely, skipping things that aren't easily printed
    print("Preferences:", result["user_preferences"])
    
    recommendations = result.get("system_findings", {}).get("recommendations", [])
    print(f"\nTop {len(recommendations)} Recommendations:")
    for idx, r in enumerate(recommendations, 1):
        print(f"\n--- Recommendation {idx} ---")
        print(f"Name: {r.get('name')}")
        print(f"Price: ${r.get('price_usd')}")
        print(f"Category: {r.get('category')}")
        print(f"Justification: {r.get('justification')}")