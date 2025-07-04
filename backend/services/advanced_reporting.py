#!/usr/bin/env python3
"""
Advanced Reporting and Visualization Service for Catalyst
Generates comprehensive reports and visualizations from conversation analysis
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta, timezone
import json
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, Counter
import base64
import io

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReportType(str, Enum):
    """Types of reports that can be generated"""
    CONVERSATION_SUMMARY = "conversation_summary"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMMUNICATION_PATTERNS = "communication_patterns"
    RELATIONSHIP_HEALTH = "relationship_health"
    CONFLICT_DETECTION = "conflict_detection"
    EMOTIONAL_TRENDS = "emotional_trends"
    PARTICIPATION_ANALYSIS = "participation_analysis"
    TIME_ANALYSIS = "time_analysis"
    TOPIC_ANALYSIS = "topic_analysis"
    THERAPEUTIC_INSIGHTS = "therapeutic_insights"
    COMPREHENSIVE = "comprehensive"

class VisualizationType(str, Enum):
    """Types of visualizations that can be generated"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    TIMELINE = "timeline"
    NETWORK_GRAPH = "network_graph"
    WORD_CLOUD = "word_cloud"
    CORRELATION_MATRIX = "correlation_matrix"
    TREEMAP = "treemap"

class ExportFormat(str, Enum):
    """Export formats for reports"""
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    EXCEL = "excel"
    PNG = "png"
    SVG = "svg"
    INTERACTIVE_HTML = "interactive_html"

@dataclass
class ReportMetric:
    """Individual metric in a report"""
    name: str
    value: Union[int, float, str]
    description: str
    category: str
    trend: Optional[str] = None  # "up", "down", "stable"
    benchmark: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    confidence: float = 1.0

@dataclass
class VisualizationData:
    """Data for a visualization"""
    type: VisualizationType
    title: str
    data: Dict[str, Any]
    config: Dict[str, Any]
    description: str
    insights: List[str]
    base64_image: Optional[str] = None
    interactive_html: Optional[str] = None

@dataclass
class ReportSection:
    """Section of a report"""
    title: str
    description: str
    metrics: List[ReportMetric]
    visualizations: List[VisualizationData]
    insights: List[str]
    recommendations: List[str]
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class AdvancedReport:
    """Complete advanced report"""
    id: str
    title: str
    report_type: ReportType
    generated_at: datetime
    time_range: Tuple[datetime, datetime]
    participants: List[str]
    summary: str
    sections: List[ReportSection]
    overall_metrics: List[ReportMetric]
    key_insights: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    export_formats: Dict[ExportFormat, str]  # Format -> file path or data

class AdvancedReportingService:
    """Advanced reporting and visualization service"""
    
    def __init__(self):
        self.report_generators = {
            ReportType.CONVERSATION_SUMMARY: self._generate_conversation_summary,
            ReportType.SENTIMENT_ANALYSIS: self._generate_sentiment_analysis,
            ReportType.COMMUNICATION_PATTERNS: self._generate_communication_patterns,
            ReportType.RELATIONSHIP_HEALTH: self._generate_relationship_health,
            ReportType.CONFLICT_DETECTION: self._generate_conflict_detection,
            ReportType.EMOTIONAL_TRENDS: self._generate_emotional_trends,
            ReportType.PARTICIPATION_ANALYSIS: self._generate_participation_analysis,
            ReportType.TIME_ANALYSIS: self._generate_time_analysis,
            ReportType.TOPIC_ANALYSIS: self._generate_topic_analysis,
            ReportType.THERAPEUTIC_INSIGHTS: self._generate_therapeutic_insights,
            ReportType.COMPREHENSIVE: self._generate_comprehensive_report,
        }
        
        self.visualization_generators = {
            VisualizationType.LINE_CHART: self._create_line_chart,
            VisualizationType.BAR_CHART: self._create_bar_chart,
            VisualizationType.PIE_CHART: self._create_pie_chart,
            VisualizationType.HEATMAP: self._create_heatmap,
            VisualizationType.SCATTER_PLOT: self._create_scatter_plot,
            VisualizationType.HISTOGRAM: self._create_histogram,
            VisualizationType.BOX_PLOT: self._create_box_plot,
            VisualizationType.TIMELINE: self._create_timeline,
            VisualizationType.CORRELATION_MATRIX: self._create_correlation_matrix,
        }
    
    async def generate_report(self, 
                            conversation_data: List[Dict[str, Any]],
                            analysis_results: Dict[str, Any],
                            report_type: ReportType,
                            custom_config: Optional[Dict[str, Any]] = None) -> AdvancedReport:
        """Generate an advanced report"""
        
        try:
            # Prepare data
            processed_data = await self._prepare_data(conversation_data, analysis_results)
            
            # Generate report using appropriate generator
            generator = self.report_generators.get(report_type)
            if not generator:
                raise ValueError(f"No generator available for report type: {report_type}")
            
            report = await generator(processed_data, custom_config or {})
            
            # Generate export formats
            export_formats = await self._generate_export_formats(report, custom_config or {})
            report.export_formats = export_formats
            
            logger.info(f"Generated {report_type} report with {len(report.sections)} sections")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _prepare_data(self, conversation_data: List[Dict[str, Any]], 
                          analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and normalize data for report generation"""
        
        # Convert to DataFrame if pandas is available
        df = None
        if PANDAS_AVAILABLE and conversation_data:
            try:
                df = pd.DataFrame(conversation_data)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
            except Exception as e:
                logger.warning(f"Could not create DataFrame: {e}")
        
        # Extract participants
        participants = list(set(msg.get('sender', 'Unknown') for msg in conversation_data))
        
        # Calculate time range
        timestamps = [msg.get('timestamp') for msg in conversation_data if msg.get('timestamp')]
        if timestamps:
            if isinstance(timestamps[0], str):
                timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
            time_range = (min(timestamps), max(timestamps))
        else:
            time_range = (datetime.now(timezone.utc), datetime.now(timezone.utc))
        
        return {
            'messages': conversation_data,
            'dataframe': df,
            'analysis_results': analysis_results,
            'participants': participants,
            'time_range': time_range,
            'message_count': len(conversation_data),
            'date_range_days': (time_range[1] - time_range[0]).days
        }
    
    async def _generate_conversation_summary(self, data: Dict[str, Any], 
                                           config: Dict[str, Any]) -> AdvancedReport:
        """Generate conversation summary report"""
        
        # Overall metrics
        overall_metrics = [
            ReportMetric(
                name="Total Messages",
                value=data['message_count'],
                description="Total number of messages in the conversation",
                category="volume",
                unit="messages"
            ),
            ReportMetric(
                name="Participants",
                value=len(data['participants']),
                description="Number of unique participants",
                category="participants",
                unit="people"
            ),
            ReportMetric(
                name="Duration",
                value=data['date_range_days'],
                description="Conversation duration in days",
                category="time",
                unit="days"
            ),
            ReportMetric(
                name="Messages per Day",
                value=round(data['message_count'] / max(data['date_range_days'], 1), 2),
                description="Average messages per day",
                category="activity",
                unit="messages/day"
            )
        ]
        
        # Participation analysis
        participation_data = self._analyze_participation(data)
        participation_viz = await self._create_bar_chart(
            title="Message Distribution by Participant",
            data=participation_data,
            config={"x_label": "Participant", "y_label": "Message Count"}
        )
        
        # Time analysis
        time_data = self._analyze_time_patterns(data)
        time_viz = await self._create_line_chart(
            title="Message Activity Over Time",
            data=time_data,
            config={"x_label": "Date", "y_label": "Message Count"}
        )
        
        # Create sections
        sections = [
            ReportSection(
                title="Participation Analysis",
                description="Analysis of participant activity and engagement",
                metrics=[
                    ReportMetric(
                        name="Most Active Participant",
                        value=max(participation_data['participants'], key=lambda x: participation_data['message_counts'][participation_data['participants'].index(x)]),
                        description="Participant with the most messages",
                        category="participation"
                    )
                ],
                visualizations=[participation_viz],
                insights=self._generate_participation_insights(participation_data),
                recommendations=[]
            ),
            ReportSection(
                title="Temporal Patterns",
                description="Analysis of conversation timing and patterns",
                metrics=[],
                visualizations=[time_viz],
                insights=self._generate_time_insights(time_data),
                recommendations=[]
            )
        ]
        
        return AdvancedReport(
            id=f"summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            title="Conversation Summary Report",
            report_type=ReportType.CONVERSATION_SUMMARY,
            generated_at=datetime.now(timezone.utc),
            time_range=data['time_range'],
            participants=data['participants'],
            summary=f"Summary of conversation with {len(data['participants'])} participants over {data['date_range_days']} days",
            sections=sections,
            overall_metrics=overall_metrics,
            key_insights=[
                f"Conversation spans {data['date_range_days']} days with {data['message_count']} total messages",
                f"Average of {round(data['message_count'] / max(data['date_range_days'], 1), 1)} messages per day"
            ],
            recommendations=[
                "Consider analyzing sentiment trends for deeper insights",
                "Review participation balance for relationship health assessment"
            ],
            metadata={
                "generation_time": datetime.now(timezone.utc).isoformat(),
                "data_quality": "high" if data['message_count'] > 50 else "medium"
            },
            export_formats={}
        )
    
    async def _generate_sentiment_analysis(self, data: Dict[str, Any], 
                                         config: Dict[str, Any]) -> AdvancedReport:
        """Generate sentiment analysis report"""
        
        analysis_results = data.get('analysis_results', {})
        sentiment_data = analysis_results.get('sentiment_analysis', {})
        
        # Extract sentiment metrics
        overall_sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        sentiment_score = sentiment_data.get('sentiment_score', 0.0)
        sentiment_distribution = sentiment_data.get('sentiment_distribution', {
            'positive': 0.33, 'neutral': 0.34, 'negative': 0.33
        })
        
        # Overall metrics
        overall_metrics = [
            ReportMetric(
                name="Overall Sentiment",
                value=overall_sentiment.title(),
                description="Dominant sentiment in the conversation",
                category="sentiment"
            ),
            ReportMetric(
                name="Sentiment Score",
                value=round(sentiment_score, 3),
                description="Average sentiment score (-1 to 1)",
                category="sentiment",
                unit="score"
            ),
            ReportMetric(
                name="Positive Ratio",
                value=f"{sentiment_distribution.get('positive', 0) * 100:.1f}%",
                description="Percentage of positive messages",
                category="sentiment",
                unit="percentage"
            )
        ]
        
        # Sentiment distribution visualization
        sentiment_viz = await self._create_pie_chart(
            title="Sentiment Distribution",
            data={
                'labels': list(sentiment_distribution.keys()),
                'values': list(sentiment_distribution.values())
            },
            config={"colors": ["#28a745", "#6c757d", "#dc3545"]}
        )
        
        # Sentiment timeline
        sentiment_timeline = self._create_sentiment_timeline(data)
        timeline_viz = await self._create_line_chart(
            title="Sentiment Over Time",
            data=sentiment_timeline,
            config={"x_label": "Time", "y_label": "Sentiment Score"}
        )
        
        sections = [
            ReportSection(
                title="Sentiment Overview",
                description="Overall sentiment analysis of the conversation",
                metrics=overall_metrics,
                visualizations=[sentiment_viz],
                insights=[
                    f"The conversation has an overall {overall_sentiment} sentiment",
                    f"Sentiment score of {sentiment_score:.2f} indicates {'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral'} tone"
                ],
                recommendations=self._generate_sentiment_recommendations(sentiment_data)
            ),
            ReportSection(
                title="Sentiment Trends",
                description="How sentiment changes over time",
                metrics=[],
                visualizations=[timeline_viz],
                insights=self._analyze_sentiment_trends(sentiment_timeline),
                recommendations=[]
            )
        ]
        
        return AdvancedReport(
            id=f"sentiment_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            title="Sentiment Analysis Report",
            report_type=ReportType.SENTIMENT_ANALYSIS,
            generated_at=datetime.now(timezone.utc),
            time_range=data['time_range'],
            participants=data['participants'],
            summary=f"Sentiment analysis showing {overall_sentiment} overall tone with score of {sentiment_score:.2f}",
            sections=sections,
            overall_metrics=overall_metrics,
            key_insights=[
                f"Overall sentiment: {overall_sentiment} (score: {sentiment_score:.2f})",
                f"Positive messages: {sentiment_distribution.get('positive', 0) * 100:.1f}%"
            ],
            recommendations=self._generate_sentiment_recommendations(sentiment_data),
            metadata={
                "sentiment_model": sentiment_data.get('model', 'unknown'),
                "confidence": sentiment_data.get('confidence', 0.8)
            },
            export_formats={}
        )
    
    def _analyze_participation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze participant activity"""
        participation_counts = Counter(msg.get('sender', 'Unknown') for msg in data['messages'])
        
        return {
            'participants': list(participation_counts.keys()),
            'message_counts': list(participation_counts.values()),
            'total_messages': sum(participation_counts.values()),
            'participation_percentages': {
                participant: (count / sum(participation_counts.values())) * 100
                for participant, count in participation_counts.items()
            }
        }
    
    def _analyze_time_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal patterns in conversation"""
        if not PANDAS_AVAILABLE or data['dataframe'] is None:
            return {'dates': [], 'message_counts': []}
        
        df = data['dataframe']
        if 'timestamp' not in df.columns:
            return {'dates': [], 'message_counts': []}
        
        # Group by date
        df['date'] = df['timestamp'].dt.date
        daily_counts = df.groupby('date').size()
        
        return {
            'dates': [str(date) for date in daily_counts.index],
            'message_counts': daily_counts.values.tolist()
        }
    
    def _create_sentiment_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sentiment timeline data"""
        # Simplified sentiment timeline - in real implementation, 
        # this would use actual sentiment scores per message
        if not data['messages']:
            return {'timestamps': [], 'sentiment_scores': []}
        
        # Mock sentiment timeline for demonstration
        import random
        timestamps = []
        sentiment_scores = []
        
        for i, msg in enumerate(data['messages'][:100]):  # Limit for performance
            if msg.get('timestamp'):
                timestamps.append(msg['timestamp'])
                # Mock sentiment score - replace with actual sentiment analysis
                sentiment_scores.append(random.uniform(-1, 1))
        
        return {
            'timestamps': timestamps,
            'sentiment_scores': sentiment_scores
        }
    
    def _generate_participation_insights(self, participation_data: Dict[str, Any]) -> List[str]:
        """Generate insights about participation patterns"""
        insights = []
        
        if not participation_data['participants']:
            return ["No participation data available"]
        
        # Find most and least active participants
        max_messages = max(participation_data['message_counts'])
        min_messages = min(participation_data['message_counts'])
        
        most_active = participation_data['participants'][participation_data['message_counts'].index(max_messages)]
        least_active = participation_data['participants'][participation_data['message_counts'].index(min_messages)]
        
        insights.append(f"{most_active} is the most active participant with {max_messages} messages")
        
        if len(participation_data['participants']) > 1:
            insights.append(f"{least_active} is the least active participant with {min_messages} messages")
            
            # Calculate participation balance
            message_counts = participation_data['message_counts']
            if len(message_counts) > 1:
                std_dev = statistics.stdev(message_counts)
                mean_messages = statistics.mean(message_counts)
                cv = std_dev / mean_messages if mean_messages > 0 else 0
                
                if cv < 0.3:
                    insights.append("Participation is well-balanced among participants")
                elif cv > 0.7:
                    insights.append("Participation is heavily skewed towards certain participants")
                else:
                    insights.append("Participation shows moderate imbalance")
        
        return insights
    
    def _generate_time_insights(self, time_data: Dict[str, Any]) -> List[str]:
        """Generate insights about temporal patterns"""
        insights = []
        
        if not time_data['message_counts']:
            return ["No temporal data available"]
        
        message_counts = time_data['message_counts']
        
        # Find peak activity
        max_messages = max(message_counts)
        max_index = message_counts.index(max_messages)
        peak_date = time_data['dates'][max_index] if max_index < len(time_data['dates']) else "unknown"
        
        insights.append(f"Peak activity occurred on {peak_date} with {max_messages} messages")
        
        # Calculate activity consistency
        if len(message_counts) > 1:
            avg_messages = statistics.mean(message_counts)
            insights.append(f"Average daily activity: {avg_messages:.1f} messages")
            
            # Identify quiet periods
            quiet_days = sum(1 for count in message_counts if count < avg_messages * 0.5)
            if quiet_days > 0:
                insights.append(f"{quiet_days} days had significantly lower activity")
        
        return insights
    
    def _generate_sentiment_recommendations(self, sentiment_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on sentiment analysis"""
        recommendations = []
        
        sentiment_score = sentiment_data.get('sentiment_score', 0.0)
        sentiment_distribution = sentiment_data.get('sentiment_distribution', {})
        
        if sentiment_score < -0.3:
            recommendations.append("Consider addressing negative sentiment patterns through positive communication techniques")
            recommendations.append("Focus on active listening and empathy to improve conversation tone")
        elif sentiment_score > 0.3:
            recommendations.append("Maintain the positive communication patterns observed")
            recommendations.append("Use this positive foundation to address any underlying issues")
        else:
            recommendations.append("Work on increasing positive interactions to improve overall sentiment")
        
        negative_ratio = sentiment_distribution.get('negative', 0)
        if negative_ratio > 0.4:
            recommendations.append("High negative sentiment detected - consider conflict resolution strategies")
        
        return recommendations
    
    def _analyze_sentiment_trends(self, sentiment_timeline: Dict[str, Any]) -> List[str]:
        """Analyze sentiment trends over time"""
        insights = []
        
        sentiment_scores = sentiment_timeline.get('sentiment_scores', [])
        if len(sentiment_scores) < 2:
            return ["Insufficient data for trend analysis"]
        
        # Calculate trend
        first_half = sentiment_scores[:len(sentiment_scores)//2]
        second_half = sentiment_scores[len(sentiment_scores)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg + 0.1:
            insights.append("Sentiment shows an improving trend over time")
        elif second_avg < first_avg - 0.1:
            insights.append("Sentiment shows a declining trend over time")
        else:
            insights.append("Sentiment remains relatively stable over time")
        
        # Identify volatility
        if len(sentiment_scores) > 5:
            std_dev = statistics.stdev(sentiment_scores)
            if std_dev > 0.5:
                insights.append("High sentiment volatility detected - emotions fluctuate significantly")
            elif std_dev < 0.2:
                insights.append("Low sentiment volatility - emotions remain relatively stable")
        
        return insights
    
    # Visualization creation methods
    async def _create_line_chart(self, title: str, data: Dict[str, Any], 
                               config: Dict[str, Any]) -> VisualizationData:
        """Create a line chart visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.LINE_CHART,
            title=title,
            data=data,
            config=config,
            description=f"Line chart showing {title.lower()}",
            insights=[]
        )
        
        # Generate actual chart if libraries are available
        if PLOTLY_AVAILABLE:
            try:
                fig = go.Figure()
                
                x_data = data.get('dates', data.get('timestamps', []))
                y_data = data.get('message_counts', data.get('sentiment_scores', []))
                
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name=title
                ))
                
                fig.update_layout(
                    title=title,
                    xaxis_title=config.get('x_label', 'X'),
                    yaxis_title=config.get('y_label', 'Y'),
                    template='plotly_white'
                )
                
                viz_data.interactive_html = fig.to_html(include_plotlyjs='cdn')
                
            except Exception as e:
                logger.warning(f"Could not generate interactive chart: {e}")
        
        return viz_data
    
    async def _create_bar_chart(self, title: str, data: Dict[str, Any], 
                              config: Dict[str, Any]) -> VisualizationData:
        """Create a bar chart visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.BAR_CHART,
            title=title,
            data=data,
            config=config,
            description=f"Bar chart showing {title.lower()}",
            insights=[]
        )
        
        if PLOTLY_AVAILABLE:
            try:
                fig = go.Figure()
                
                x_data = data.get('participants', data.get('categories', []))
                y_data = data.get('message_counts', data.get('values', []))
                
                fig.add_trace(go.Bar(
                    x=x_data,
                    y=y_data,
                    name=title
                ))
                
                fig.update_layout(
                    title=title,
                    xaxis_title=config.get('x_label', 'Category'),
                    yaxis_title=config.get('y_label', 'Value'),
                    template='plotly_white'
                )
                
                viz_data.interactive_html = fig.to_html(include_plotlyjs='cdn')
                
            except Exception as e:
                logger.warning(f"Could not generate bar chart: {e}")
        
        return viz_data
    
    async def _create_pie_chart(self, title: str, data: Dict[str, Any], 
                              config: Dict[str, Any]) -> VisualizationData:
        """Create a pie chart visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.PIE_CHART,
            title=title,
            data=data,
            config=config,
            description=f"Pie chart showing {title.lower()}",
            insights=[]
        )
        
        if PLOTLY_AVAILABLE:
            try:
                fig = go.Figure()
                
                labels = data.get('labels', [])
                values = data.get('values', [])
                colors = config.get('colors', None)
                
                fig.add_trace(go.Pie(
                    labels=labels,
                    values=values,
                    marker_colors=colors
                ))
                
                fig.update_layout(
                    title=title,
                    template='plotly_white'
                )
                
                viz_data.interactive_html = fig.to_html(include_plotlyjs='cdn')
                
            except Exception as e:
                logger.warning(f"Could not generate pie chart: {e}")
        
        return viz_data
    
    async def _create_heatmap(self, title: str, data: Dict[str, Any], 
                            config: Dict[str, Any]) -> VisualizationData:
        """Create a heatmap visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.HEATMAP,
            title=title,
            data=data,
            config=config,
            description=f"Heatmap showing {title.lower()}",
            insights=[]
        )
        
        # Implementation would depend on specific data structure
        return viz_data
    
    async def _create_scatter_plot(self, title: str, data: Dict[str, Any], 
                                 config: Dict[str, Any]) -> VisualizationData:
        """Create a scatter plot visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.SCATTER_PLOT,
            title=title,
            data=data,
            config=config,
            description=f"Scatter plot showing {title.lower()}",
            insights=[]
        )
        
        return viz_data
    
    async def _create_histogram(self, title: str, data: Dict[str, Any], 
                              config: Dict[str, Any]) -> VisualizationData:
        """Create a histogram visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.HISTOGRAM,
            title=title,
            data=data,
            config=config,
            description=f"Histogram showing {title.lower()}",
            insights=[]
        )
        
        return viz_data
    
    async def _create_box_plot(self, title: str, data: Dict[str, Any], 
                             config: Dict[str, Any]) -> VisualizationData:
        """Create a box plot visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.BOX_PLOT,
            title=title,
            data=data,
            config=config,
            description=f"Box plot showing {title.lower()}",
            insights=[]
        )
        
        return viz_data
    
    async def _create_timeline(self, title: str, data: Dict[str, Any], 
                             config: Dict[str, Any]) -> VisualizationData:
        """Create a timeline visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.TIMELINE,
            title=title,
            data=data,
            config=config,
            description=f"Timeline showing {title.lower()}",
            insights=[]
        )
        
        return viz_data
    
    async def _create_correlation_matrix(self, title: str, data: Dict[str, Any], 
                                       config: Dict[str, Any]) -> VisualizationData:
        """Create a correlation matrix visualization"""
        
        viz_data = VisualizationData(
            type=VisualizationType.CORRELATION_MATRIX,
            title=title,
            data=data,
            config=config,
            description=f"Correlation matrix showing {title.lower()}",
            insights=[]
        )
        
        return viz_data
    
    # Additional report generators (simplified implementations)
    async def _generate_communication_patterns(self, data: Dict[str, Any], 
                                             config: Dict[str, Any]) -> AdvancedReport:
        """Generate communication patterns report"""
        # Simplified implementation
        return await self._generate_conversation_summary(data, config)
    
    async def _generate_relationship_health(self, data: Dict[str, Any], 
                                          config: Dict[str, Any]) -> AdvancedReport:
        """Generate relationship health report"""
        # Simplified implementation
        return await self._generate_sentiment_analysis(data, config)
    
    async def _generate_conflict_detection(self, data: Dict[str, Any], 
                                         config: Dict[str, Any]) -> AdvancedReport:
        """Generate conflict detection report"""
        # Simplified implementation
        return await self._generate_sentiment_analysis(data, config)
    
    async def _generate_emotional_trends(self, data: Dict[str, Any], 
                                       config: Dict[str, Any]) -> AdvancedReport:
        """Generate emotional trends report"""
        # Simplified implementation
        return await self._generate_sentiment_analysis(data, config)
    
    async def _generate_participation_analysis(self, data: Dict[str, Any], 
                                             config: Dict[str, Any]) -> AdvancedReport:
        """Generate participation analysis report"""
        # Simplified implementation
        return await self._generate_conversation_summary(data, config)
    
    async def _generate_time_analysis(self, data: Dict[str, Any], 
                                    config: Dict[str, Any]) -> AdvancedReport:
        """Generate time analysis report"""
        # Simplified implementation
        return await self._generate_conversation_summary(data, config)
    
    async def _generate_topic_analysis(self, data: Dict[str, Any], 
                                     config: Dict[str, Any]) -> AdvancedReport:
        """Generate topic analysis report"""
        # Simplified implementation
        return await self._generate_conversation_summary(data, config)
    
    async def _generate_therapeutic_insights(self, data: Dict[str, Any], 
                                           config: Dict[str, Any]) -> AdvancedReport:
        """Generate therapeutic insights report"""
        # Simplified implementation
        return await self._generate_sentiment_analysis(data, config)
    
    async def _generate_comprehensive_report(self, data: Dict[str, Any], 
                                           config: Dict[str, Any]) -> AdvancedReport:
        """Generate comprehensive report combining multiple analyses"""
        # This would combine multiple report types
        return await self._generate_conversation_summary(data, config)
    
    async def _generate_export_formats(self, report: AdvancedReport, 
                                     config: Dict[str, Any]) -> Dict[ExportFormat, str]:
        """Generate different export formats for the report"""
        export_formats = {}
        
        # JSON export (always available)
        json_data = {
            'report': asdict(report),
            'generated_at': report.generated_at.isoformat(),
            'export_format': 'json'
        }
        export_formats[ExportFormat.JSON] = json.dumps(json_data, indent=2, default=str)
        
        # HTML export
        html_content = self._generate_html_report(report)
        export_formats[ExportFormat.HTML] = html_content
        
        return export_formats
    
    def _generate_html_report(self, report: AdvancedReport) -> str:
        """Generate HTML version of the report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007bff; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }}
        .insight {{ background-color: #d4edda; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .recommendation {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.title}</h1>
        <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Participants:</strong> {', '.join(report.participants)}</p>
        <p><strong>Time Range:</strong> {report.time_range[0].strftime('%Y-%m-%d')} to {report.time_range[1].strftime('%Y-%m-%d')}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <p>{report.summary}</p>
    </div>
    
    <div class="section">
        <h2>Key Metrics</h2>
        {''.join(f'<div class="metric"><strong>{metric.name}:</strong> {metric.value} {metric.unit or ""}</div>' for metric in report.overall_metrics)}
    </div>
    
    <div class="section">
        <h2>Key Insights</h2>
        {''.join(f'<div class="insight">{insight}</div>' for insight in report.key_insights)}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in report.recommendations)}
    </div>
    
    {''.join(f'<div class="section"><h2>{section.title}</h2><p>{section.description}</p></div>' for section in report.sections)}
    
</body>
</html>
        """
        return html
    
    def get_supported_report_types(self) -> List[str]:
        """Get list of supported report types"""
        return [report_type.value for report_type in ReportType]
    
    def get_supported_visualization_types(self) -> List[str]:
        """Get list of supported visualization types"""
        return [viz_type.value for viz_type in VisualizationType]
    
    def get_supported_export_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return [export_format.value for export_format in ExportFormat]


# Utility functions
async def generate_advanced_report(conversation_data: List[Dict[str, Any]],
                                  analysis_results: Dict[str, Any],
                                  report_type: str = "conversation_summary",
                                  config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for generating advanced reports"""
    service = AdvancedReportingService()
    
    try:
        report_type_enum = ReportType(report_type)
    except ValueError:
        report_type_enum = ReportType.CONVERSATION_SUMMARY
    
    report = await service.generate_report(
        conversation_data=conversation_data,
        analysis_results=analysis_results,
        report_type=report_type_enum,
        custom_config=config or {}
    )
    
    return asdict(report)


def get_reporting_capabilities() -> Dict[str, Any]:
    """Get information about reporting capabilities"""
    return {
        "report_types": [report_type.value for report_type in ReportType],
        "visualization_types": [viz_type.value for viz_type in VisualizationType],
        "export_formats": [export_format.value for export_format in ExportFormat],
        "dependencies": {
            "pandas": PANDAS_AVAILABLE,
            "matplotlib": MATPLOTLIB_AVAILABLE,
            "plotly": PLOTLY_AVAILABLE
        },
        "features": {
            "interactive_visualizations": PLOTLY_AVAILABLE,
            "statistical_analysis": PANDAS_AVAILABLE,
            "export_formats": ["json", "html"],
            "real_time_generation": True,
            "custom_configurations": True
        }
    }


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test_reporting():
        service = AdvancedReportingService()
        
        # Sample conversation data
        sample_data = [
            {
                "id": "1",
                "sender": "Alice",
                "content": "Hey, how are you?",
                "timestamp": "2023-12-25T10:30:00Z",
                "platform": "whatsapp"
            },
            {
                "id": "2",
                "sender": "Bob",
                "content": "I'm good, thanks!",
                "timestamp": "2023-12-25T10:31:00Z",
                "platform": "whatsapp"
            }
        ]
        
        # Sample analysis results
        analysis_results = {
            "sentiment_analysis": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.7,
                "sentiment_distribution": {
                    "positive": 0.8,
                    "neutral": 0.2,
                    "negative": 0.0
                }
            }
        }
        
        # Generate report
        report = await service.generate_report(
            conversation_data=sample_data,
            analysis_results=analysis_results,
            report_type=ReportType.CONVERSATION_SUMMARY
        )
        
        print(f"Generated report: {report.title}")
        print(f"Sections: {len(report.sections)}")
        print(f"Metrics: {len(report.overall_metrics)}")
    
    # Run test
    # asyncio.run(test_reporting())