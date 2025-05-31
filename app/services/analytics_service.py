from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, cast, Float
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from app.models.database import Call, CallAction, CallDirection, CallStatus
from app.schemas.analytics import CallMetrics, IntentSummary, CallAnalytics

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_call_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> CallAnalytics:
        """Get call analytics within a specified date range"""
        try:
            # Parse date range
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) if end_date else datetime.now()
            
            # Date range filter
            date_filter = and_(
                Call.created_at >= start_datetime,
                Call.created_at < end_datetime
            )
            
            # Get basic metrics
            total_calls = self.db.query(func.count(Call.id)).filter(date_filter).scalar() or 0
            inbound_calls = self.db.query(func.count(Call.id)).filter(
                date_filter, Call.direction == CallDirection.INBOUND
            ).scalar() or 0
            outbound_calls = self.db.query(func.count(Call.id)).filter(
                date_filter, Call.direction == CallDirection.OUTBOUND
            ).scalar() or 0
            avg_duration = self.db.query(func.avg(Call.duration)).filter(date_filter).scalar() or 0
            completed_calls = self.db.query(func.count(Call.id)).filter(
                date_filter, Call.status == CallStatus.COMPLETED
            ).scalar() or 0
            failed_calls = self.db.query(func.count(Call.id)).filter(
                date_filter, Call.status == CallStatus.FAILED
            ).scalar() or 0
            
            # Get intent summary
            intents_query = self.db.query(
                Call.intent, func.count(Call.id).label("count")
            ).filter(
                date_filter, Call.intent.isnot(None)
            ).group_by(Call.intent).order_by(desc("count")).all()
            
            intent_summary = []
            for intent, count in intents_query:
                if not intent:
                    continue
                percentage = (count / total_calls) * 100 if total_calls > 0 else 0
                intent_summary.append(IntentSummary(
                    intent=intent,
                    count=count,
                    percentage=round(percentage, 2)
                ))
            
            # Get call volume by day
            call_volume_query = self.db.query(
                func.date(Call.created_at).label("date"),
                func.count(Call.id).label("count")
            ).filter(date_filter).group_by("date").order_by("date").all()
            
            call_volume_by_day = {
                str(date): count for date, count in call_volume_query
            }
            
            # Get average duration by intent
            duration_by_intent_query = self.db.query(
                Call.intent,
                func.avg(Call.duration).label("avg_duration")
            ).filter(
                date_filter, Call.intent.isnot(None), Call.duration > 0
            ).group_by(Call.intent).all()
            
            call_duration_by_intent = {
                intent: round(float(avg_duration), 2) for intent, avg_duration in duration_by_intent_query if intent
            }
            
            # Construct the response
            metrics = CallMetrics(
                total_calls=total_calls,
                inbound_calls=inbound_calls,
                outbound_calls=outbound_calls,
                average_duration=round(float(avg_duration), 2),
                completed_calls=completed_calls,
                failed_calls=failed_calls
            )
            
            return CallAnalytics(
                metrics=metrics,
                intents=intent_summary,
                call_volume_by_day=call_volume_by_day,
                call_duration_by_intent=call_duration_by_intent
            )
            
        except Exception as e:
            logger.error(f"Error getting call analytics: {e}")
            # Return empty analytics
            return CallAnalytics(
                metrics=CallMetrics(
                    total_calls=0,
                    inbound_calls=0,
                    outbound_calls=0,
                    average_duration=0,
                    completed_calls=0,
                    failed_calls=0
                ),
                intents=[],
                call_volume_by_day={},
                call_duration_by_intent={}
            )
    
    async def get_intent_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[IntentSummary]:
        """Get summary of detected intents within a specified date range"""
        try:
            # Parse date range
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) if end_date else datetime.now()
            
            # Date range filter
            date_filter = and_(
                Call.created_at >= start_datetime,
                Call.created_at < end_datetime
            )
            
            # Get total calls
            total_calls = self.db.query(func.count(Call.id)).filter(date_filter).scalar() or 0
            
            # Get intent summary
            intents_query = self.db.query(
                Call.intent, func.count(Call.id).label("count")
            ).filter(
                date_filter, Call.intent.isnot(None)
            ).group_by(Call.intent).order_by(desc("count")).all()
            
            intent_summary = []
            for intent, count in intents_query:
                if not intent:
                    continue
                percentage = (count / total_calls) * 100 if total_calls > 0 else 0
                intent_summary.append(IntentSummary(
                    intent=intent,
                    count=count,
                    percentage=round(percentage, 2)
                ))
            
            return intent_summary
            
        except Exception as e:
            logger.error(f"Error getting intent summary: {e}")
            return []