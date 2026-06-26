from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from graph import run_workflow

app = FastAPI(title="AI Shopping Advisor API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    direct_category: Optional[str] = None

class Recommendation(BaseModel):
    name: str
    price_usd: Optional[float] = None
    category: Optional[str] = None
    justification: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    specs_summary: Optional[str] = None

class SearchResponse(BaseModel):
    user_preferences: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

@app.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    try:
        # Run the workflow
        state = run_workflow(request.query, direct_category=request.direct_category)
        
        # Extract results
        recommendations = state.get("system_findings", {}).get("recommendations", [])
        prefs = state.get("user_preferences", {})
        
        return SearchResponse(
            user_preferences=prefs,
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
