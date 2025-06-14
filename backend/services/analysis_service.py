import io
from fastapi import UploadFile
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from textblob import TextBlob
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
import re
import json

class AnalysisService:
    def __init__(self):
        # In-memory storage for analysis results
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        self.analysis_counter = 0
    
    async def analyze_upload(self, file: UploadFile) -> dict:
        """Read file, detect type, extract text."""
        content = await file.read()
        filename = file.filename.lower()
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
        """Analyze text sentiment and basic patterns."""
        if not text or len(text.strip()) == 0:
            return {"error": "No text to analyze"}
        
        try:
            blob = TextBlob(text)
            
            # Sentiment analysis
            sentiment = blob.sentiment
            
            # Word count and basic stats
            words = text.split()
            sentences = text.split('.')
            
            # Emotion indicators
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
                    "classification": self._classify_sentiment(sentiment.polarity)
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
                }
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
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
        """Analyze conversation content for relationship dynamics."""
        try:
            # Basic sentiment analysis
            sentiment_analysis = await self.analyze_text_sentiment(content)
            
            # Communication patterns analysis
            communication_patterns = await self._analyze_communication_patterns(content, participants)
            
            # Relationship dynamics
            relationship_dynamics = await self._analyze_relationship_dynamics(content, participants)
            
            # Generate insights
            insights = await self._generate_insights(sentiment_analysis, communication_patterns, relationship_dynamics)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations({
                "sentiment": sentiment_analysis,
                "communication_patterns": communication_patterns,
                "relationship_dynamics": relationship_dynamics
            }, content)
            
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
                    **(metadata or {})
                }
            }
            
            # Store analysis result
            analysis_id = str(uuid.uuid4())
            self.analysis_results[analysis_id] = analysis_result
            self.analysis_counter += 1
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Conversation analysis failed: {str(e)}"}
    
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
        """Quick sentiment analysis for real-time processing."""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                "sentiment": {
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity,
                    "classification": self._classify_sentiment(sentiment.polarity)
                },
                "quick_stats": {
                    "word_count": len(text.split()),
                    "character_count": len(text)
                }
            }
            
        except Exception as e:
            return {"error": f"Quick analysis failed: {str(e)}"}
    
    async def analyze_relationship_dynamics(self, text: str) -> Dict[str, Any]:
        """Detailed relationship dynamics analysis."""
        try:
            # This would be a more sophisticated analysis
            # For now, using the existing method
            return await self._analyze_relationship_dynamics(text, ["Person A", "Person B"])
            
        except Exception as e:
            return {"error": f"Relationship dynamics analysis failed: {str(e)}"}
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get stored analysis result by ID."""
        return self.analysis_results.get(analysis_id)
    
    def get_all_analysis_results(self) -> List[Dict[str, Any]]:
        """Get all stored analysis results."""
        return list(self.analysis_results.values())
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now(timezone.utc).isoformat()