"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas import HealthResponse
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="Clinical Decision Support System",
        version="1.0.0",
        timestamp=datetime.now()
    )


@router.get("/database", response_model=dict)
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database connectivity health check
    """
    try:
        # Simple query to test database connection - using text() for SQLAlchemy 2.0+
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Get additional database info
        database_type = "sqlite" if "sqlite" in str(db.bind.url) else "postgresql"
        
        return {
            "status": "healthy",
            "database": "connected",
            "database_type": database_type,
            "test_query": "successful",
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now()
        }