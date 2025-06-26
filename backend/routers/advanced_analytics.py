#!/usr/bin/env python3
"""
Advanced Analytics API Router
Provides REST endpoints for the Advanced Analytics Engine and Report Generator
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import os
from pathlib import Path
# Import our services
try:
    from services.advanced_analytics import (
        AdvancedAnalyticsEngine, MetricType, TrendDirection, AlertLevel
    )
except ImportError:
    pass

try:
    from services.report_generator import (
        ProfessionalReportGenerator, ReportType, ReportFormat
    )
except ImportError:
    # Fallback imports for standalone testing
    try:
        from services.advanced_analytics import (
            AdvancedAnalyticsEngine, MetricType, TrendDirection, AlertLevel
        )
    except ImportError:
        pass
    
    try:
        from services.report_generator import (
            ProfessionalReportGenerator, ReportType, ReportFormat
        )
    except ImportError:
        pass

logger = logging.getLogger(__name__)

# Initialize services
analytics_engine = AdvancedAnalyticsEngine()
report_generator = ProfessionalReportGenerator(analytics_engine)

# Create router
router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])

# Request/Response Models
class MetricsRequest(BaseModel):
    metric_types: List[str]
    time_range: List[datetime]
    interval: str = "daily"

class TrendRequest(BaseModel):
    metric_type: str
    time_range: List[datetime]
    comparison_type: str = "previous_period"

class ReportRequest(BaseModel):
    report_type: str
    time_range: List[datetime]
    user_id: Optional[str] = None
    formats: List[str] = ["json", "html"]

class AnalyticsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.now()

# Helper function to validate metric types
def validate_metric_types(metric_types: List[str]) -> List[MetricType]:
    """Validate and convert metric type strings to MetricType enums"""
    validated_types = []
    for metric_type in metric_types:
        try:
            validated_types.append(MetricType(metric_type))
        except ValueError:
            logger.warning(f"Invalid metric type: {metric_type}")
    return validated_types

# Helper function to validate time range
def validate_time_range(time_range: List[datetime]) -> tuple:
    """Validate time range and return start/end dates"""
    if len(time_range) != 2:
        raise HTTPException(status_code=400, detail="Time range must contain exactly 2 dates")
    
    start_date, end_date = time_range
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    return start_date, end_date

@router.get("/health")
async def health_check():
    """Health check endpoint for analytics service"""
    try:
        # Test that services are initialized
        test_metrics = await analytics_engine.collect_metrics(
            [MetricType.ACTIVE_USERS], 
            (datetime.now() - timedelta(days=1), datetime.now()),
            "daily"
        )
        
        return AnalyticsResponse(
            success=True,
            data={
                "status": "healthy",
                "analytics_engine": "operational",
                "report_generator": "operational",
                "test_metrics_collected": len(test_metrics)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return AnalyticsResponse(
            success=False,
            error=f"Service unhealthy: {str(e)}"
        )

@router.get("/comprehensive")
async def get_comprehensive_analytics(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    user_id: Optional[str] = Query(None, description="Optional user ID filter")
):
    """Get comprehensive analytics for a time range"""
    try:
        time_range = (start_date, end_date)
        
        analytics_data = await analytics_engine.get_comprehensive_analytics(
            time_range=time_range,
            user_id=user_id
        )
        
        return AnalyticsResponse(
            success=True,
            data=analytics_data
        )
        
    except Exception as e:
        logger.error(f"Error getting comprehensive analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics")
async def get_metrics(request: MetricsRequest):
    """Get specific metrics for given time range"""
    try:
        # Validate inputs
        metric_types = validate_metric_types(request.metric_types)
        start_date, end_date = validate_time_range(request.time_range)
        
        if not metric_types:
            raise HTTPException(status_code=400, detail="No valid metric types provided")
        
        # Collect metrics
        metrics_data = await analytics_engine.collect_metrics(
            metric_types=metric_types,
            time_range=(start_date, end_date),
            interval=request.interval
        )
        
        return AnalyticsResponse(
            success=True,
            data=metrics_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collecting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trends")
async def get_trend_analysis(request: TrendRequest):
    """Get trend analysis for a specific metric"""
    try:
        # Validate inputs
        try:
            metric_type = MetricType(request.metric_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid metric type: {request.metric_type}")
        
        start_date, end_date = validate_time_range(request.time_range)
        
        # Analyze trends
        trend_analysis = await analytics_engine.analyze_trends(
            metric_type=metric_type,
            time_range=(start_date, end_date),
            comparison_type=request.comparison_type
        )
        
        return AnalyticsResponse(
            success=True,
            data={
                "metric_type": request.metric_type,
                "trend_analysis": {
                    "direction": trend_analysis.direction.value,
                    "change_percentage": trend_analysis.change_percentage,
                    "confidence": trend_analysis.confidence,
                    "insights": trend_analysis.insights,
                    "recommendations": trend_analysis.recommendations
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts(
    start_date: datetime = Query(..., description="Start date for alerts"),
    end_date: datetime = Query(..., description="End date for alerts"),
    alert_level: Optional[str] = Query(None, description="Filter by alert level")
):
    """Get system alerts for a time range"""
    try:
        time_range = (start_date, end_date)
        
        # Get sample metrics to check for alerts
        sample_metrics = await analytics_engine.collect_metrics(
            [MetricType.ACTIVE_USERS, MetricType.SENTIMENT_SCORE, MetricType.RESPONSE_TIME],
            time_range,
            "daily"
        )
        
        # Check for alerts
        alerts = await analytics_engine.check_alerts(sample_metrics)
        
        # Filter by alert level if specified
        if alert_level:
            try:
                filter_level = AlertLevel(alert_level)
                alerts = [alert for alert in alerts if alert.alert_level == filter_level]
            except ValueError:
                logger.warning(f"Invalid alert level filter: {alert_level}")
        
        # Convert alerts to serializable format
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "metric_type": alert.metric_type.value,
                "alert_level": alert.alert_level.value,
                "message": alert.message,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "timestamp": alert.timestamp
            })
        
        return AnalyticsResponse(
            success=True,
            data=alerts_data
        )
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_scores(
    start_date: datetime = Query(..., description="Start date for performance analysis"),
    end_date: datetime = Query(..., description="End date for performance analysis"),
    user_id: Optional[str] = Query(None, description="Optional user ID filter")
):
    """Get performance scores and indicators"""
    try:
        time_range = (start_date, end_date)
        
        # Get comprehensive analytics to extract performance scores
        analytics_data = await analytics_engine.get_comprehensive_analytics(
            time_range=time_range,
            user_id=user_id
        )
        
        return AnalyticsResponse(
            success=True,
            data={
                "performance_scores": analytics_data.get("performance_scores", {}),
                "summary": analytics_data.get("summary", {}),
                "confidence": analytics_data.get("confidence", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting performance scores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate a professional report"""
    try:
        # Validate inputs
        try:
            report_type = ReportType(request.report_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {request.report_type}")
        
        # Validate formats
        formats = []
        for fmt in request.formats:
            try:
                formats.append(ReportFormat(fmt))
            except ValueError:
                logger.warning(f"Invalid report format: {fmt}")
        
        if not formats:
            formats = [ReportFormat.JSON]  # Default format
        
        start_date, end_date = validate_time_range(request.time_range)
        
        # Generate report
        report = await report_generator.generate_report(
            report_type=report_type,
            time_range=(start_date, end_date),
            user_id=request.user_id,
            formats=formats
        )
        
        return AnalyticsResponse(
            success=True,
            data={
                "report_id": report.report_id,
                "report_type": request.report_type,
                "metadata": {
                    "title": report.metadata.title,
                    "generated_at": report.metadata.generated_at,
                    "time_range": {
                        "start": start_date,
                        "end": end_date
                    }
                },
                "export_paths": {fmt.value: path for fmt, path in report.export_paths.items()},
                "sections_count": len(report.sections),
                "insights_count": len(report.insights),
                "recommendations_count": len(report.recommendations)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("pdf", description="Export format (json, html, pdf, csv)")
):
    """Download a generated report"""
    try:
        # Validate format
        try:
            export_format = ReportFormat(format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
        
        # Find report file
        reports_dir = Path("reports/professional")
        report_files = list(reports_dir.glob(f"{report_id}*.{format}"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report file not found")
        
        report_file = report_files[0]
        
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Return file
        return FileResponse(
            path=str(report_file),
            filename=f"catalyst_report_{report_id}.{format}",
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights(
    start_date: datetime = Query(..., description="Start date for insights"),
    end_date: datetime = Query(..., description="End date for insights"),
    user_id: Optional[str] = Query(None, description="Optional user ID filter"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)")
):
    """Get AI-generated insights"""
    try:
        time_range = (start_date, end_date)
        
        # Get sample metrics for insights generation
        metrics_data = await analytics_engine.collect_metrics(
            [MetricType.ACTIVE_USERS, MetricType.SENTIMENT_SCORE, MetricType.RELATIONSHIP_SCORE],
            time_range,
            "daily"
        )
        
        # Generate insights
        insights = await analytics_engine.generate_insights(metrics_data)
        
        # Filter by priority if specified
        if priority:
            insights = [insight for insight in insights if insight.priority == priority]
        
        # Convert insights to serializable format
        insights_data = []
        for insight in insights:
            insights_data.append({
                "title": insight.title,
                "description": insight.description,
                "category": insight.category,
                "priority": insight.priority,
                "confidence": insight.confidence,
                "recommendations": insight.recommendations,
                "timestamp": insight.timestamp
            })
        
        return AnalyticsResponse(
            success=True,
            data=insights_data
        )
        
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add router to main application
if __name__ == "__main__":
    # For testing purposes
    import uvicorn
    try:
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except ImportError:
        pass
