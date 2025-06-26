#!/usr/bin/env python3
"""
Advanced Analytics Engine for Catalyst
Comprehensive metrics collection, trend analysis, and insights generation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter
import uuid
import math
import time

# Database imports
try:
    # Try relative import first (when running as module)
    from catalyst_backend.database.enhanced_models import (
        UserProfile, ConversationHistory, AnalysisCache, 
        TherapeuticSession, ProgressTracking, FileMetadata
    )
except ImportError:
    # Fall back to absolute import (when running as script)
    try:
        from database.enhanced_models import (
            UserProfile, ConversationHistory, AnalysisCache, 
            TherapeuticSession, ProgressTracking, FileMetadata
        )
    except ImportError:
        pass

    except ImportError:
        # For testing without database
        class MockModel:
            pass
        UserProfile = ConversationHistory = AnalysisCache = MockModel
        TherapeuticSession = ProgressTracking = FileMetadata = MockModel

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Types of metrics that can be calculated"""
    # User Engagement Metrics
    ACTIVE_USERS = "active_users"
    USER_RETENTION = "user_retention"
    SESSION_DURATION = "session_duration"
    LOGIN_FREQUENCY = "login_frequency"
    
    # Communication Metrics
    MESSAGE_COUNT = "message_count"
    CONVERSATION_LENGTH = "conversation_length"
    RESPONSE_TIME = "response_time"
    SENTIMENT_SCORE = "sentiment_score"
    
    # Relationship Health Metrics
    RELATIONSHIP_SCORE = "relationship_score"
    CONFLICT_FREQUENCY = "conflict_frequency"
    POSITIVE_INTERACTIONS = "positive_interactions"
    EMOTIONAL_INTIMACY = "emotional_intimacy"
    
    # Therapeutic Progress Metrics
    GOAL_ACHIEVEMENT = "goal_achievement"
    PROGRESS_RATE = "progress_rate"
    ENGAGEMENT_SCORE = "engagement_score"
    INTERVENTION_SUCCESS = "intervention_success"
    
    # Platform Usage Metrics
    FEATURE_USAGE = "feature_usage"
    PLATFORM_DISTRIBUTION = "platform_distribution"
    ERROR_RATE = "error_rate"
    PERFORMANCE_METRICS = "performance_metrics"

class TrendDirection(str, Enum):
    """Direction of trend analysis"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"

class AlertLevel(str, Enum):
    """Alert levels for metrics"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

@dataclass
class MetricValue:
    """Individual metric value with metadata"""
    metric_type: MetricType
    value: Union[float, int]
    timestamp: datetime
    period: str  # "daily", "weekly", "monthly"
    metadata: Dict[str, Any]
    confidence: float = 1.0
    source: str = "system"

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_type: MetricType
    direction: TrendDirection
    change_percentage: float
    significance: float  # Statistical significance
    period_comparison: str
    insights: List[str]
    recommendations: List[str]
    confidence: float

@dataclass
class AlertMetric:
    """Metric alert"""
    metric_type: MetricType
    alert_level: AlertLevel
    current_value: float
    threshold_value: float
    description: str
    action_required: str
    timestamp: datetime

@dataclass
class AnalyticsInsight:
    """Generated analytics insight"""
    id: str
    title: str
    description: str
    category: str
    priority: str  # "high", "medium", "low"
    impact_score: float  # 0-1
    actionable: bool
    related_metrics: List[MetricType]
    generated_at: datetime

class AdvancedAnalyticsEngine:
    """Advanced analytics engine for comprehensive metrics and insights"""
    
    def __init__(self):
        self.metrics_cache: Dict[str, List[MetricValue]] = defaultdict(list)
        self.alerts: List[AlertMetric] = []
        self.insights: List[AnalyticsInsight] = []
        
        # Metric calculation functions
        self.metric_calculators = {
            MetricType.ACTIVE_USERS: self._calculate_active_users,
            MetricType.USER_RETENTION: self._calculate_user_retention,
            MetricType.SESSION_DURATION: self._calculate_session_duration,
            MetricType.MESSAGE_COUNT: self._calculate_message_count,
            MetricType.SENTIMENT_SCORE: self._calculate_sentiment_score,
            MetricType.RELATIONSHIP_SCORE: self._calculate_relationship_score,
            MetricType.GOAL_ACHIEVEMENT: self._calculate_goal_achievement,
            MetricType.FEATURE_USAGE: self._calculate_feature_usage,
            MetricType.RESPONSE_TIME: self._calculate_response_time,
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            MetricType.USER_RETENTION: {"warning": 0.7, "critical": 0.5},
            MetricType.SENTIMENT_SCORE: {"warning": -0.3, "critical": -0.5},
            MetricType.ERROR_RATE: {"warning": 0.05, "critical": 0.1},
            MetricType.RESPONSE_TIME: {"warning": 5.0, "critical": 10.0},
        }
        
        logger.info("Advanced Analytics Engine initialized")
    
    async def collect_metrics(self, 
                            metric_types: List[MetricType],
                            time_range: Tuple[datetime, datetime],
                            granularity: str = "daily") -> Dict[MetricType, List[MetricValue]]:
        """Collect comprehensive metrics for specified time range"""
        
        collected_metrics = {}
        
        for metric_type in metric_types:
            try:
                calculator = self.metric_calculators.get(metric_type)
                if calculator:
                    metrics = await calculator(time_range, granularity)
                    collected_metrics[metric_type] = metrics
                    # Cache metrics
                    self.metrics_cache[metric_type.value].extend(metrics)
                    logger.debug(f"Collected {len(metrics)} values for {metric_type}")
                else:
                    logger.warning(f"No calculator available for metric: {metric_type}")
                    
            except Exception as e:
                logger.error(f"Error collecting metric {metric_type}: {str(e)}")
                collected_metrics[metric_type] = []
        
        return collected_metrics
    
    async def analyze_trends(self, 
                           metric_type: MetricType,
                           time_range: Tuple[datetime, datetime],
                           comparison_period: str = "previous_period") -> TrendAnalysis:
        """Analyze trends for a specific metric"""
        
        try:
            # Get current period metrics
            current_metrics = await self.collect_metrics([metric_type], time_range, "daily")
            current_values = [m.value for m in current_metrics.get(metric_type, [])]
            
            if len(current_values) < 2:
                return TrendAnalysis(
                    metric_type=metric_type,
                    direction=TrendDirection.STABLE,
                    change_percentage=0.0,
                    significance=0.0,
                    period_comparison=comparison_period,
                    insights=["Insufficient data for trend analysis"],
                    recommendations=["Collect more data points"],
                    confidence=0.0
                )
            
            # Calculate comparison period
            period_length = time_range[1] - time_range[0]
            comparison_start = time_range[0] - period_length
            comparison_end = time_range[0]
            
            # Get comparison period metrics
            comparison_metrics = await self.collect_metrics(
                [metric_type], (comparison_start, comparison_end), "daily"
            )
            comparison_values = [m.value for m in comparison_metrics.get(metric_type, [])]
            
            # Calculate trend
            current_avg = statistics.mean([v for v in current_values if isinstance(v, (int, float))]) if current_values else 0
            comparison_avg = statistics.mean([v for v in comparison_values if isinstance(v, (int, float))]) if comparison_values else 0
            
            if comparison_avg == 0:
                change_percentage = 0.0
            else:
                change_percentage = ((current_avg - comparison_avg) / comparison_avg) * 100
            
            # Determine trend direction
            if abs(change_percentage) < 5:
                direction = TrendDirection.STABLE
            elif change_percentage > 0:
                direction = TrendDirection.IMPROVING
            else:
                direction = TrendDirection.DECLINING
            
            # Calculate statistical significance (simplified)
            significance = min(abs(change_percentage) / 100, 1.0)
            
            # Generate insights and recommendations
            insights, recommendations = await self._generate_trend_insights(
                metric_type, direction, change_percentage, current_avg
            )
            
            return TrendAnalysis(
                metric_type=metric_type,
                direction=direction,
                change_percentage=change_percentage,
                significance=significance,
                period_comparison=comparison_period,
                insights=insights,
                recommendations=recommendations,
                confidence=significance
            )
            
        except Exception as e:
            logger.error(f"Error analyzing trends for {metric_type}: {str(e)}")
            raise
    
    async def generate_insights(self, 
                              metrics_data: Dict[MetricType, List[MetricValue]],
                              context: Optional[Dict[str, Any]] = None) -> List[AnalyticsInsight]:
        """Generate actionable insights from metrics data"""
        
        insights = []
        
        try:
            # User engagement insights
            if MetricType.ACTIVE_USERS in metrics_data:
                user_insights = await self._analyze_user_engagement(metrics_data)
                insights.extend(user_insights)
            
            # Communication pattern insights
            if MetricType.MESSAGE_COUNT in metrics_data and MetricType.SENTIMENT_SCORE in metrics_data:
                comm_insights = await self._analyze_communication_patterns(metrics_data)
                insights.extend(comm_insights)
            
            # Relationship health insights
            if MetricType.RELATIONSHIP_SCORE in metrics_data:
                health_insights = await self._analyze_relationship_health(metrics_data)
                insights.extend(health_insights)
            
            # Performance insights
            if MetricType.RESPONSE_TIME in metrics_data:
                perf_insights = await self._analyze_performance_metrics(metrics_data)
                insights.extend(perf_insights)
            
            # Store insights
            self.insights.extend(insights)
            logger.info(f"Generated {len(insights)} analytics insights")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def check_alerts(self, 
                         metrics_data: Dict[MetricType, List[MetricValue]]) -> List[AlertMetric]:
        """Check for alert conditions in metrics"""
        
        alerts = []
        
        for metric_type, values in metrics_data.items():
            if not values:
                continue
                
            try:
                latest_value = values[-1].value
                thresholds = self.alert_thresholds.get(metric_type)
                
                if not thresholds:
                    continue
                
                alert_level = None
                threshold_value = None
                
                if isinstance(latest_value, (int, float)):
                    if latest_value <= thresholds.get("critical", float('-inf')):
                        alert_level = AlertLevel.CRITICAL
                        threshold_value = thresholds["critical"]
                    elif latest_value <= thresholds.get("warning", float('-inf')):
                        alert_level = AlertLevel.WARNING
                        threshold_value = thresholds["warning"]
                
                if alert_level and threshold_value is not None:
                    alert = AlertMetric(
                        metric_type=metric_type,
                        alert_level=alert_level,
                        current_value=float(latest_value),
                        threshold_value=float(threshold_value),
                        description=self._get_alert_description(metric_type, alert_level),
                        action_required=self._get_alert_action(metric_type, alert_level),
                        timestamp=datetime.now(timezone.utc)
                    )
                    alerts.append(alert)
                    
            except Exception as e:
                logger.error(f"Error checking alerts for {metric_type}: {str(e)}")
        
        # Store alerts
        self.alerts.extend(alerts)
        
        return alerts
    
    async def get_comprehensive_analytics(self, 
                                        time_range: Tuple[datetime, datetime],
                                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive analytics report"""
        
        try:
            # Define metrics to collect
            metrics_to_collect = [
                MetricType.ACTIVE_USERS,
                MetricType.USER_RETENTION,
                MetricType.SESSION_DURATION,
                MetricType.MESSAGE_COUNT,
                MetricType.SENTIMENT_SCORE,
                MetricType.RELATIONSHIP_SCORE,
                MetricType.GOAL_ACHIEVEMENT,
                MetricType.FEATURE_USAGE,
                MetricType.RESPONSE_TIME
            ]
            
            # Collect metrics
            metrics_data = await self.collect_metrics(metrics_to_collect, time_range)
            
            # Analyze trends for key metrics
            trend_analyses = {}
            key_metrics = [MetricType.ACTIVE_USERS, MetricType.SENTIMENT_SCORE, 
                          MetricType.RELATIONSHIP_SCORE, MetricType.USER_RETENTION]
            
            for metric_type in key_metrics:
                if metric_type in metrics_data and metrics_data[metric_type]:
                    trend_analyses[metric_type] = await self.analyze_trends(
                        metric_type, time_range
                    )
            
            # Generate insights
            insights = await self.generate_insights(metrics_data)
            
            # Check alerts
            alerts = await self.check_alerts(metrics_data)
            
            # Calculate summary statistics
            summary_stats = await self._calculate_summary_statistics(metrics_data)
            
            # Generate performance scores
            performance_scores = await self._calculate_performance_scores(metrics_data)
            
            return {
                "time_range": {
                    "start": time_range[0].isoformat(),
                    "end": time_range[1].isoformat()
                },
                "user_id": user_id,
                "metrics": {
                    metric_type.value: [asdict(m) for m in values]
                    for metric_type, values in metrics_data.items()
                },
                "trends": {
                    metric_type.value: asdict(trend) 
                    for metric_type, trend in trend_analyses.items()
                },
                "insights": [asdict(insight) for insight in insights],
                "alerts": [asdict(alert) for alert in alerts],
                "summary": summary_stats,
                "performance_scores": performance_scores,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "confidence": self._calculate_overall_confidence(metrics_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics: {str(e)}")
            raise
    
    # Metric calculation methods
    async def _calculate_active_users(self, 
                                    time_range: Tuple[datetime, datetime],
                                    granularity: str) -> List[MetricValue]:
        """Calculate active users metric"""
        # Simulated data - in real implementation, query database
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate active user count with some variance
            base_count = 1000
            variance = int(50 * math.sin(current_date.timestamp() / 86400))
            active_count = base_count + variance
            
            metrics.append(MetricValue(
                metric_type=MetricType.ACTIVE_USERS,
                value=active_count,
                timestamp=current_date,
                period=granularity,
                metadata={"calculation_method": "unique_logins"},
                confidence=0.95
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_user_retention(self, 
                                      time_range: Tuple[datetime, datetime],
                                      granularity: str) -> List[MetricValue]:
        """Calculate user retention metric"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate retention rate between 0.7-0.9
            retention_rate = 0.8 + 0.1 * math.sin(current_date.timestamp() / 86400)
            
            metrics.append(MetricValue(
                metric_type=MetricType.USER_RETENTION,
                value=retention_rate,
                timestamp=current_date,
                period=granularity,
                metadata={"period": "7_day_retention"},
                confidence=0.90
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_session_duration(self, 
                                        time_range: Tuple[datetime, datetime],
                                        granularity: str) -> List[MetricValue]:
        """Calculate average session duration"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate session duration in minutes (15-45 minutes)
            duration = 30 + 15 * math.sin(current_date.timestamp() / 86400)
            
            metrics.append(MetricValue(
                metric_type=MetricType.SESSION_DURATION,
                value=duration,
                timestamp=current_date,
                period=granularity,
                metadata={"unit": "minutes"},
                confidence=0.85
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_message_count(self, 
                                     time_range: Tuple[datetime, datetime],
                                     granularity: str) -> List[MetricValue]:
        """Calculate message count metric"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate message count with weekly patterns
            day_of_week = current_date.weekday()
            base_count = 5000
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0
            message_count = int(base_count * weekend_factor)
            
            metrics.append(MetricValue(
                metric_type=MetricType.MESSAGE_COUNT,
                value=message_count,
                timestamp=current_date,
                period=granularity,
                metadata={"day_of_week": day_of_week},
                confidence=0.95
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_sentiment_score(self, 
                                       time_range: Tuple[datetime, datetime],
                                       granularity: str) -> List[MetricValue]:
        """Calculate average sentiment score"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate sentiment score between -1 and 1
            sentiment = 0.3 + 0.4 * math.sin(current_date.timestamp() / 86400)
            
            metrics.append(MetricValue(
                metric_type=MetricType.SENTIMENT_SCORE,
                value=sentiment,
                timestamp=current_date,
                period=granularity,
                metadata={"scale": "-1_to_1"},
                confidence=0.80
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_relationship_score(self, 
                                          time_range: Tuple[datetime, datetime],
                                          granularity: str) -> List[MetricValue]:
        """Calculate relationship health score"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate relationship score (0-100)
            base_score = 75
            trend = 5 * math.sin(current_date.timestamp() / (86400 * 7))  # Weekly trend
            score = base_score + trend
            
            metrics.append(MetricValue(
                metric_type=MetricType.RELATIONSHIP_SCORE,
                value=max(0, min(100, score)),
                timestamp=current_date,
                period=granularity,
                metadata={"scale": "0_to_100"},
                confidence=0.75
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_goal_achievement(self, 
                                        time_range: Tuple[datetime, datetime],
                                        granularity: str) -> List[MetricValue]:
        """Calculate goal achievement rate"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate goal achievement rate (0-1)
            achievement_rate = 0.6 + 0.2 * math.sin(current_date.timestamp() / (86400 * 30))
            
            metrics.append(MetricValue(
                metric_type=MetricType.GOAL_ACHIEVEMENT,
                value=achievement_rate,
                timestamp=current_date,
                period=granularity,
                metadata={"total_goals": 50, "achieved_goals": int(50 * achievement_rate)},
                confidence=0.90
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_feature_usage(self, 
                                     time_range: Tuple[datetime, datetime],
                                     granularity: str) -> List[MetricValue]:
        """Calculate feature usage statistics"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        features = ["whisper_suggestions", "sentiment_analysis", "goal_tracking", "analytics"]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate feature usage
            usage_data = {}
            for feature in features:
                usage_rate = 0.5 + 0.3 * math.sin(
                    (current_date.timestamp() + hash(feature)) / 86400
                )
                usage_data[feature] = max(0, min(1, usage_rate))
            
            metrics.append(MetricValue(
                metric_type=MetricType.FEATURE_USAGE,
                value=len(json.dumps(usage_data)),  # Use length as numeric value
                timestamp=current_date,
                period=granularity,
                metadata={"features": features},
                confidence=0.85
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    async def _calculate_response_time(self, 
                                     time_range: Tuple[datetime, datetime],
                                     granularity: str) -> List[MetricValue]:
        """Calculate average response time"""
        metrics = []
        start_date = time_range[0]
        end_date = time_range[1]
        
        current_date = start_date
        while current_date <= end_date:
            # Simulate response time in seconds (1-8 seconds)
            response_time = 3 + 2 * math.sin(current_date.timestamp() / 86400)
            
            metrics.append(MetricValue(
                metric_type=MetricType.RESPONSE_TIME,
                value=max(1, response_time),
                timestamp=current_date,
                period=granularity,
                metadata={"unit": "seconds"},
                confidence=0.95
            ))
            
            current_date += timedelta(days=1)
        
        return metrics
    
    # Analysis methods
    async def _generate_trend_insights(self, 
                                     metric_type: MetricType,
                                     direction: TrendDirection,
                                     change_percentage: float,
                                     current_value: float) -> Tuple[List[str], List[str]]:
        """Generate insights and recommendations for trends"""
        
        insights = []
        recommendations = []
        
        if metric_type == MetricType.ACTIVE_USERS:
            if direction == TrendDirection.IMPROVING:
                insights.append(f"Active user count is increasing by {abs(change_percentage):.1f}%")
                recommendations.append("Continue current engagement strategies")
            elif direction == TrendDirection.DECLINING:
                insights.append(f"Active user count is decreasing by {abs(change_percentage):.1f}%")
                recommendations.append("Investigate user retention issues and implement re-engagement campaigns")
        
        elif metric_type == MetricType.SENTIMENT_SCORE:
            if direction == TrendDirection.DECLINING and current_value < 0:
                insights.append("Sentiment is becoming increasingly negative")
                recommendations.append("Review recent conversations for conflict patterns and consider intervention")
        
        elif metric_type == MetricType.RELATIONSHIP_SCORE:
            if direction == TrendDirection.IMPROVING:
                insights.append("Relationship health is improving")
                recommendations.append("Maintain current therapeutic approaches")
            elif direction == TrendDirection.DECLINING:
                insights.append("Relationship health shows concerning decline")
                recommendations.append("Increase intervention frequency and focus on core issues")
        
        return insights, recommendations
    
    async def _analyze_user_engagement(self, 
                                     metrics_data: Dict[MetricType, List[MetricValue]]) -> List[AnalyticsInsight]:
        """Analyze user engagement patterns"""
        insights = []
        
        if MetricType.ACTIVE_USERS in metrics_data and MetricType.SESSION_DURATION in metrics_data:
            active_users = metrics_data[MetricType.ACTIVE_USERS]
            session_durations = metrics_data[MetricType.SESSION_DURATION]
            
            if active_users and session_durations:
                avg_active = statistics.mean([float(m.value) for m in active_users if isinstance(m.value, (int, float))])
                avg_duration = statistics.mean([float(m.value) for m in session_durations if isinstance(m.value, (int, float))])
                
                if avg_duration > 25:  # Above 25 minutes
                    insights.append(AnalyticsInsight(
                        id=str(uuid.uuid4()),
                        title="High User Engagement",
                        description=f"Users spend an average of {avg_duration:.1f} minutes per session, indicating strong engagement",
                        category="user_engagement",
                        priority="medium",
                        impact_score=0.7,
                        actionable=True,
                        related_metrics=[MetricType.SESSION_DURATION, MetricType.ACTIVE_USERS],
                        generated_at=datetime.now(timezone.utc)
                    ))
        
        return insights
    
    async def _analyze_communication_patterns(self, 
                                            metrics_data: Dict[MetricType, List[MetricValue]]) -> List[AnalyticsInsight]:
        """Analyze communication patterns"""
        insights = []
        
        if MetricType.MESSAGE_COUNT in metrics_data and MetricType.SENTIMENT_SCORE in metrics_data:
            messages = metrics_data[MetricType.MESSAGE_COUNT]
            sentiments = metrics_data[MetricType.SENTIMENT_SCORE]
            
            if messages and sentiments:
                avg_sentiment = statistics.mean([float(m.value) for m in sentiments if isinstance(m.value, (int, float))])
                
                if avg_sentiment < -0.2:
                    insights.append(AnalyticsInsight(
                        id=str(uuid.uuid4()),
                        title="Negative Communication Trend",
                        description=f"Average sentiment is {avg_sentiment:.2f}, indicating predominantly negative communication",
                        category="communication",
                        priority="high",
                        impact_score=0.9,
                        actionable=True,
                        related_metrics=[MetricType.SENTIMENT_SCORE, MetricType.MESSAGE_COUNT],
                        generated_at=datetime.now(timezone.utc)
                    ))
        
        return insights
    
    async def _analyze_relationship_health(self, 
                                         metrics_data: Dict[MetricType, List[MetricValue]]) -> List[AnalyticsInsight]:
        """Analyze relationship health metrics"""
        insights = []
        
        if MetricType.RELATIONSHIP_SCORE in metrics_data:
            relationship_scores = metrics_data[MetricType.RELATIONSHIP_SCORE]
            
            if relationship_scores:
                latest_score = relationship_scores[-1].value
                avg_score = statistics.mean([float(m.value) for m in relationship_scores if isinstance(m.value, (int, float))])
                
                if isinstance(latest_score, (int, float)) and latest_score > 80:
                    insights.append(AnalyticsInsight(
                        id=str(uuid.uuid4()),
                        title="Excellent Relationship Health",
                        description=f"Current relationship score is {latest_score:.1f}, indicating strong relationship health",
                        category="relationship_health",
                        priority="low",
                        impact_score=0.8,
                        actionable=False,
                        related_metrics=[MetricType.RELATIONSHIP_SCORE],
                        generated_at=datetime.now(timezone.utc)
                    ))
                elif isinstance(latest_score, (int, float)) and latest_score < 60:
                    insights.append(AnalyticsInsight(
                        id=str(uuid.uuid4()),
                        title="Concerning Relationship Health",
                        description=f"Current relationship score is {latest_score:.1f}, requiring immediate attention",
                        category="relationship_health",
                        priority="high",
                        impact_score=0.95,
                        actionable=True,
                        related_metrics=[MetricType.RELATIONSHIP_SCORE],
                        generated_at=datetime.now(timezone.utc)
                    ))
        
        return insights
    
    async def _analyze_performance_metrics(self, 
                                         metrics_data: Dict[MetricType, List[MetricValue]]) -> List[AnalyticsInsight]:
        """Analyze system performance metrics"""
        insights = []
        
        if MetricType.RESPONSE_TIME in metrics_data:
            response_times = metrics_data[MetricType.RESPONSE_TIME]
            
            if response_times:
                avg_response_time = statistics.mean([float(m.value) for m in response_times if isinstance(m.value, (int, float))])
                
                if avg_response_time > 5:
                    insights.append(AnalyticsInsight(
                        id=str(uuid.uuid4()),
                        title="Slow System Response",
                        description=f"Average response time is {avg_response_time:.1f} seconds, affecting user experience",
                        category="performance",
                        priority="medium",
                        impact_score=0.6,
                        actionable=True,
                        related_metrics=[MetricType.RESPONSE_TIME],
                        generated_at=datetime.now(timezone.utc)
                    ))
        
        return insights
    
    def _get_alert_description(self, metric_type: MetricType, alert_level: AlertLevel) -> str:
        """Get description for alert"""
        descriptions = {
            (MetricType.USER_RETENTION, AlertLevel.WARNING): "User retention is below expected levels",
            (MetricType.USER_RETENTION, AlertLevel.CRITICAL): "User retention is critically low",
            (MetricType.SENTIMENT_SCORE, AlertLevel.WARNING): "Sentiment scores are declining",
            (MetricType.SENTIMENT_SCORE, AlertLevel.CRITICAL): "Sentiment scores are critically negative",
            (MetricType.RESPONSE_TIME, AlertLevel.WARNING): "System response times are elevated",
            (MetricType.RESPONSE_TIME, AlertLevel.CRITICAL): "System response times are critically slow",
        }
        return descriptions.get((metric_type, alert_level), f"{alert_level.value} alert for {metric_type.value}")
    
    def _get_alert_action(self, metric_type: MetricType, alert_level: AlertLevel) -> str:
        """Get recommended action for alert"""
        actions = {
            (MetricType.USER_RETENTION, AlertLevel.WARNING): "Review user engagement strategies",
            (MetricType.USER_RETENTION, AlertLevel.CRITICAL): "Implement immediate retention interventions",
            (MetricType.SENTIMENT_SCORE, AlertLevel.WARNING): "Monitor communication patterns closely",
            (MetricType.SENTIMENT_SCORE, AlertLevel.CRITICAL): "Initiate conflict resolution protocols",
            (MetricType.RESPONSE_TIME, AlertLevel.WARNING): "Optimize system performance",
            (MetricType.RESPONSE_TIME, AlertLevel.CRITICAL): "Investigate and resolve performance bottlenecks",
        }
        return actions.get((metric_type, alert_level), f"Take action for {metric_type.value}")
    
    async def _calculate_summary_statistics(self, 
                                          metrics_data: Dict[MetricType, List[MetricValue]]) -> Dict[str, Any]:
        """Calculate summary statistics for all metrics"""
        summary = {}
        
        for metric_type, values in metrics_data.items():
            if not values:
                continue
                
            numeric_values = [v.value for v in values if isinstance(v.value, (int, float))]
            
            if numeric_values:
                summary[metric_type.value] = {
                    "count": len(numeric_values),
                    "mean": statistics.mean(numeric_values),
                    "median": statistics.median(numeric_values),
                    "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "latest": numeric_values[-1],
                    "trend": "improving" if len(numeric_values) > 1 and numeric_values[-1] > numeric_values[0] else "declining"
                }
        
        return summary
    
    async def _calculate_performance_scores(self, 
                                          metrics_data: Dict[MetricType, List[MetricValue]]) -> Dict[str, float]:
        """Calculate overall performance scores"""
        scores = {}
        
        # User engagement score (0-100)
        if MetricType.ACTIVE_USERS in metrics_data and MetricType.SESSION_DURATION in metrics_data:
            active_users = [m.value for m in metrics_data[MetricType.ACTIVE_USERS]]
            session_durations = [m.value for m in metrics_data[MetricType.SESSION_DURATION]]
            
            if active_users and session_durations:
                numeric_active = [float(v) for v in active_users if isinstance(v, (int, float))]
                numeric_durations = [float(v) for v in session_durations if isinstance(v, (int, float))]
                
                user_score = min(100, (statistics.mean(numeric_active) / 1000) * 50) if numeric_active else 0
                duration_score = min(100, (statistics.mean(numeric_durations) / 60) * 50) if numeric_durations else 0
                scores["user_engagement"] = (user_score + duration_score) / 2
        
        # Communication health score (0-100)
        if MetricType.SENTIMENT_SCORE in metrics_data:
            sentiments = [m.value for m in metrics_data[MetricType.SENTIMENT_SCORE]]
            numeric_sentiments = [float(v) for v in sentiments if isinstance(v, (int, float))]
            if numeric_sentiments:
                # Convert sentiment (-1 to 1) to score (0 to 100)
                avg_sentiment = statistics.mean(numeric_sentiments)
                scores["communication_health"] = max(0, min(100, (avg_sentiment + 1) * 50))
        
        # Relationship health score (direct from metrics)
        if MetricType.RELATIONSHIP_SCORE in metrics_data:
            relationship_scores = [m.value for m in metrics_data[MetricType.RELATIONSHIP_SCORE]]
            numeric_relationship = [float(v) for v in relationship_scores if isinstance(v, (int, float))]
            if numeric_relationship:
                scores["relationship_health"] = statistics.mean(numeric_relationship)
        
        # System performance score (0-100)
        if MetricType.RESPONSE_TIME in metrics_data:
            response_times = [m.value for m in metrics_data[MetricType.RESPONSE_TIME]]
            numeric_response = [float(v) for v in response_times if isinstance(v, (int, float))]
            if numeric_response:
                avg_response = statistics.mean(numeric_response)
                # Better score for faster response times
                scores["system_performance"] = max(0, min(100, 100 - (avg_response * 10)))
        
        return scores
    
    def _calculate_overall_confidence(self, 
                                    metrics_data: Dict[MetricType, List[MetricValue]]) -> float:
        """Calculate overall confidence in analytics results"""
        confidences = []
        
        for values in metrics_data.values():
            if values:
                avg_confidence = statistics.mean([v.confidence for v in values])
                confidences.append(avg_confidence)
        
        return statistics.mean(confidences) if confidences else 0.0

# Export the main class
__all__ = ["AdvancedAnalyticsEngine", "MetricType", "TrendDirection", "AlertLevel"]
