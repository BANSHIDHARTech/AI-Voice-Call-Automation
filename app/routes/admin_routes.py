from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database.db import get_db
from app.schemas.analytics import CallAnalytics, IntentSummary
from app.services.analytics_service import AnalyticsService
from app.services.call_service import CallService

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

@router.get("/analytics", response_model=CallAnalytics)
async def get_call_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get analytics for calls within a specified date range
    """
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_call_analytics(start_date, end_date)
        return analytics
    except Exception as e:
        logger.error(f"Error retrieving call analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intents", response_model=List[IntentSummary])
async def get_intent_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get summary of detected intents within a specified date range
    """
    try:
        analytics_service = AnalyticsService(db)
        intent_summary = await analytics_service.get_intent_summary(start_date, end_date)
        return intent_summary
    except Exception as e:
        logger.error(f"Error retrieving intent summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-call", tags=["Testing"])
async def simulate_call(
    phone_number: str = Query(..., description="Phone number to simulate call from"),
    message: str = Query(..., description="Message to simulate from caller"),
    language: str = Query("en", description="Language of the message (en/hi)"),
    db: Session = Depends(get_db)
):
    """
    Simulate an inbound call for testing purposes
    """
    try:
        call_service = CallService(db)
        result = await call_service.simulate_inbound_call(
            phone_number=phone_number,
            message=message,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error simulating call: {e}")
        raise HTTPException(status_code=500, detail=str(e))