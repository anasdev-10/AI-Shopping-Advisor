"""LangGraph shopping advisor state definition.

In LangGraph, the State is a simple Python dictionary that stores
what the user wants and what the system finds.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

State = Dict[str, Any]


def initialize_state(query_text: str = "", data_source: Any = None) -> State:
    if data_source is None:
        data_source = {"type": "csv", "path": "products.csv"}

    return {
        "user_preferences": {
            "budget": None,
            "category": None,
            "brand": None,
            "ram": None,
            "storage": None,
            "must_have": [],
            "avoid": [],
        },
        "system_findings": {
            "matched_products": [],
            "recommendations": [],
            "extraction_log": [],
            "confidence": None,
        },
        "metadata": {
            "query_text": query_text,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "data_source": data_source,
        },
    }


def update_user_preferences(state: State, **preferences: Any) -> None:
    state["user_preferences"].update(preferences)
    state["system_findings"]["extraction_log"].append(
        {"event": "preferences_updated", "values": preferences}
    )


def add_matched_products(state: State, products: List[Dict[str, Any]]) -> None:
    state["system_findings"]["matched_products"].extend(products)


def add_recommendations(state: State, products: List[Dict[str, Any]]) -> None:
    state["system_findings"]["recommendations"].extend(products)


if __name__ == "__main__":
    state = initialize_state("Find me a laptop under 200k with 16GB RAM")
    update_user_preferences(state, budget=200000, category="laptop", ram="16GB")
    print(state)
