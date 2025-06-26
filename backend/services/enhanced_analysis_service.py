"""Enhanced Analysis Service for Catalyst
Integrates advanced conversation analysis capabilities from Relationship-Therapist
"""

import asyncio
import logging
import os

try:
    from typing import List, Dict, Any, Optional, Union, Tuple
    from datetime import datetime, timedelta, timezone
    import json
    import re
    from dataclasses import dataclass, asdict
    from enum import Enum
    
    # Try to import VADER sentiment analyzer
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        VADER_AVAILABLE = True
    except ImportError:
        # Try alternative import style
        try:
            from vaderSentiment import SentimentIntensityAnalyzer
            VADER_AVAILABLE = True
        except ImportError:
            VADER_AVAILABLE = False
except ImportError:
    VADER_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Import the new AI service
try:
    from .ai_service import EnhancedAIService, AnalysisType, TherapyApproach, InterventionType
except ImportError:
    pass

class EnhancedAnalysisService:
    """Service for enhanced analysis of conversations and messages"""
    
    def __init__(self):
        """Initialize the enhanced analysis service"""
        self.analyzers = {}
        if VADER_AVAILABLE:
            try:
                self.analyzers["sentiment"] = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.error(f"Error initializing VADER sentiment analyzer: {e}")
    
    async def analyze_conversation(self, conversation: List[Dict], 
                                  analysis_type: AnalysisType = None,
                                  user_id: Optional[str] = None,
                                  project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a conversation using the specified analysis type
        
        Args:
            conversation: List of message dictionaries
            analysis_type: Type of analysis to perform
            user_id: Optional user ID for tracking/persistence
            project_id: Optional project ID for tracking/persistence
            
        Returns:
            Dictionary with analysis results
        """
        if not conversation:
            return {"error": "Empty conversation provided"}
        
        try:
            # Basic metrics first
            metrics = self._calculate_basic_metrics(conversation)
            
            # Sentiment analysis if VADER is available
            sentiment_data = {}
            if "sentiment" in self.analyzers:
                sentiment_data = await self._analyze_sentiment(conversation)
            
            # Combine results
            results = {
                "basic_metrics": metrics,
                "sentiment": sentiment_data,
                "analysis_type": str(analysis_type) if analysis_type else "basic",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "project_id": project_id
            }
            
            return results
        except Exception as e:
            logger.error(f"Error in analyze_conversation: {e}")
            return {"error": str(e)}
    
    def _calculate_basic_metrics(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Calculate basic conversation metrics"""
        total_messages = len(conversation)
        if total_messages == 0:
            return {}
        
        # Count by sender
        senders = {}
        message_lengths = []
        total_words = 0
        
        for msg in conversation:
            sender = msg.get("sender", "unknown")
            content = msg.get("content", "")
            
            senders[sender] = senders.get(sender, 0) + 1
            
            # Count words and characters
            words = len(content.split())
            total_words += words
            message_lengths.append(len(content))
        
        # Calculate averages
        avg_length = sum(message_lengths) / total_messages if message_lengths else 0
        avg_words = total_words / total_messages if total_messages > 0 else 0
        
        return {
            "total_messages": total_messages,
            "message_distribution": senders,
            "avg_message_length": avg_length,
            "avg_words_per_message": avg_words,
            "total_participants": len(senders)
        }
    
    async def _analyze_sentiment(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment in conversation"""
        if "sentiment" not in self.analyzers:
            return {"error": "Sentiment analyzer not available"}
        
        analyzer = self.analyzers["sentiment"]
        results = {
            "message_sentiments": [],
            "overall_sentiment": 0,
            "sentiment_trends": []
        }
        
        sentiments = []
        
        try:
            for msg in conversation:
                content = msg.get("content", "")
                if not content:
                    continue
                
                sentiment = analyzer.polarity_scores(content)
                compound = sentiment["compound"]
                sentiments.append(compound)
                
                results["message_sentiments"].append({
                    "message_id": msg.get("id", ""),
                    "sentiment": compound,
                    "positive": sentiment["pos"],
                    "negative": sentiment["neg"],
                    "neutral": sentiment["neu"],
                    "content_preview": content[:50] + "..." if len(content) > 50 else content
                })
            
            # Calculate overall sentiment
            if sentiments:
                results["overall_sentiment"] = sum(sentiments) / len(sentiments)
                
                # Calculate sentiment trend (simple linear)
                if len(sentiments) > 1:
                    start = sentiments[0]
                    end = sentiments[-1]
                    trend = end - start
                    results["sentiment_trends"] = {
                        "direction": "improving" if trend > 0 else "worsening" if trend < 0 else "stable",
                        "magnitude": abs(trend),
                        "raw_trend": trend
                    }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            results["error"] = str(e)
        
        return results
    
    async def save_analysis(self, project_id: str, analysis_type: Any, 
                           content: Dict[str, Any], conversation: List[Dict]) -> str:
        """
        Save analysis results to storage
        
        Args:
            project_id: The project ID
            analysis_type: The type of analysis
            content: The analysis content
            conversation: The conversation that was analyzed
            
        Returns:
            ID of the saved analysis
        """
        try:
            # In a real implementation, this would save to a database
            analysis_id = f"analysis_{project_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            # Log the saved analysis
            logger.info(f"Saved analysis {analysis_id} for project {project_id}")
            
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
    
    async def save_coaching(self, project_id: str, approach: Any, 
                           content: Dict[str, Any], conversation: List[Dict]) -> str:
        """
        Save coaching results to storage
        
        Args:
            project_id: The project ID
            approach: The therapeutic approach used
            content: The coaching content
            conversation: The conversation that was analyzed
            
        Returns:
            ID of the saved coaching
        """
        try:
            # In a real implementation, this would save to a database
            coaching_id = f"coaching_{project_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            # Log the saved coaching
            logger.info(f"Saved coaching {coaching_id} for project {project_id}")
            
            return coaching_id
        except Exception as e:
            logger.error(f"Error saving coaching: {e}")
            raise
