import os
import tempfile
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

try:
    import openai
    import whisper
    import torch
except ImportError as e:
    logging.warning(f"Optional dependency not available: {e}")
    try:
        from ..llm_router.llm_router import LLMRouter
        from catalyst_backend.schemas.ai_provider_schema import (
            AIResponse
        )
        from catalyst_backend.config.ai_providers import AIProviderType
    except ImportError as e:
        logging.warning(f"Import error in whisper_service: {e}")

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

try:
    from typing import Dict, List, Any, Optional
    from datetime import datetime, timezone, timezone
    import json
    import re
    import asyncio
    
    # Import enhanced AI services
    from .llm_router import generate_ai_response, llm_router
    from catalyst_backend.schemas.ai_provider_schema import AIRequest, AIResponse
    from catalyst_backend.config.ai_providers import AIProviderType, ai_config
except ImportError as e:
    logging.error(f"Import error in whisper_service: {e}")

logger = logging.getLogger(__name__)

class WhisperService:
    """Service for real-time whisper suggestions and coaching"""
    
    def __init__(self):
        # Audio transcription configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model_cache: Dict[str, Any] = {}  # Cache for loaded models
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg',
                     '.wma'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
                     '.webm']
        }
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit
        self.chunk_duration = 600  # 10 minutes in seconds for chunking
        
        # Enhanced configuration
        self.quality_settings = {
            'high': {'model': 'large-v2', 'temperature': 0.0},
            'medium': {'model': 'medium', 'temperature': 0.2},
            'fast': {'model': 'base', 'temperature': 0.4}
        }
        
        # Language detection and processing
        self.language_confidence_threshold = 0.8
        self.auto_detect_language = True
        
        # Advanced processing options
        self.enable_speaker_detection = False
        self.enable_emotion_analysis = False
        self.enable_topic_extraction = False
        
        # Output formatting
        self.timestamp_precision = 'word'  # 'word', 'segment', 'none'
        self.include_confidence_scores = True
        
        # Error handling and retry logic
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Performance optimization
        gpu_available = torch.cuda.is_available() if 'torch' in globals() else False
        self.use_gpu = gpu_available
        self.batch_processing = True
        
        # Initialize models based on configuration
        self._initialize_models()
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
        """Analyze incoming message and return enhanced AI-powered suggestion."""
        try:
            # Enhanced AI analysis
            enhanced_suggestion = await self._generate_enhanced_whisper(message, context)
            if enhanced_suggestion and "error" not in enhanced_suggestion:
                return f"[Catalyst Whisper] {enhanced_suggestion}"
            
            logger.warning("Enhanced whisper failed, falling back to basic analysis")
            
        except Exception as e:
            logger.error(f"Enhanced whisper error: {str(e)}")
        
        # Fallback to basic analysis
        fallback_suggestion = await self._generate_fallback_whisper(message, context)
        return f"[Catalyst Whisper] {fallback_suggestion}"
    
    async def _generate_enhanced_whisper(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate enhanced whisper suggestion using AI."""
        try:
            # Build context for AI
            context_info = ""
            if context:
                relationship_stage = context.get("relationship_stage", "unknown")
                conversation_history = context.get("recent_messages", [])
                participants = context.get("participants", [])
                
                context_info = f"""
Context:
- Relationship stage: {relationship_stage}
- Participants: {', '.join(participants) if participants else 'Unknown'}
- Recent conversation flow: {len(conversation_history)} previous messages
"""
            
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert relationship coach providing real-time whisper suggestions. 

Your role:
- Analyze the incoming message for emotional tone, intent, and relationship dynamics
- Provide a single, actionable suggestion for how to respond thoughtfully
- Focus on improving communication, showing empathy, and strengthening the relationship
- Keep suggestions brief (1-2 sentences), specific, and emotionally intelligent

Response guidelines:
- If the message shows upset/frustration: Suggest empathy and understanding
- If positive: Suggest building on the positive energy
- If neutral: Suggest deepening engagement or connection
- Always consider the relationship context and communication patterns"""
                    },
                    {
                        "role": "user",
                        "content": f"{context_info}\n\nIncoming message: \"{message}\"\n\nProvide a whisper suggestion:"
                    }
                ],
                analysis_type="whisper_coaching",
                max_tokens=ai_config.whisper_max_tokens,
                temperature=ai_config.whisper_temperature
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Clean up the response
            suggestion = ai_response.content.strip()
            
            # Remove any quotes or formatting
            suggestion = suggestion.strip('"\'')
            suggestion = suggestion.replace('[Catalyst Whisper]', '').strip()
            
            # Ensure it's a reasonable length for a whisper
            if len(suggestion) > 200:
                suggestion = suggestion[:197] + "..."
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Enhanced whisper generation failed: {str(e)}")
            raise
    
    async def _generate_fallback_whisper(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate fallback whisper using basic analysis."""
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
            
            return suggestion
            
        except Exception as e:
            return f"Unable to analyze message: {str(e)}"
    
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
        """Get enhanced contextual coaching based on current message and conversation history."""
        try:
            # Enhanced AI-powered contextual analysis
            enhanced_coaching = await self._generate_enhanced_contextual_coaching(
                current_message, conversation_history, relationship_context
            )
            
            if enhanced_coaching and "error" not in enhanced_coaching:
                return enhanced_coaching
            
            logger.warning("Enhanced contextual coaching failed, falling back to basic analysis")
            
        except Exception as e:
            logger.error(f"Enhanced contextual coaching error: {str(e)}")
        
        # Fallback to basic analysis
        return await self._generate_basic_contextual_coaching(
            current_message, conversation_history, relationship_context
        )
    
    async def _generate_enhanced_contextual_coaching(
        self,
        current_message: str,
        conversation_history: List[Dict[str, Any]],
        relationship_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate enhanced contextual coaching using AI."""
        try:
            # Prepare conversation context
            history_summary = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages for context
                history_summary = "\n".join([
                    f"{msg.get('sender', 'Unknown')}: {msg.get('content', '')}"
                    for msg in recent_messages
                ])
            
            # Prepare relationship context
            relationship_info = ""
            if relationship_context:
                stage = relationship_context.get("stage", "unknown")
                participants = relationship_context.get("participants", [])
                relationship_info = f"Relationship stage: {stage}, Participants: {', '.join(participants)}"
            
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert relationship coach providing comprehensive contextual guidance.

Analyze the current message in context of:
1. Recent conversation flow and patterns
2. Relationship dynamics and stage
3. Communication effectiveness
4. Emotional undertones and needs

Provide coaching in this JSON format:
{
  "immediate_suggestion": "specific response suggestion",
  "strategic_advice": ["broader relationship advice points"],
  "emotional_analysis": {
    "sender_emotional_state": "detected emotion",
    "relationship_temperature": "warm/neutral/tense",
    "communication_quality": "score 0-1"
  },
  "conversation_insights": ["key observations about communication patterns"],
  "confidence": 0.0-1.0
}"""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this communication situation:

{relationship_info}

Recent conversation:
{history_summary}

Current message: "{current_message}"

Provide comprehensive coaching guidance:"""
                    }
                ],
                analysis_type="contextual_coaching",
                max_tokens=800,
                temperature=0.3
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                coaching_data = json.loads(ai_response.content)
                
                return {
                    "immediate_suggestion": coaching_data.get("immediate_suggestion", ""),
                    "strategic_advice": coaching_data.get("strategic_advice", []),
                    "current_analysis": {
                        "emotional_state": coaching_data.get("emotional_analysis", {}).get("sender_emotional_state", "unknown"),
                        "relationship_temperature": coaching_data.get("emotional_analysis", {}).get("relationship_temperature", "neutral"),
                        "communication_quality": coaching_data.get("emotional_analysis", {}).get("communication_quality", 0.5)
                    },
                    "conversation_insights": coaching_data.get("conversation_insights", []),
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "confidence": coaching_data.get("confidence", ai_response.confidence),
                        "cost": ai_response.cost,
                        "response_time_ms": ai_response.response_time_ms
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            except json.JSONDecodeError:
                # If AI doesn't return valid JSON, extract key parts
                return {
                    "immediate_suggestion": ai_response.content[:200],
                    "strategic_advice": [ai_response.content],
                    "current_analysis": {
                        "emotional_state": "unknown",
                        "relationship_temperature": "neutral", 
                        "communication_quality": 0.5
                    },
                    "conversation_insights": ["AI analysis available in strategic advice"],
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "confidence": ai_response.confidence,
                        "cost": ai_response.cost
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Enhanced contextual coaching failed: {str(e)}")
            raise
    
    async def _generate_basic_contextual_coaching(
        self,
        current_message: str,
        conversation_history: List[Dict[str, Any]],
        relationship_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate basic contextual coaching as fallback."""
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
                "timestamp": datetime.now(timezone.utc).isoformat()
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
        """Process a whisper message and return structured response with enhanced AI."""
        try:
            # Enhanced AI processing
            enhanced_response = await self._process_enhanced_message(whisper_message)
            if enhanced_response and "error" not in enhanced_response:
                return enhanced_response
                
            logger.warning("Enhanced message processing failed, falling back to basic processing")
            
        except Exception as e:
            logger.error(f"Enhanced message processing error: {str(e)}")
        
        # Fallback to basic processing
        return await self._process_basic_message(whisper_message)
    
    async def _process_enhanced_message(self, whisper_message) -> Dict[str, Any]:
        """Process message with enhanced AI analysis."""
        try:
            # Create context for AI
            message_context = {
                "sender": getattr(whisper_message, 'sender', 'unknown'),
                "platform": getattr(whisper_message, 'platform', 'unknown'),
                "project_id": getattr(whisper_message, 'project_id', None),
                "content": getattr(whisper_message, 'content', '')
            }
            
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a real-time relationship coaching assistant. Analyze the message and provide structured guidance.

Respond in JSON format:
{
  "suggestions": ["immediate actionable suggestions"],
  "urgency_level": "low/medium/high",
  "category": "emotional_support/conflict_resolution/engagement/communication_improvement/positive_reinforcement",
  "confidence": 0.0-1.0,
  "emotional_tone": "detected emotion",
  "coaching_priority": "what to focus on first"
}

Guidelines:
- High urgency: conflict, distress, important relationship moments
- Medium urgency: emotional needs, communication improvements
- Low urgency: general engagement, positive reinforcement"""
                    },
                    {
                        "role": "user",
                        "content": f"""Process this message for real-time coaching:

Sender: {message_context['sender']}
Platform: {message_context['platform']}
Message: "{message_context['content']}"

Provide structured coaching response:"""
                    }
                ],
                analysis_type="message_processing",
                max_tokens=400,
                temperature=0.2
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                response_data = json.loads(ai_response.content)
                
                return {
                    "suggestions": response_data.get("suggestions", ["Continue the conversation naturally"]),
                    "urgency_level": response_data.get("urgency_level", "medium"),
                    "category": response_data.get("category", "general"),
                    "confidence": response_data.get("confidence", ai_response.confidence),
                    "context": {
                        "sender": message_context["sender"],
                        "platform": message_context["platform"],
                        "project_id": message_context["project_id"],
                        "emotional_tone": response_data.get("emotional_tone", "neutral"),
                        "coaching_priority": response_data.get("coaching_priority", "general communication")
                    },
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "cost": ai_response.cost,
                        "response_time_ms": ai_response.response_time_ms
                    }
                }
                
            except json.JSONDecodeError:
                # Extract suggestions from non-JSON response
                suggestions = [line.strip() for line in ai_response.content.split('\n') if line.strip()]
                
                return {
                    "suggestions": suggestions[:3] if suggestions else ["Continue the conversation naturally"],
                    "urgency_level": "medium",
                    "category": "general",
                    "confidence": ai_response.confidence,
                    "context": message_context,
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "cost": ai_response.cost
                    }
                }
                
        except Exception as e:
            logger.error(f"Enhanced message processing failed: {str(e)}")
            raise
    
    async def _process_basic_message(self, whisper_message) -> Dict[str, Any]:
        """Process message with basic analysis as fallback."""
        try:
            # Use the existing whisper_stream method
            suggestion = await self.whisper_stream(getattr(whisper_message, 'content', ''))
            
            # Clean up the suggestion
            clean_suggestion = suggestion.replace('[Catalyst Whisper]', '').strip()
            
            # Return structured response matching expected format
            return {
                "suggestions": [clean_suggestion],
                "urgency_level": "medium",
                "category": "general",
                "confidence": 0.6,  # Moderate confidence for basic analysis
                "context": {
                    "sender": getattr(whisper_message, 'sender', 'unknown'),
                    "platform": getattr(whisper_message, 'platform', 'unknown'),
                    "project_id": getattr(whisper_message, 'project_id', None)
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
        return datetime.now(timezone.utc).isoformat()
    
    def _initialize_models(self):
        """Initialize Whisper models for local transcription."""
        try:
            if 'whisper' not in globals():
                logging.warning("Whisper not available, skipping model initialization")
                return
            
            logging.info(
                f"Initializing Whisper models with GPU: {self.use_gpu}"
            )
            
            # Load models based on quality settings
            for quality, settings in self.quality_settings.items():
                model_name = settings['model']
                try:
                    device = "cuda" if self.use_gpu else "cpu"
                    model = whisper.load_model(model_name, device=device)
                    self.model_cache[model_name] = model
                    logging.info(f"Loaded Whisper model: {model_name}")
                except Exception as e:
                    logging.error(f"Failed to load model {model_name}: {e}")
                    
        except Exception as e:
            logging.error(f"Failed to initialize Whisper models: {e}")
            self.model_cache = {}
    
    async def transcribe_audio(
        self, 
        file_path: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transcribe audio file to text with enhanced options."""
        try:
            # Validate file
            if not await self._validate_audio_file(file_path):
                raise ValueError(f"Invalid audio file: {file_path}")
            
            # Get processing options
            quality = (
                options.get('quality', 'medium') if options else 'medium'
            )
            language = options.get('language') if options else None
            
            # Choose transcription method
            if self._should_use_api(file_path):
                result = await self._transcribe_with_api(file_path, language)
            else:
                result = await self._transcribe_with_local_model(
                    file_path, quality, language
                )
            
            # Post-process results
            if self.enable_speaker_detection:
                result = await self._add_speaker_detection(
                    result, file_path
                )
            
            if self.enable_emotion_analysis:
                result = await self._add_emotion_analysis(result)
            
            if self.enable_topic_extraction:
                result = await self._add_topic_extraction(result)
            
            return result
            
        except Exception as e:
            return {"error": f"Transcription failed: {str(e)}"}
    
    async def transcribe_video(
        self, 
        file_path: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transcribe video file by extracting audio first."""
        try:
            # Extract audio from video
            audio_path = await self._extract_audio_from_video(file_path)
            
            try:
                # Transcribe the extracted audio
                result = await self.transcribe_audio(audio_path, options)
                result['source_type'] = 'video'
                result['original_file'] = file_path
                return result
            finally:
                # Clean up temporary audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
        except Exception as e:
            return {"error": f"Video transcription failed: {str(e)}"}
    
    async def batch_transcribe(
        self, 
        file_paths: List[str], 
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Transcribe multiple files in batch."""
        results = []
        
        for file_path in file_paths:
            try:
                if self._is_video_file(file_path):
                    result = await self.transcribe_video(
                        file_path, options
                    )
                else:
                    result = await self.transcribe_audio(
                        file_path, options
                    )
                
                results.append({
                    'file_path': file_path,
                    'success': True,
                    'result': result
                })
                
            except Exception as e:
                logging.error(f"Failed to transcribe {file_path}: {e}")
                results.append({
                    'file_path': file_path,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def _validate_audio_file(self, file_path: str) -> bool:
        """Validate audio file format and accessibility."""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_ext = Path(file_path).suffix.lower()
            all_formats = self.supported_formats['audio'] + self.supported_formats['video']
            
            return file_ext in all_formats
            
        except Exception as e:
            logging.error(f"File validation error: {e}")
            return False
    
    async def _transcribe_with_api(
        self, 
        file_path: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API."""
        try:
            with open(file_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"]
                )
            
            return self._format_result(transcript, 'api')
            
        except Exception as e:
            raise RuntimeError(f"API transcription failed: {str(e)}")
    
    async def _transcribe_with_local_model(
        self, 
        file_path: str, 
        quality: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe using local Whisper model."""
        try:
            model_name = self.quality_settings[quality]['model']
            temperature = self.quality_settings[quality]['temperature']
            
            if model_name not in self.model_cache:
                logging.warning(
                    f"Model {model_name} not loaded, using base model"
                )
                model_name = 'base'
            
            model = self.model_cache.get(model_name)
            if not model:
                raise RuntimeError(
                    "No Whisper model available for transcription"
                )
            
            # Transcribe with the local model
            result = model.transcribe(
                file_path,
                language=language,
                temperature=temperature,
                word_timestamps=True,
                verbose=False
            )
            
            return self._format_result(result, 'local')
            
        except Exception as e:
            raise RuntimeError(f"Local transcription failed: {str(e)}")
    
    async def _extract_audio_from_video(
        self, video_path: str
    ) -> str:
        """Extract audio from video file using ffmpeg."""
        try:
            # Create temporary file for audio
            temp_dir = tempfile.gettempdir()
            base_name = os.path.basename(video_path)
            audio_filename = f"extracted_audio_{base_name}.wav"
            audio_path = os.path.join(temp_dir, audio_filename)
            
            # Use ffmpeg to extract audio (you'll need to install ffmpeg)
            import subprocess
            
            cmd = [
                'ffmpeg', '-i', video_path, '-vn', '-acodec',
                'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path, '-y'
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                raise RuntimeError(
                    f"Failed to extract audio: {process.stderr}"
                )
            
            return audio_path
            
        except Exception as e:
            raise RuntimeError(f"Audio extraction failed: {str(e)}")
    
    async def _add_speaker_detection(
        self, result: Dict[str, Any], file_path: str
    ) -> Dict[str, Any]:
        """Add speaker detection to transcription results."""
        try:
            # Placeholder for speaker detection logic
            # This would integrate with libraries like pyannote.audio
            logging.info("Speaker detection requested but not implemented")
            result['speakers'] = []
            return result
            
        except Exception as e:
            logging.error(f"Speaker detection failed: {e}")
            return result
    
    async def _add_emotion_analysis(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add emotion analysis to transcription results."""
        try:
            # Placeholder for emotion analysis
            logging.info("Emotion analysis requested but not implemented")
            result['emotions'] = []
            return result
            
        except Exception as e:
            logging.error(f"Emotion analysis failed: {e}")
            return result
    
    async def _add_topic_extraction(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add topic extraction to transcription results."""
        try:
            # Placeholder for topic extraction
            logging.info("Topic extraction requested but not implemented")
            result['topics'] = []
            return result
            
        except Exception as e:
            logging.error(f"Topic extraction failed: {e}")
            return result
    
    def _should_use_api(self, file_path: str) -> bool:
        """Determine whether to use API or local model based on file size and availability."""
        try:
            file_size = os.path.getsize(file_path)
            return (
                file_size <= self.max_file_size and 
                self.api_key is not None
            )
        except Exception:
            return False
    
    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video file."""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats['video']
    
    def _format_result(
        self, 
        raw_result: Dict[str, Any], 
        source_type: str = 'audio'
    ) -> Dict[str, Any]:
        """Format transcription result into standardized format."""
        return {
            'text': raw_result.get('text', ''),
            'confidence': raw_result.get('confidence', 0.0),
            'language': raw_result.get('language', 'unknown'),
            'duration': raw_result.get('duration', 0.0),
            'segments': self._format_segments(
                raw_result.get('segments', [])
            ),
            'words': (
                self._format_words(raw_result.get('words', []))
                if self.timestamp_precision == 'word' else []
            ),
            'source_type': source_type,
            'processing_time': raw_result.get('processing_time', 0.0),
            'model_used': raw_result.get('model_used', 'unknown'),
            'quality_metrics': self._calculate_quality_metrics(raw_result)
        }
    
    def _format_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format segment data."""
        formatted_segments = []
        for segment in segments:
            formatted_segments.append({
                'id': segment.get('id', 0),
                'start': segment.get('start', 0.0),
                'end': segment.get('end', 0.0),
                'text': segment.get('text', ''),
                'confidence': segment.get('confidence', 0.0)
            })
        return formatted_segments
    
    def _format_words(self, words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format word-level timestamp data."""
        formatted_words = []
        for word in words:
            formatted_words.append({
                'word': word.get('word', ''),
                'start': word.get('start', 0.0),
                'end': word.get('end', 0.0),
                'confidence': word.get('confidence', 0.0)
            })
        return formatted_words
    
    def _calculate_quality_metrics(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate quality metrics for transcription."""
        try:
            segments = result.get('segments', [])
            if segments:
                confidences = [seg.get('confidence', 0) for seg in segments]
                avg_confidence = sum(confidences) / len(segments)
            else:
                avg_confidence = 0
            
            word_count = len(result.get('words', []))
            duration = result.get('duration', 1)
            
            return {
                'average_confidence': avg_confidence,
                'segment_count': len(segments),
                'word_count': word_count,
                'speech_rate': word_count / duration,
                'silence_ratio': self._calculate_silence_ratio(result)
            }
            
        except Exception as e:
            logging.error(f"Error calculating quality metrics: {e}")
            return {}
    
    def _calculate_silence_ratio(
        self, result: Dict[str, Any]
    ) -> float:
        """Calculate ratio of silence in the audio."""
        try:
            total_duration = result.get('duration', 0)
            segments = result.get('segments', [])
            speech_duration = sum(
                seg.get('end', 0) - seg.get('start', 0) for seg in segments
            )
            if total_duration > 0:
                return max(0, (total_duration - speech_duration) / total_duration)
            return 0
            
        except Exception as e:
            logging.error(f"Error calculating silence ratio: {e}")
            return 0.0