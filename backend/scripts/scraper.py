import argparse
import hashlib
import json
import random
import re
import time
import os
from datetime import datetime
from typing import Any

import requests
import bs4
from pymongo import MongoClient
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")

def get_mongo_collection(uri: str, db_name: str, collection_name: str):
    client = MongoClient(uri)
    return client[db_name][collection_name]

def normalize_price(price_text: str) -> float:
    if not price_text:
        return 0.0
    # Handle ranges by taking the first number (e.g., "$900 - $1000" -> 900)
    if "-" in price_text:
        price_text = price_text.split("-")[0]
        
    text = re.sub(r"[^0-9.]", "", price_text.replace(",", ""))
    try:
        return float(text)
    except ValueError:
        return 0.0

def normalize_rating(rating_text: str) -> float:
    if not rating_text:
        return 0.0
    match = re.search(r"([0-9]+\.?[0-9]*)", rating_text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def make_product_id(product: dict) -> str:
    raw = f"{product.get('name')}|{product.get('brand')}|{product.get('category')}|{product.get('price_pkr')}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def fetch_page(url: str) -> bs4.BeautifulSoup:
    """Uses ZenRows API to fetch rendered HTML, bypassing anti-bot measures."""
    if not ZENROWS_API_KEY:
        raise ValueError("ZENROWS_API_KEY not found in .env file")

    api_url = "https://api.zenrows.com/v1/"
    
    # premium_proxy and js_render are required for Amazon
    params = {
        "url": url,
        "apikey": ZENROWS_API_KEY,
        "js_render": "true",
        "premium_proxy": "true",
        "wait": "2000" # Wait 2 seconds for JS to finish rendering
    }

    print(f"Requesting via ZenRows: {url}")
    response = requests.get(api_url, params=params, timeout=60)
    
    if response.status_code != 200:
        print(f"ZenRows Error {response.status_code}: {response.text}")
        response.raise_for_status()
        
    return bs4.BeautifulSoup(response.text, "html.parser")

def scrape_amazon_search_page(url: str) -> list[dict]:
    soup = fetch_page(url)
    
    # Broaden the search for product cards
    results = soup.select("div[data-component-type='s-search-result']")
    
    # If no results found, let's try an even broader selector
    if not results:
        results = soup.select(".s-result-item[data-asin]")

    products = []
    print(f"Found {len(results)} potential product cards. Extracting...")

    for card in results:
        asin = card.get("data-asin")
        if not asin or asin == "":
            continue

        # More robust Title search
        title_node = card.select_one("h2 a span") or card.select_one("h2") or card.select_one(".a-size-medium")
        
        # More robust Price search
        price_whole = card.select_one("span.a-price-whole")
        price_fraction = card.select_one("span.a-price-fraction")
        
        price_text = ""
        if price_whole:
            whole = price_whole.get_text(strip=True)
            fraction = price_fraction.get_text(strip=True) if price_fraction else "00"
            price_text = f"{whole}.{fraction}"
        else:
            # Fallback for "Offscreen" text or different price classes
            price_node = card.select_one(".a-price .a-offscreen") or card.select_one(".a-color-base")
            price_text = price_node.get_text(strip=True) if price_node else ""

        # Rating and Brand
        rating_text = extract_first_text(card, ["span.a-icon-alt", ".a-icon-star-small"])
        brand = extract_first_text(card, [".a-size-base-plus", ".s-line-clamp-1"])

        product_name = title_node.get_text(strip=True) if title_node else "Unknown"

        product = {
            "name": product_name,
            "brand": brand or None,
            "category": None, 
            "price_pkr": normalize_price(price_text),
            "ram": None,
            "storage": None,
            "specs_summary": product_name, # Default to name if specs not found
            "rating": normalize_rating(rating_text),
            "source_url": url,
            "source": "amazon",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
        }
        product["_id"] = asin
        products.append(product)

    return products
def extract_first_text(element, selectors: list[str]) -> str:
    for selector in selectors:
        node = element.select_one(selector)
        if node and node.get_text(strip=True):
            return node.get_text(strip=True)
    return ""

def is_valid_product(product: dict) -> bool:
    if not product.get("name") or len(product["name"]) < 5:
        return False
    if not product.get("price_pkr") or product["price_pkr"] <= 0:
        return False
    if not product.get("category"):
        return False
    return True

def upsert_products(collection, products: list[dict]) -> int:
    if not products:
        return 0
    for product in products:
        # Filter out None values to keep DB clean
        clean_product = {k: v for k, v in product.items() if v is not None}
        collection.replace_one({"_id": clean_product["_id"]}, clean_product, upsert=True)
    return len(products)

def main():
    parser = argparse.ArgumentParser(description="Scrape Amazon via ZenRows.")
    parser.add_argument("--mongo-uri", required=True)
    parser.add_argument("--db", default="shopping_advisor")
    parser.add_argument("--collection", default="products")
    parser.add_argument("--url", required=True)
    parser.add_argument("--category", required=True, help="Category name (e.g., 'laptop')")
    parser.add_argument("--clear", action="store_true", help="Clear collection before scraping")
    args = parser.parse_args()

    collection = get_mongo_collection(args.mongo_uri, args.db, args.collection)
    
    if args.clear:
        print(f"Clearing collection {args.collection}...")
        collection.delete_many({})

    print(f"Scraping Amazon via ZenRows: {args.url}")
    
    # 1. Fetch and parse
    raw_scraped = scrape_amazon_search_page(args.url)
    
    # 2. Assign category and validate
    validated_products = []
    for p in raw_scraped:
        p["category"] = args.category # Apply the forced category
        if is_valid_product(p):
            validated_products.append(p)
        else:
            print(f"Skipping invalid product: {p.get('name', 'Unknown')[:30]}...")

    # 3. Save
    count = upsert_products(collection, validated_products)
    print(f"Successfully saved {count} high-quality products to {args.collection}.")

if __name__ == "__main__":
    main()