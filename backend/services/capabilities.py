#!/usr/bin/env python3
"""
Capabilities module for Advanced Features
Provides information about available features and capabilities
"""

from typing import Dict, Any, List
from services.multi_format_processor import InputFormat, ProcessingMode
from services.therapeutic_interventions import TherapyApproach, InterventionType
try:
    from .advanced_reporting import ReportType, ExportFormat
except ImportError:
    pass

def get_processor_capabilities() -> Dict[str, Any]:
    """Get multi-format processor capabilities"""
    return {
        "supported_formats": [format.value for format in InputFormat],
        "processing_modes": [mode.value for mode in ProcessingMode],
        "max_file_size_mb": 50,
        "supported_file_types": [
            ".txt", ".json", ".csv", ".pdf", ".mp3", ".wav", ".mp4", 
            ".jpg", ".jpeg", ".png", ".docx", ".xlsx"
        ],
        "features": [
            "Real-time processing",
            "Batch processing",
            "Streaming analysis",
            "Multi-language support",
            "Audio transcription",
            "Image text extraction",
            "Format auto-detection",
            "Participant identification",
            "Timestamp parsing",
            "Metadata extraction"
        ],
        "platforms_supported": [
            "WhatsApp", "Facebook Messenger", "Discord", "Slack", 
            "Microsoft Teams", "Telegram", "SMS", "Email", "Generic Text"
        ]
    }

def get_reporting_capabilities() -> Dict[str, Any]:
    """Get advanced reporting capabilities"""
    return {
        "report_types": [report_type.value for report_type in ReportType],
        "export_formats": [format.value for format in ExportFormat],
        "visualization_types": [
            "sentiment_timeline",
            "communication_heatmap",
            "relationship_radar",
            "conflict_indicators",
            "emotional_flow",
            "participant_activity",
            "topic_distribution",
            "response_patterns",
            "engagement_trends",
            "conversation_flow"
        ],
        "metrics_available": [
            "sentiment_analysis",
            "communication_patterns",
            "relationship_health",
            "conflict_detection",
            "emotional_indicators",
            "conversation_flow",
            "response_times",
            "message_frequency",
            "topic_analysis",
            "engagement_levels",
            "turn_taking_patterns",
            "interruption_analysis"
        ],
        "features": [
            "Interactive visualizations",
            "Custom time ranges",
            "Participant filtering",
            "Metric selection",
            "Export to multiple formats",
            "Automated insights",
            "Trend analysis",
            "Comparative reports",
            "Real-time updates",
            "Scheduled reports"
        ]
    }

def get_therapeutic_capabilities() -> Dict[str, Any]:
    """Get therapeutic intervention capabilities"""
    return {
        "therapy_approaches": [approach.value for approach in TherapyApproach],
        "intervention_types": [intervention_type.value for intervention_type in InterventionType],
        "assessment_areas": [
            "Communication patterns",
            "Conflict resolution",
            "Emotional regulation",
            "Relationship dynamics",
            "Attachment styles",
            "Stress management",
            "Intimacy and connection",
            "Trust and security",
            "Goal setting",
            "Behavioral change"
        ],
        "intervention_categories": [
            "Immediate interventions",
            "Short-term strategies",
            "Long-term goals",
            "Preventive measures",
            "Crisis management",
            "Skill building",
            "Awareness exercises",
            "Communication tools",
            "Emotional techniques",
            "Behavioral modifications"
        ],
        "features": [
            "AI-powered recommendations",
            "Personalized interventions",
            "Evidence-based approaches",
            "Progress tracking",
            "Outcome measurement",
            "Technique libraries",
            "Step-by-step guidance",
            "Real-time suggestions",
            "Crisis detection",
            "Professional referrals"
        ],
        "supported_conditions": [
            "Relationship conflicts",
            "Communication issues",
            "Trust problems",
            "Emotional disconnection",
            "Stress and anxiety",
            "Anger management",
            "Intimacy concerns",
            "Life transitions",
            "Parenting challenges",
            "Work-life balance"
        ]
    }

def get_all_capabilities() -> Dict[str, Any]:
    """Get all advanced features capabilities"""
    return {
        "multi_format_processing": get_processor_capabilities(),
        "advanced_reporting": get_reporting_capabilities(),
        "therapeutic_interventions": get_therapeutic_capabilities(),
        "system_info": {
            "version": "1.0.0",
            "last_updated": "2023-12-25",
            "api_version": "v1",
            "supported_languages": ["en", "es", "fr", "de", "it", "pt"],
            "max_concurrent_users": 1000,
            "uptime_sla": "99.9%"
        }
    }