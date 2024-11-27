# backend/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from wiki_processor.processor import WikiDatasetProcessor
from wiki_processor.utils import ensure_directory
from typing import List
import uvicorn
from pathlib import Path
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wiki-Forge API")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
OUTPUT_DIR = Path("output")
ensure_directory(OUTPUT_DIR)

class ProcessRequest(BaseModel):
    titles: List[str]

class ProcessResponse(BaseModel):
    job_id: str
    message: str

@app.post("/api/process-wiki")
async def process_wiki_articles(request: ProcessRequest):
    """
    Process Wikipedia articles and return statistics.
    
    Args:
        request (ProcessRequest): Request containing list of article titles
        
    Returns:
        Dict: Processing statistics
    """
    try:
        if not request.titles:
            raise HTTPException(
                status_code=400,
                detail="No article titles provided"
            )
            
        processor = WikiDatasetProcessor()
        df = processor.process_articles(
            request.titles,
            str(OUTPUT_DIR / "processed_articles")
        )
        
        stats = processor.get_article_statistics(df)
        return {"statistics": stats}
        
    except Exception as e:
        logger.error(f"Error processing articles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing articles: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)