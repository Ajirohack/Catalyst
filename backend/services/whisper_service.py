import asyncio
from textblob import TextBlob
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

class WhisperService:
    """Service for real-time whisper suggestions and coaching"""
    
    def __init__(self):
        # Coaching templates based on different scenarios
        self.coaching_templates = {
            "positive_reinforcement": [
                "Great tone! Keep building on this positive energy.",
                "She's responding well - continue with this approach.",
                "Positive vibes detected - you're on the right track."
            ],
            "conflict_resolution": [
                "She seems upset - try an empathetic approach.",
                "Consider acknowledging her feelings before responding.",
                "Use 'I' statements to avoid sounding accusatory.",
                "Take a moment to understand her perspective."
            ],
            "engagement": [
                "Ask more about her interests to deepen the conversation.",
                "Show genuine curiosity about what she's sharing.",
                "Try asking an open-ended question to encourage more sharing."
            ],
            "emotional_support": [
                "She might need emotional support right now.",
                "Consider offering comfort and understanding.",
                "Validate her feelings before offering solutions."
            ],
            "intimacy_building": [
                "This is a good moment to share something personal.",
                "Consider expressing your feelings more openly.",
                "Share a meaningful memory or experience."
            ],
            "communication_improvement": [
                "Try to be more specific about your feelings.",
                "Consider asking for clarification to avoid misunderstandings.",
                "Active listening would be helpful here."
            ]
        }
        
        # Keywords for different emotional states and contexts
        self.emotion_keywords = {
            "upset": ["angry", "frustrated", "annoyed", "mad", "irritated", "upset"],
            "sad": ["sad", "depressed", "down", "blue", "unhappy", "disappointed"],
            "happy": ["happy", "excited", "joyful", "glad", "cheerful", "thrilled"],
            "stressed": ["stressed", "overwhelmed", "pressure", "busy", "exhausted"],
            "confused": ["confused", "unsure", "don't understand", "unclear", "puzzled"],
            "loving": ["love", "adore", "cherish", "care", "affection", "devoted"]
        }
        
        # Context indicators
        self.context_indicators = {
            "work": ["work", "job", "office", "boss", "colleague", "meeting", "project"],
            "family": ["family", "parents", "siblings", "relatives", "mom", "dad"],
            "friends": ["friends", "buddy", "pal", "hang out", "social"],
            "relationship": ["us", "we", "together", "relationship", "couple", "dating"],
            "future": ["future", "plans", "goals", "dreams", "tomorrow", "next"]
        }
    
    async def whisper_stream(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Analyze incoming message and return suggestion."""
        try:
            # Analyze sentiment
            sentiment_analysis = await self._analyze_message_sentiment(message)
            
            # Detect emotional state
            emotional_state = await self._detect_emotional_state(message)
            
            # Detect context
            conversation_context = await self._detect_context(message)
            
            # Generate appropriate whisper suggestion
            suggestion = await self._generate_whisper_suggestion(
                message, 
                sentiment_analysis, 
                emotional_state, 
                conversation_context,
                context
            )
            
            return f"[Catalyst Whisper] {suggestion}"
            
        except Exception as e:
            return f"[Catalyst Whisper] Unable to analyze message: {str(e)}"
    
    async def _analyze_message_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of the incoming message."""
        try:
            blob = TextBlob(message)
            sentiment = blob.sentiment
            
            return {
                "polarity": sentiment.polarity,  # -1 to 1
                "subjectivity": sentiment.subjectivity,  # 0 to 1
                "classification": self._classify_sentiment(sentiment.polarity)
            }
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity score."""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    
    async def _detect_emotional_state(self, message: str) -> List[str]:
        """Detect emotional states from message content."""
        detected_emotions = []
        message_lower = message.lower()
        
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions
    
    async def _detect_context(self, message: str) -> List[str]:
        """Detect conversation context from message content."""
        detected_contexts = []
        message_lower = message.lower()
        
        for context, keywords in self.context_indicators.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_contexts.append(context)
        
        return detected_contexts
    
    async def _generate_whisper_suggestion(
        self, 
        message: str, 
        sentiment: Dict[str, Any], 
        emotions: List[str], 
        contexts: List[str],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate appropriate whisper suggestion based on analysis."""
        
        # Priority-based suggestion generation
        
        # 1. Handle negative emotions first
        if "upset" in emotions or "angry" in emotions:
            return self._get_random_template("conflict_resolution")
        
        if "sad" in emotions or "disappointed" in emotions:
            return self._get_random_template("emotional_support")
        
        if "confused" in emotions:
            return "Consider asking clarifying questions to better understand her perspective."
        
        if "stressed" in emotions:
            return "She seems stressed - offer support and understanding rather than solutions."
        
        # 2. Handle positive emotions
        if sentiment.get("classification") == "positive" or "happy" in emotions:
            if "loving" in emotions:
                return self._get_random_template("intimacy_building")
            else:
                return self._get_random_template("positive_reinforcement")
        
        # 3. Context-based suggestions
        if "relationship" in contexts:
            return "This seems like an important relationship topic - listen actively and share openly."
        
        if "future" in contexts:
            return "She's talking about the future - show interest in her plans and share your thoughts."
        
        if "work" in contexts:
            return "Work-related stress detected - offer support and ask how you can help."
        
        if "family" in contexts:
            return "Family matters can be sensitive - be supportive and understanding."
        
        # 4. General sentiment-based suggestions
        sentiment_classification = sentiment.get("classification", "neutral")
        
        if sentiment_classification == "negative":
            return self._get_random_template("conflict_resolution")
        elif sentiment_classification == "positive":
            return self._get_random_template("engagement")
        else:
            # Neutral sentiment - encourage engagement
            return self._get_random_template("engagement")
    
    def _get_random_template(self, category: str) -> str:
        """Get a random template from the specified category."""
        import random
        templates = self.coaching_templates.get(category, ["Continue the conversation naturally."])
        return random.choice(templates)
    
    async def analyze_conversation_flow(
        self, 
        messages: List[Dict[str, Any]], 
        participants: List[str]
    ) -> Dict[str, Any]:
        """Analyze the flow of conversation for coaching insights."""
        try:
            if not messages:
                return {"error": "No messages to analyze"}
            
            # Analyze message patterns
            total_messages = len(messages)
            participant_counts = {participant: 0 for participant in participants}
            
            sentiment_trend = []
            response_times = []
            
            for i, message in enumerate(messages):
                sender = message.get("sender", "unknown")
                content = message.get("content", "")
                timestamp = message.get("timestamp")
                
                # Count messages per participant
                if sender in participant_counts:
                    participant_counts[sender] += 1
                
                # Analyze sentiment trend
                sentiment = await self._analyze_message_sentiment(content)
                sentiment_trend.append(sentiment.get("polarity", 0))
                
                # Calculate response times (mock for now)
                if i > 0 and timestamp:
                    # This would calculate actual response time
                    response_times.append(2.5)  # Mock average response time
            
            # Calculate conversation balance
            message_counts = list(participant_counts.values())
            balance_ratio = max(message_counts) / min(message_counts) if min(message_counts) > 0 else float('inf')
            
            # Calculate sentiment trend
            avg_sentiment = sum(sentiment_trend) / len(sentiment_trend) if sentiment_trend else 0
            sentiment_direction = "improving" if len(sentiment_trend) > 1 and sentiment_trend[-1] > sentiment_trend[0] else "stable"
            
            return {
                "conversation_balance": {
                    "participant_counts": participant_counts,
                    "balance_ratio": balance_ratio,
                    "is_balanced": balance_ratio < 2.0
                },
                "sentiment_analysis": {
                    "average_sentiment": avg_sentiment,
                    "sentiment_trend": sentiment_direction,
                    "sentiment_history": sentiment_trend[-10:]  # Last 10 messages
                },
                "engagement_metrics": {
                    "total_messages": total_messages,
                    "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "conversation_length": total_messages
                },
                "coaching_insights": await self._generate_flow_insights(
                    participant_counts, balance_ratio, avg_sentiment, sentiment_direction
                )
            }
            
        except Exception as e:
            return {"error": f"Conversation flow analysis failed: {str(e)}"}
    
    async def _generate_flow_insights(
        self, 
        participant_counts: Dict[str, int], 
        balance_ratio: float, 
        avg_sentiment: float, 
        sentiment_direction: str
    ) -> List[str]:
        """Generate insights based on conversation flow analysis."""
        insights = []
        
        # Balance insights
        if balance_ratio > 3.0:
            insights.append("Conversation is heavily one-sided - encourage more participation from the quieter person.")
        elif balance_ratio > 2.0:
            insights.append("Slight conversation imbalance detected - try to engage both participants equally.")
        else:
            insights.append("Good conversation balance between participants.")
        
        # Sentiment insights
        if avg_sentiment > 0.3:
            insights.append("Overall positive conversation tone - great job maintaining good energy!")
        elif avg_sentiment < -0.3:
            insights.append("Conversation tone is quite negative - consider addressing underlying issues.")
        else:
            insights.append("Neutral conversation tone - look for opportunities to inject positivity.")
        
        # Trend insights
        if sentiment_direction == "improving":
            insights.append("Sentiment is improving throughout the conversation - keep up the good work!")
        
        return insights
    
    async def get_contextual_coaching(
        self, 
        current_message: str, 
        conversation_history: List[Dict[str, Any]], 
        relationship_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get contextual coaching based on current message and conversation history."""
        try:
            # Analyze current message
            current_sentiment = await self._analyze_message_sentiment(current_message)
            current_emotions = await self._detect_emotional_state(current_message)
            current_context = await self._detect_context(current_message)
            
            # Analyze conversation flow
            flow_analysis = await self.analyze_conversation_flow(
                conversation_history, 
                relationship_context.get("participants", ["Person A", "Person B"]) if relationship_context else ["Person A", "Person B"]
            )
            
            # Generate comprehensive coaching
            immediate_suggestion = await self._generate_whisper_suggestion(
                current_message, current_sentiment, current_emotions, current_context, relationship_context
            )
            
            # Generate strategic advice based on conversation flow
            strategic_advice = await self._generate_strategic_advice(flow_analysis, relationship_context)
            
            return {
                "immediate_suggestion": immediate_suggestion,
                "strategic_advice": strategic_advice,
                "current_analysis": {
                    "sentiment": current_sentiment,
                    "emotions": current_emotions,
                    "context": current_context
                },
                "flow_analysis": flow_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Contextual coaching failed: {str(e)}"}
    
    async def _generate_strategic_advice(
        self, 
        flow_analysis: Dict[str, Any], 
        relationship_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate strategic advice based on conversation flow analysis."""
        advice = []
        
        try:
            # Balance-based advice
            balance_info = flow_analysis.get("conversation_balance", {})
            if not balance_info.get("is_balanced", True):
                advice.append("Try to encourage more balanced participation in your conversations.")
            
            # Sentiment-based advice
            sentiment_info = flow_analysis.get("sentiment_analysis", {})
            avg_sentiment = sentiment_info.get("average_sentiment", 0)
            
            if avg_sentiment < -0.2:
                advice.append("Focus on addressing underlying concerns that may be causing negative sentiment.")
            elif avg_sentiment > 0.2:
                advice.append("Great positive energy! Continue building on this foundation.")
            
            # Engagement-based advice
            engagement_info = flow_analysis.get("engagement_metrics", {})
            total_messages = engagement_info.get("total_messages", 0)
            
            if total_messages < 5:
                advice.append("Consider deepening the conversation with more engaging questions.")
            
            # Relationship context advice
            if relationship_context:
                relationship_stage = relationship_context.get("stage", "unknown")
                if relationship_stage == "early":
                    advice.append("Focus on building trust and getting to know each other better.")
                elif relationship_stage == "established":
                    advice.append("Work on maintaining intimacy and addressing any recurring issues.")
            
            if not advice:
                advice.append("Continue maintaining open and honest communication.")
            
            return advice
            
        except Exception as e:
            return [f"Strategic advice generation failed: {str(e)}"]
    
    async def process_message(self, whisper_message) -> Dict[str, Any]:
        """Process a whisper message and return structured response."""
        try:
            # Use the existing whisper_stream method
            suggestion = await self.whisper_stream(whisper_message.content)
            
            # Return structured response matching expected format
            return {
                "suggestions": [suggestion],
                "urgency_level": "medium",
                "category": "general",
                "confidence": 0.8,
                "context": {
                    "sender": whisper_message.sender,
                    "platform": whisper_message.platform,
                    "project_id": whisper_message.project_id
                }
            }
        except Exception as e:
            return {
                "suggestions": [f"Error processing message: {str(e)}"],
                "urgency_level": "low",
                "category": "error",
                "confidence": 0.0,
                "context": {}
            }
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.utcnow().isoformat()