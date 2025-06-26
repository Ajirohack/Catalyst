"""Analysis service module for Catalyst backend."""

try:
    from fastapi import UploadFile
    from PyPDF2 import PdfReader
    from PIL import Image
    import pytesseract
    from textblob import TextBlob
    import io
    import os
    import logging
    from typing import Dict, List, Any, Optional, Union
    from datetime import datetime
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for analyzing various types of content."""
    
    def __init__(self):
        """Initialize the analysis service."""
        # In-memory storage for analysis results
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        self.analysis_counter = 0
    
    async def analyze_upload(self, file: UploadFile) -> dict:
        """Read file, detect type, extract text."""
        content = await file.read()
        filename = file.filename.lower() if file.filename else "unknown"
        text = ""
        
        try:
            # PDF
            if filename.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(content))
                text = "".join(page.extract_text() or "" for page in reader.pages)
            # Image
            elif file.content_type and file.content_type.startswith("image/"):
                img = Image.open(io.BytesIO(content))
                text = pytesseract.image_to_string(img)
            # Plain text
            else:
                text = content.decode(errors="ignore")
            
            preview = text[:200]
            
            # Basic NLP analysis
            analysis = await self.analyze_text_sentiment(text)
            
            return {
                "text_preview": preview,
                "full_text": text,
                "analysis": analysis,
                "file_info": {
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type,
                    "text_length": len(text)
                }
            }
            
        except Exception as e:
            return {
                "text_preview": "",
                "full_text": "",
                "analysis": {},
                "error": f"Failed to process file: {str(e)}",
                "file_info": {
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type
                }
            }
    
    async def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment using enhanced AI models with fallback to TextBlob."""
        if not text or len(text.strip()) == 0:
            return {"error": "No text to analyze"}
        
        try:
            # Try enhanced AI analysis first
            enhanced_result = await self._enhanced_sentiment_analysis(text)
            if enhanced_result and "error" not in enhanced_result:
                return enhanced_result
            
            logger.warning("Enhanced AI analysis failed, falling back to TextBlob")
            
        except Exception as e:
            logger.error(f"Enhanced AI analysis error: {str(e)}")
        
        # Fallback to TextBlob analysis
        return await self._textblob_sentiment_analysis(text)
    
    async def _enhanced_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Enhanced sentiment analysis using LLM Router."""
        try:
            # Create AI request for sentiment analysis
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert relationship and communication analyst. Analyze the provided text for:
1. Sentiment (emotional tone): positive, negative, or neutral with confidence score
2. Communication patterns: direct/indirect, assertive/passive, formal/casual
3. Emotional indicators: specific emotions detected
4. Relationship dynamics: support, conflict, intimacy levels
5. Red flags or positive indicators

Respond in JSON format with detailed analysis and confidence scores."""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this text for sentiment and communication patterns:\n\n{text}"
                    }
                ],
                analysis_type="comprehensive_sentiment",
                max_tokens=ai_config.analysis_max_tokens,
                temperature=ai_config.analysis_temperature
            )
            
            # Get AI response
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                ai_analysis = json.loads(ai_response.content)
            except json.JSONDecodeError:
                # If AI doesn't return valid JSON, extract key information
                ai_analysis = self._extract_analysis_from_text(ai_response.content)
            
            # Calculate basic stats for compatibility
            words = text.split()
            sentences = text.split('.')
            
            # Enhanced analysis with AI insights
            return {
                "sentiment": {
                    "polarity": ai_analysis.get("sentiment_score", 0.0),
                    "subjectivity": ai_analysis.get("subjectivity", 0.5),
                    "classification": ai_analysis.get("sentiment", "neutral"),
                    "confidence": ai_response.confidence,
                    "ai_provider": ai_response.provider,
                    "detailed_emotions": ai_analysis.get("emotions", [])
                },
                "statistics": {
                    "word_count": len(words),
                    "sentence_count": len([s for s in sentences if s.strip()]),
                    "character_count": len(text),
                    "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
                },
                "enhanced_analysis": {
                    "communication_style": ai_analysis.get("communication_style", {}),
                    "emotional_indicators": ai_analysis.get("emotional_indicators", {}),
                    "relationship_dynamics": ai_analysis.get("relationship_dynamics", {}),
                    "red_flags": ai_analysis.get("red_flags", []),
                    "positive_indicators": ai_analysis.get("positive_indicators", [])
                },
                "ai_metadata": {
                    "provider": ai_response.provider,
                    "model": ai_response.model,
                    "cost": ai_response.cost,
                    "response_time_ms": ai_response.response_time_ms,
                    "confidence": ai_response.confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced sentiment analysis failed: {str(e)}")
            return {"error": f"Enhanced analysis failed: {str(e)}"}
    
    def _extract_analysis_from_text(self, ai_content: str) -> Dict[str, Any]:
        """Extract analysis from AI text response when JSON parsing fails."""
        analysis = {}
        
        # Extract sentiment
        if "positive" in ai_content.lower():
            analysis["sentiment"] = "positive"
            analysis["sentiment_score"] = 0.5
        elif "negative" in ai_content.lower():
            analysis["sentiment"] = "negative"
            analysis["sentiment_score"] = -0.5
        else:
            analysis["sentiment"] = "neutral"
            analysis["sentiment_score"] = 0.0
        
        # Extract emotions (basic)
        emotions = []
        emotion_keywords = ["joy", "anger", "sadness", "fear", "surprise", "love", "frustration", "excitement"]
        for emotion in emotion_keywords:
            if emotion in ai_content.lower():
                emotions.append(emotion)
        analysis["emotions"] = emotions
        
        return analysis
    
    async def _textblob_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using TextBlob."""
        try:
            blob = TextBlob(text)
            
            # Sentiment analysis
            sentiment = blob.sentiment
            
            # Word count and basic stats
            words = text.split()
            sentences = text.split('.')
            
            # Emotion indicators (basic keyword matching)
            positive_words = ['love', 'happy', 'great', 'wonderful', 'amazing', 'good', 'excellent', 'fantastic']
            negative_words = ['hate', 'sad', 'terrible', 'awful', 'bad', 'horrible', 'disappointed', 'angry']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            # Question patterns
            question_count = text.count('?')
            
            # Exclamation patterns
            exclamation_count = text.count('!')
            
            return {
                "sentiment": {
                    "polarity": sentiment.polarity,  # -1 to 1
                    "subjectivity": sentiment.subjectivity,  # 0 to 1
                    "classification": self._classify_sentiment(sentiment.polarity),
                    "confidence": 0.6,  # TextBlob has moderate confidence
                    "ai_provider": "textblob_fallback",
                    "detailed_emotions": []
                },
                "statistics": {
                    "word_count": len(words),
                    "sentence_count": len([s for s in sentences if s.strip()]),
                    "character_count": len(text),
                    "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
                },
                "emotional_indicators": {
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                    "question_count": question_count,
                    "exclamation_count": exclamation_count
                },
                "communication_patterns": {
                    "questions_ratio": question_count / len(sentences) if sentences else 0,
                    "exclamation_ratio": exclamation_count / len(sentences) if sentences else 0,
                    "average_sentence_length": len(words) / len(sentences) if sentences else 0
                },
                "ai_metadata": {
                    "provider": "textblob",
                    "model": "textblob_sentiment",
                    "cost": 0.0,
                    "response_time_ms": 0,
                    "confidence": 0.6
                }
            }
            
        except Exception as e:
            return {"error": f"TextBlob analysis failed: {str(e)}"}
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity score."""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    
    async def analyze_conversation(
        self, 
        content: str, 
        participants: List[str], 
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze conversation content for relationship dynamics using enhanced AI."""
        try:
            # Enhanced sentiment analysis with AI
            sentiment_analysis = await self.analyze_text_sentiment(content)
            
            # Enhanced communication patterns analysis
            communication_patterns = await self._enhanced_communication_analysis(content, participants)
            
            # Enhanced relationship dynamics analysis
            relationship_dynamics = await self._enhanced_relationship_analysis(content, participants)
            
            # Generate AI-powered insights
            insights = await self._generate_ai_insights(sentiment_analysis, communication_patterns, relationship_dynamics, content)
            
            # Generate enhanced recommendations
            recommendations = await self._generate_ai_recommendations(
                sentiment_analysis, communication_patterns, relationship_dynamics, content
            )
            
            analysis_result = {
                "sentiment": sentiment_analysis,
                "communication_patterns": communication_patterns,
                "relationship_dynamics": relationship_dynamics,
                "insights": insights,
                "recommendations": recommendations,
                "metadata": {
                    "participants": participants,
                    "project_id": project_id,
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                    "analysis_version": "enhanced_ai_v1.0",
                    **(metadata or {})
                }
            }
            
            # Store analysis result
            analysis_id = str(uuid.uuid4())
            self.analysis_results[analysis_id] = analysis_result
            self.analysis_counter += 1
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Enhanced conversation analysis failed: {str(e)}")
            return {"error": f"Conversation analysis failed: {str(e)}"}
    
    async def _enhanced_communication_analysis(self, content: str, participants: List[str]) -> Dict[str, Any]:
        """Enhanced communication patterns analysis using AI."""
        try:
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a communication expert. Analyze the conversation for:
1. Message distribution and balance between participants
2. Communication styles (direct/indirect, assertive/passive)
3. Response patterns and engagement levels
4. Turn-taking and conversation flow
5. Active listening indicators

Provide specific metrics and observations in JSON format."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze communication patterns in this conversation between {', '.join(participants)}:\n\n{content}"
                    }
                ],
                analysis_type="communication_patterns",
                max_tokens=ai_config.communication_max_tokens,
                temperature=ai_config.communication_temperature
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                ai_analysis = json.loads(ai_response.content)
            except json.JSONDecodeError:
                ai_analysis = {"analysis": ai_response.content}
            
            # Basic pattern analysis for compatibility
            lines = content.split('\n')
            messages = [line.strip() for line in lines if line.strip()]
            
            participant_messages = {participant: 0 for participant in participants}
            for message in messages:
                for participant in participants:
                    if message.lower().startswith(participant.lower()):
                        participant_messages[participant] += 1
                        break
            
            return {
                "ai_analysis": ai_analysis,
                "message_distribution": participant_messages,
                "total_messages": len(messages),
                "enhanced_metrics": {
                    "communication_styles": ai_analysis.get("communication_styles", {}),
                    "engagement_levels": ai_analysis.get("engagement_levels", {}),
                    "turn_taking_quality": ai_analysis.get("turn_taking", "unknown"),
                    "active_listening_score": ai_analysis.get("active_listening_score", 0.5)
                },
                "ai_metadata": {
                    "provider": ai_response.provider,
                    "confidence": ai_response.confidence,
                    "cost": ai_response.cost
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced communication analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._analyze_communication_patterns(content, participants)
    
    async def _enhanced_relationship_analysis(self, content: str, participants: List[str]) -> Dict[str, Any]:
        """Enhanced relationship dynamics analysis using AI."""
        try:
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a relationship dynamics expert. Analyze the conversation for:
1. Emotional connection and intimacy levels
2. Conflict patterns and resolution styles
3. Support and validation patterns
4. Power dynamics and equality
5. Trust and vulnerability indicators
6. Attachment styles visible in communication

Provide detailed analysis with confidence scores in JSON format."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze relationship dynamics in this conversation:\n\n{content}"
                    }
                ],
                analysis_type="relationship_dynamics",
                max_tokens=ai_config.relationship_max_tokens,
                temperature=ai_config.relationship_temperature
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                ai_analysis = json.loads(ai_response.content)
            except json.JSONDecodeError:
                ai_analysis = {"analysis": ai_response.content}
            
            # Enhanced relationship metrics
            return {
                "ai_analysis": ai_analysis,
                "enhanced_dynamics": {
                    "intimacy_level": ai_analysis.get("intimacy_level", 0.5),
                    "conflict_resolution_style": ai_analysis.get("conflict_resolution", "unknown"),
                    "emotional_support_quality": ai_analysis.get("emotional_support", 0.5),
                    "power_balance": ai_analysis.get("power_balance", "balanced"),
                    "trust_indicators": ai_analysis.get("trust_indicators", []),
                    "attachment_patterns": ai_analysis.get("attachment_patterns", {}),
                    "vulnerability_level": ai_analysis.get("vulnerability_level", 0.5)
                },
                "ai_metadata": {
                    "provider": ai_response.provider,
                    "confidence": ai_response.confidence,
                    "cost": ai_response.cost
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced relationship analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._analyze_relationship_dynamics(content, participants)
    
    async def _generate_ai_insights(self, sentiment: Dict, patterns: Dict, dynamics: Dict, content: str) -> List[str]:
        """Generate AI-powered insights from analysis results."""
        try:
            # Compile analysis data for AI
            analysis_summary = {
                "sentiment_classification": sentiment.get("sentiment", {}).get("classification"),
                "sentiment_confidence": sentiment.get("sentiment", {}).get("confidence"),
                "communication_balance": patterns.get("enhanced_metrics", {}).get("turn_taking_quality"),
                "relationship_dynamics": dynamics.get("enhanced_dynamics", {})
            }
            
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a relationship coach. Based on the analysis data provided, generate 3-5 key insights about the relationship dynamics. Be specific, actionable, and empathetic."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate insights based on this analysis:\n{json.dumps(analysis_summary, indent=2)}"
                    }
                ],
                analysis_type="insights_generation",
                max_tokens=ai_config.insights_max_tokens,
                temperature=ai_config.insights_temperature
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Extract insights from AI response
            if ai_response.content:
                # Split by bullet points or numbers
                insights = [insight.strip() for insight in ai_response.content.split('\n') if insight.strip()]
                return [insight.lstrip('•-123456789. ') for insight in insights if len(insight.strip()) > 10]
            
            return ["AI insights generation temporarily unavailable"]
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {str(e)}")
            # Fallback to basic insights
            return await self._generate_insights(sentiment, patterns, dynamics)
    
    async def _generate_ai_recommendations(self, sentiment: Dict, patterns: Dict, dynamics: Dict, content: str) -> List[str]:
        """Generate AI-powered recommendations based on analysis."""
        try:
            # Compile analysis data
            analysis_context = {
                "sentiment": sentiment.get("sentiment", {}),
                "communication_metrics": patterns.get("enhanced_metrics", {}),
                "relationship_dynamics": dynamics.get("enhanced_dynamics", {}),
                "content_preview": content[:500] if len(content) > 500 else content
            }
            
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert relationship coach. Based on the conversation analysis, provide 3-6 specific, actionable recommendations to improve communication and relationship dynamics. Focus on practical steps they can take immediately."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate recommendations based on this analysis:\n{json.dumps(analysis_context, indent=2)}"
                    }
                ],
                analysis_type="recommendations_generation",
                max_tokens=ai_config.recommendations_max_tokens,
                temperature=ai_config.recommendations_temperature
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Extract recommendations from AI response
            if ai_response.content:
                recommendations = [rec.strip() for rec in ai_response.content.split('\n') if rec.strip()]
                return [rec.lstrip('•-123456789. ') for rec in recommendations if len(rec.strip()) > 10]
            
            return ["AI recommendations temporarily unavailable"]
            
        except Exception as e:
            logger.error(f"AI recommendations generation failed: {str(e)}")
            # Fallback to basic recommendations
            return await self.generate_recommendations({
                "sentiment": sentiment,
                "communication_patterns": patterns,
                "relationship_dynamics": dynamics
            }, content)
    
    async def _analyze_communication_patterns(self, content: str, participants: List[str]) -> Dict[str, Any]:
        """Analyze communication patterns in the conversation."""
        try:
            # Split content into messages (basic approach)
            lines = content.split('\n')
            messages = [line.strip() for line in lines if line.strip()]
            
            # Message distribution
            participant_messages = {participant: 0 for participant in participants}
            
            # Simple pattern: look for participant names at start of messages
            for message in messages:
                for participant in participants:
                    if message.lower().startswith(participant.lower()):
                        participant_messages[participant] += 1
                        break
            
            # Response time patterns (mock data for now)
            avg_response_time = "2.5 minutes"  # This would be calculated from timestamps
            
            # Message length patterns
            message_lengths = [len(msg.split()) for msg in messages]
            avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
            
            return {
                "message_distribution": participant_messages,
                "total_messages": len(messages),
                "average_message_length": avg_message_length,
                "average_response_time": avg_response_time,
                "conversation_flow": {
                    "balanced": max(participant_messages.values()) / min(participant_messages.values()) < 2 if participant_messages.values() else True,
                    "engagement_level": "high" if len(messages) > 20 else "medium" if len(messages) > 10 else "low"
                }
            }
            
        except Exception as e:
            return {"error": f"Communication pattern analysis failed: {str(e)}"}
    
    async def _analyze_relationship_dynamics(self, content: str, participants: List[str]) -> Dict[str, Any]:
        """Analyze relationship dynamics from conversation content."""
        try:
            # Emotional tone analysis
            blob = TextBlob(content)
            overall_sentiment = blob.sentiment
            
            # Conflict indicators
            conflict_words = ['disagree', 'wrong', 'no', 'but', 'however', 'argue', 'fight']
            content_lower = content.lower()
            conflict_score = sum(1 for word in conflict_words if word in content_lower)
            
            # Support indicators
            support_words = ['understand', 'agree', 'yes', 'support', 'help', 'care', 'love']
            support_score = sum(1 for word in support_words if word in content_lower)
            
            # Intimacy indicators
            intimacy_words = ['dear', 'honey', 'love', 'miss', 'close', 'together']
            intimacy_score = sum(1 for word in intimacy_words if word in content_lower)
            
            # Power dynamics (basic analysis)
            question_ratio = content.count('?') / len(content.split('.')) if content.split('.') else 0
            
            return {
                "emotional_tone": {
                    "overall_sentiment": overall_sentiment.polarity,
                    "emotional_stability": 1 - abs(overall_sentiment.polarity),  # More stable if closer to neutral
                    "subjectivity": overall_sentiment.subjectivity
                },
                "conflict_level": {
                    "score": conflict_score,
                    "level": "high" if conflict_score > 5 else "medium" if conflict_score > 2 else "low"
                },
                "support_level": {
                    "score": support_score,
                    "level": "high" if support_score > 5 else "medium" if support_score > 2 else "low"
                },
                "intimacy_level": {
                    "score": intimacy_score,
                    "level": "high" if intimacy_score > 3 else "medium" if intimacy_score > 1 else "low"
                },
                "power_dynamics": {
                    "question_ratio": question_ratio,
                    "balance": "balanced" if 0.1 <= question_ratio <= 0.3 else "imbalanced"
                }
            }
            
        except Exception as e:
            return {"error": f"Relationship dynamics analysis failed: {str(e)}"}
    
    async def _generate_insights(self, sentiment: Dict, patterns: Dict, dynamics: Dict) -> List[str]:
        """Generate insights based on analysis results."""
        insights = []
        
        try:
            # Sentiment insights
            if sentiment.get("sentiment", {}).get("classification") == "positive":
                insights.append("Overall conversation tone is positive, indicating good relationship health.")
            elif sentiment.get("sentiment", {}).get("classification") == "negative":
                insights.append("Conversation shows negative sentiment - may need attention to underlying issues.")
            
            # Communication pattern insights
            if patterns.get("conversation_flow", {}).get("balanced"):
                insights.append("Communication appears balanced between participants.")
            else:
                insights.append("Communication imbalance detected - one person may be dominating the conversation.")
            
            # Relationship dynamics insights
            conflict_level = dynamics.get("conflict_level", {}).get("level", "low")
            if conflict_level == "high":
                insights.append("High conflict indicators detected - consider conflict resolution strategies.")
            
            support_level = dynamics.get("support_level", {}).get("level", "low")
            if support_level == "high":
                insights.append("Strong mutual support evident in the conversation.")
            
            intimacy_level = dynamics.get("intimacy_level", {}).get("level", "low")
            if intimacy_level == "high":
                insights.append("High intimacy and emotional connection observed.")
            elif intimacy_level == "low":
                insights.append("Consider ways to increase emotional intimacy and connection.")
            
            return insights
            
        except Exception as e:
            return [f"Insight generation failed: {str(e)}"]
    
    async def generate_recommendations(self, analysis_result: Dict[str, Any], content: str) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        try:
            sentiment = analysis_result.get("sentiment", {})
            patterns = analysis_result.get("communication_patterns", {})
            dynamics = analysis_result.get("relationship_dynamics", {})
            
            # Sentiment-based recommendations
            sentiment_classification = sentiment.get("sentiment", {}).get("classification")
            if sentiment_classification == "negative":
                recommendations.append("Consider addressing underlying concerns with empathy and active listening.")
                recommendations.append("Schedule a calm discussion to understand each other's perspectives.")
            elif sentiment_classification == "positive":
                recommendations.append("Great communication! Continue building on this positive foundation.")
            
            # Communication pattern recommendations
            if not patterns.get("conversation_flow", {}).get("balanced", True):
                recommendations.append("Encourage more balanced participation - ask open-ended questions to draw out the quieter person.")
            
            # Conflict resolution recommendations
            conflict_level = dynamics.get("conflict_level", {}).get("level")
            if conflict_level == "high":
                recommendations.append("Use 'I' statements to express feelings without blame.")
                recommendations.append("Take breaks during heated discussions to cool down and reflect.")
                recommendations.append("Focus on finding common ground and shared goals.")
            
            # Support building recommendations
            support_level = dynamics.get("support_level", {}).get("level")
            if support_level == "low":
                recommendations.append("Practice active listening and validate each other's feelings.")
                recommendations.append("Express appreciation and gratitude more frequently.")
            
            # Intimacy building recommendations
            intimacy_level = dynamics.get("intimacy_level", {}).get("level")
            if intimacy_level == "low":
                recommendations.append("Share more personal thoughts and feelings to deepen connection.")
                recommendations.append("Create regular opportunities for meaningful one-on-one time.")
            
            # General recommendations
            if len(recommendations) == 0:
                recommendations.append("Continue maintaining open and honest communication.")
                recommendations.append("Regular check-ins can help maintain relationship health.")
            
            return recommendations
            
        except Exception as e:
            return [f"Recommendation generation failed: {str(e)}"]
    
    async def quick_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Quick sentiment analysis for real-time processing using enhanced AI."""
        try:
            # For quick analysis, use a simplified AI request
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze sentiment: positive, negative, or neutral. Respond with JSON: {\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0, \"emotion\": \"primary emotion\"}"
                    },
                    {
                        "role": "user",
                        "content": text[:500]  # Limit for quick analysis
                    }
                ],
                analysis_type="quick_sentiment",
                max_tokens=100,
                temperature=0.1
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            # Parse AI response
            try:
                ai_result = json.loads(ai_response.content)
                polarity = 0.5 if ai_result.get("sentiment") == "positive" else -0.5 if ai_result.get("sentiment") == "negative" else 0.0
                
                return {
                    "sentiment": {
                        "polarity": polarity,
                        "subjectivity": 0.5,  # Default for quick analysis
                        "classification": ai_result.get("sentiment", "neutral"),
                        "confidence": ai_result.get("confidence", ai_response.confidence),
                        "primary_emotion": ai_result.get("emotion", "unknown")
                    },
                    "quick_stats": {
                        "word_count": len(text.split()),
                        "character_count": len(text)
                    },
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "response_time_ms": ai_response.response_time_ms,
                        "cost": ai_response.cost
                    }
                }
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                return await self._quick_textblob_analysis(text)
            
        except Exception as e:
            logger.warning(f"Quick AI analysis failed: {str(e)}", exc_info=True)
            return await self._quick_textblob_analysis(text)
    
    async def _quick_textblob_analysis(self, text: str) -> Dict[str, Any]:
        """Quick TextBlob analysis as fallback."""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                "sentiment": {
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity,
                    "classification": self._classify_sentiment(sentiment.polarity),
                    "confidence": 0.6,
                    "primary_emotion": "unknown"
                },
                "quick_stats": {
                    "word_count": len(text.split()),
                    "character_count": len(text)
                },
                "ai_metadata": {
                    "provider": "textblob_fallback",
                    "response_time_ms": 0,
                    "cost": 0.0
                }
            }
        except Exception as e:
            return {"error": f"Quick analysis failed: {str(e)}"}
    
    async def analyze_relationship_dynamics(self, text: str) -> Dict[str, Any]:
        """Detailed relationship dynamics analysis using enhanced AI."""
        try:
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze relationship dynamics in the text. Focus on:
1. Emotional connection and intimacy
2. Communication effectiveness
3. Conflict or harmony indicators
4. Support and validation patterns
5. Power dynamics

Respond in JSON format with scores and observations."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze relationship dynamics:\n{text}"
                    }
                ],
                analysis_type="relationship_dynamics_detailed",
                max_tokens=600,
                temperature=0.2
            )
            
            ai_response = await generate_ai_response(ai_request)
            
            try:
                ai_analysis = json.loads(ai_response.content)
                return {
                    "enhanced_analysis": ai_analysis,
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "confidence": ai_response.confidence,
                        "cost": ai_response.cost
                    }
                }
            except json.JSONDecodeError:
                return {
                    "analysis": ai_response.content,
                    "ai_metadata": {
                        "provider": ai_response.provider,
                        "confidence": ai_response.confidence,
                        "cost": ai_response.cost
                    }
                }
                
        except Exception as e:
            logger.error(f"Enhanced relationship dynamics analysis failed: {str(e)}", exc_info=True)
            # Fallback to basic analysis
            return await self._analyze_relationship_dynamics(text, ["Person A", "Person B"])
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get stored analysis result by ID."""
        return self.analysis_results.get(analysis_id)
    
    def get_all_analysis_results(self) -> List[Dict[str, Any]]:
        """Get all stored analysis results."""
        return list(self.analysis_results.values())
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now(timezone.utc).isoformat()