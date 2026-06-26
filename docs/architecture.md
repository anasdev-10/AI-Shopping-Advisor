# AI-Powered Intelligent Shopping Advisor

## 1. Introduction
Online shopping platforms provide thousands of product options, which makes decision-making difficult for users. Buyers usually need to manually compare prices, specifications, and ratings before selecting a product. This project addresses that challenge by building an AI-powered shopping advisor that understands natural language queries and recommends the best product matches.

The system combines web scraping, data storage, filtering logic, ranking, and LLM-based explanation generation. A user can ask for products using plain language (for example, "Find me a laptop under 200k with 16GB RAM"), and the system returns ranked recommendations with justifications.

## 2. Project Objectives
- Build an end-to-end shopping recommendation workflow.
- Extract products from e-commerce pages and store them in a structured database.
- Parse user preferences from natural language queries.
- Retrieve and rank products using budget, category, brand, and specs.
- Generate human-readable recommendation reasons with an LLM.

## 3. Technology Stack
- **Programming Language:** Python
- **Workflow/Orchestration:** LangGraph-style node pipeline
- **Data Processing:** pandas
- **Web Scraping:** requests + BeautifulSoup + ZenRows API
- **Database:** MongoDB (pymongo)
- **LLM Integration:** Ollama (`llama3.2:3b`)
- **Visualization:** matplotlib (architecture diagram)

Dependencies are listed in `requirements.txt`:
- `langgraph`
- `pandas`
- `ollama`
- `pymongo`
- `requests`
- `beautifulsoup4`

## 4. System Architecture
The project follows a multi-agent pipeline where each node handles a specific responsibility:

1. **Preference Node**
   - Reads user query.
   - Uses LLM prompt engineering to extract structured preferences:
     - budget
     - category
     - brand
     - RAM
     - storage
     - must-have keywords
     - avoid keywords
   - Includes fallback parsing when JSON extraction fails.

2. **Retrieval Node**
   - Loads product data from CSV, JSON, DataFrame/list, or MongoDB.
   - Applies filters in sequence:
     - category
     - brand
     - RAM
     - storage
     - budget
     - must-have terms
     - avoid terms
   - Saves filtered products into workflow state.

3. **Comparison Node**
   - Scores products using a weighted formula:
     - price score (40%)
     - feature score from `must_have` matches (30%)
     - rating score (30%)
   - Sorts products by composite score.

4. **Recommendation Node**
   - Picks top products (up to 3).
   - Uses LLM to generate concise, user-facing recommendation justifications.
   - Stores final recommendations in state output.

The architecture and data flow are visualized in `diagram.py`.

## 5. Data Pipeline
### 5.1 Data Collection
`scraper.py` scrapes Amazon search result pages through ZenRows to bypass anti-bot restrictions and JS rendering issues. It extracts:
- product name
- brand
- price
- rating
- source metadata
- scrape timestamp

### 5.2 Data Cleaning and Validation
The scraper normalizes:
- **Price** into numeric format (`price_pkr`)
- **Rating** into float values

Products are validated before insertion:
- name must be present and meaningful
- price must be greater than zero
- category must be assigned

### 5.3 Storage
Validated products are upserted into MongoDB using a stable `_id` (ASIN for Amazon records), preventing duplicate entries.

## 6. State Management
`state.py` defines a structured shared state with three sections:
- **user_preferences**
- **system_findings**
- **metadata**

This state-based design improves traceability and keeps each node focused on a single job while passing context across steps.

## 7. Current Output Behavior
Given a user query, the system:
1. Extracts preferences with LLM.
2. Retrieves matching products from source data.
3. Ranks products with scoring logic.
4. Produces top recommendations with generated explanations.

The sample local dataset (`products.csv`) includes phone and laptop entries with fields required for matching and ranking.

## 8. Strengths of the Project
- Clear modular architecture (easy to maintain and extend).
- Works with multiple data sources (CSV/JSON/MongoDB).
- Real-world scraping support through ZenRows.
- Hybrid recommendation approach:
  - deterministic filtering + scoring
  - LLM-based natural language reasoning
- Good foundation for conversational commerce applications.

## 9. Limitations
- Budget filter implementation in `graph.py` should be reviewed for DataFrame boolean chaining correctness.
- Recommendation quality depends on extracted product text quality.
- LLM output may vary between runs.
- No automated test suite is currently included.
- No dedicated API/UI layer yet for production usage.

## 10. Future Enhancements
- Add unit and integration tests for all nodes.
- Introduce robust error handling and retry logic for scraping/LLM calls.
- Improve ranking with personalization signals (brand loyalty, historical clicks).
- Add vector/semantic search for better retrieval.
- Expose the workflow as REST API and web UI.
- Add monitoring/logging for production observability.

## 11. Conclusion
This project successfully demonstrates an intelligent shopping advisor pipeline that integrates data acquisition, preference understanding, product retrieval, ranking, and explainable recommendations. The current implementation provides a solid prototype for AI-assisted e-commerce decision support. With testing, UI/API deployment, and ranking enhancements, it can evolve into a practical production-grade recommendation assistant.

