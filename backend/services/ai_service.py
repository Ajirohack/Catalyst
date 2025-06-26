"""Enhanced AI Service for Catalyst
Combines advanced AI capabilities from Relationship-Therapist with Catalyst's architecture
"""

import asyncio
import logging
import os
try:
    from typing import Dict, List, Optional, Any, Union
    from dataclasses import dataclass
    from enum import Enum
    import json
    from datetime import datetime, timezone
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    """Types of analysis available"""
    SENTIMENT = "sentiment"
    COMMUNICATION_STYLE = "communication_style"
    RELATIONSHIP_HEALTH = "relationship_health"
    CONFLICT_DETECTION = "conflict_detection"
    RECOMMENDATION = "recommendation"
    PATTERN_ANALYSIS = "pattern_analysis"
    COMPREHENSIVE = "comprehensive"
    EMOTIONAL = "emotional"
    COMPATIBILITY = "compatibility"
    RELATIONSHIP_STAGE = "relationship_stage"

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class TherapyApproach(str, Enum):
    """Therapeutic approaches for relationship guidance"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    EMOTIONALLY_FOCUSED = "emotionally_focused"
    GOTTMAN_METHOD = "gottman_method"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE_THERAPY = "narrative_therapy"
    SYSTEMIC_THERAPY = "systemic_therapy"

class InterventionType(str, Enum):
    """Types of therapeutic interventions"""
    IMMEDIATE_RESPONSE = "immediate_response"
    COMMUNICATION_COACHING = "communication_coaching"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMOTIONAL_REGULATION = "emotional_regulation"
    RELATIONSHIP_BUILDING = "relationship_building"
    BOUNDARY_SETTING = "boundary_setting"

@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    confidence: float
    metadata: Dict[str, Any]
    provider: str
    model: str
    timestamp: datetime
    analysis_type: Optional[str] = None
    recommendations: Optional[List[str]] = None
    insights: Optional[List[str]] = None

@dataclass
class ConversationMetrics:
    """Metrics extracted from conversation analysis"""
    response_time: float
    message_length: int
    emotional_tone: str
    engagement_level: float
    intimacy_level: float
    communication_style: str
    topics_discussed: List[str]
    sentiment_score: float
    attachment_indicators: List[str]
    conflict_indicators: List[str]
    positive_indicators: List[str]

@dataclass
class AnalysisResult:
    """Comprehensive analysis result"""
    user_id: str
    project_id: Optional[str]
    analysis_type: str
    overall_score: float
    emotional_analysis: Dict[str, Any]
    communication_patterns: Dict[str, Any]
    relationship_insights: Dict[str, Any]
    red_flags: List[str]
    positive_indicators: List[str]
    recommendations: List[str]
    therapy_suggestions: List[Dict[str, Any]]
    metrics: Optional[ConversationMetrics] = None
    timestamp: datetime = None
    confidence: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class EnhancedAIService:
    """Enhanced AI service combining multiple providers and advanced analysis"""
    
    def __init__(self, provider: AIProvider = AIProvider.OPENAI):
        self.provider = provider
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
        
        # Analysis templates for different relationship contexts
        self.analysis_templates = {
            AnalysisType.SENTIMENT: self._get_sentiment_template(),
            AnalysisType.COMMUNICATION_STYLE: self._get_communication_template(),
            AnalysisType.RELATIONSHIP_HEALTH: self._get_relationship_health_template(),
            AnalysisType.CONFLICT_DETECTION: self._get_conflict_detection_template(),
            AnalysisType.COMPREHENSIVE: self._get_comprehensive_template()
        }
    
    def _initialize_clients(self):
        """Initialize AI provider clients"""
        try:
            if self.provider == AIProvider.OPENAI and openai:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("OpenAI API key not found")
            
            elif self.provider == AIProvider.ANTHROPIC and anthropic:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
                else:
                    logger.warning("Anthropic API key not found")
                    
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
    
    async def analyze_conversation(self, 
                                 conversation_data: Union[str, List[Dict]], 
                                 analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
                                 project_id: Optional[str] = None,
                                 user_id: Optional[str] = None) -> AnalysisResult:
        """Analyze conversation data with specified analysis type"""
        try:
            # Prepare conversation text
            if isinstance(conversation_data, str):
                conversation_text = conversation_data
            else:
                conversation_text = self._format_conversation(conversation_data)
            
            # Get analysis template
            template = self.analysis_templates.get(analysis_type, self.analysis_templates[AnalysisType.COMPREHENSIVE])
            
            # Perform AI analysis
            ai_response = await self._call_ai_provider(template, conversation_text)
            
            # Parse and structure results
            analysis_result = self._parse_analysis_response(ai_response, analysis_type, user_id, project_id)
            
            # Add conversation metrics
            if isinstance(conversation_data, list):
                analysis_result.metrics = self._calculate_conversation_metrics(conversation_data)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in conversation analysis: {e}")
            return self._create_fallback_analysis(analysis_type, user_id, project_id)
    
    async def generate_therapeutic_intervention(self, 
                                              analysis_result: AnalysisResult,
                                              intervention_type: InterventionType,
                                              therapy_approach: TherapyApproach = TherapyApproach.COGNITIVE_BEHAVIORAL) -> Dict[str, Any]:
        """Generate therapeutic intervention based on analysis"""
        try:
            intervention_prompt = self._get_intervention_template(intervention_type, therapy_approach)
            
            # Include analysis context
            context = {
                "analysis_summary": analysis_result.relationship_insights,
                "red_flags": analysis_result.red_flags,
                "positive_indicators": analysis_result.positive_indicators,
                "overall_score": analysis_result.overall_score
            }
            
            prompt = intervention_prompt.format(
                context=json.dumps(context, indent=2),
                intervention_type=intervention_type.value,
                therapy_approach=therapy_approach.value
            )
            
            ai_response = await self._call_ai_provider(prompt, "")
            
            return {
                "intervention_type": intervention_type.value,
                "therapy_approach": therapy_approach.value,
                "content": ai_response.content,
                "confidence": ai_response.confidence,
                "timestamp": datetime.now(timezone.utc),
                "metadata": ai_response.metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating therapeutic intervention: {e}")
            return self._create_fallback_intervention(intervention_type, therapy_approach)
    
    async def real_time_coaching(self, 
                               message: str, 
                               context: Dict[str, Any],
                               project_id: str) -> Dict[str, Any]:
        """Provide real-time coaching suggestions"""
        try:
            coaching_prompt = self._get_real_time_coaching_template()
            
            prompt = coaching_prompt.format(
                message=message,
                context=json.dumps(context, indent=2),
                project_id=project_id
            )
            
            ai_response = await self._call_ai_provider(prompt, "")
            
            return {
                "suggestion": ai_response.content,
                "urgency": self._assess_urgency(message, context),
                "confidence": ai_response.confidence,
                "timestamp": datetime.now(timezone.utc),
                "project_id": project_id
            }
            
        except Exception as e:
            logger.error(f"Error in real-time coaching: {e}")
            return self._create_fallback_coaching()
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format conversation messages into text"""
        formatted = []
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            formatted.append(f"[{timestamp}] {sender}: {content}")
        return "\n".join(formatted)
    
    def _calculate_conversation_metrics(self, messages: List[Dict]) -> ConversationMetrics:
        """Calculate conversation metrics from message data"""
        # Simplified metrics calculation
        total_length = sum(len(msg.get('content', '')) for msg in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        # Basic sentiment analysis (would use more sophisticated methods in production)
        positive_words = ['love', 'happy', 'great', 'wonderful', 'amazing', 'good']
        negative_words = ['hate', 'angry', 'terrible', 'awful', 'bad', 'upset']
        
        positive_count = 0
        negative_count = 0
        
        for msg in messages:
            content = msg.get('content', '').lower()
            positive_count += sum(1 for word in positive_words if word in content)
            negative_count += sum(1 for word in negative_words if word in content)
        
        sentiment_score = (positive_count - negative_count) / max(len(messages), 1)
        
        return ConversationMetrics(
            response_time=0.0,  # Would calculate from timestamps
            message_length=int(avg_length),
            emotional_tone="positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral",
            engagement_level=min(len(messages) / 10.0, 1.0),  # Normalized engagement
            intimacy_level=0.5,  # Would use more sophisticated analysis
            communication_style="collaborative",  # Would analyze patterns
            topics_discussed=["general"],  # Would extract topics
            sentiment_score=max(-1, min(1, sentiment_score)),
            attachment_indicators=[],
            conflict_indicators=[],
            positive_indicators=[]
        )
    
    async def _call_ai_provider(self, prompt: str, context: str) -> AIResponse:
        """Call the configured AI provider"""
        try:
            if self.provider == AIProvider.OPENAI and self.openai_client:
                return await self._call_openai(prompt, context)
            elif self.provider == AIProvider.ANTHROPIC and self.anthropic_client:
                return await self._call_anthropic(prompt, context)
            else:
                return await self._call_fallback(prompt, context)
        except Exception as e:
            logger.error(f"Error calling AI provider: {e}")
            return await self._call_fallback(prompt, context)
    
    async def _call_openai(self, prompt: str, context: str) -> AIResponse:
        """Call OpenAI API"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                confidence=0.8,  # Would calculate based on response
                metadata={"model": "gpt-4", "tokens": response.usage.total_tokens},
                provider="openai",
                model="gpt-4",
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _call_anthropic(self, prompt: str, context: str) -> AIResponse:
        """Call Anthropic API"""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{context}"}
                ]
            )
            
            return AIResponse(
                content=response.content[0].text,
                confidence=0.8,
                metadata={"model": "claude-3-sonnet", "tokens": response.usage.input_tokens + response.usage.output_tokens},
                provider="anthropic",
                model="claude-3-sonnet",
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def _call_fallback(self, prompt: str, context: str) -> AIResponse:
        """Fallback response when AI providers are unavailable"""
        return AIResponse(
            content="Analysis completed with basic algorithms. For enhanced AI insights, please configure an AI provider.",
            confidence=0.3,
            metadata={"fallback": True},
            provider="fallback",
            model="basic",
            timestamp=datetime.now(timezone.utc)
        )
    
    def _parse_analysis_response(self, ai_response: AIResponse, analysis_type: AnalysisType, user_id: str, project_id: str) -> AnalysisResult:
        """Parse AI response into structured analysis result"""
        try:
            # Try to parse JSON response
            if ai_response.content.strip().startswith('{'):
                parsed = json.loads(ai_response.content)
                return AnalysisResult(
                    user_id=user_id or "unknown",
                    project_id=project_id,
                    analysis_type=analysis_type.value,
                    overall_score=parsed.get('overall_score', 0.5),
                    emotional_analysis=parsed.get('emotional_analysis', {}),
                    communication_patterns=parsed.get('communication_patterns', {}),
                    relationship_insights=parsed.get('relationship_insights', {}),
                    red_flags=parsed.get('red_flags', []),
                    positive_indicators=parsed.get('positive_indicators', []),
                    recommendations=parsed.get('recommendations', []),
                    therapy_suggestions=parsed.get('therapy_suggestions', []),
                    confidence=ai_response.confidence
                )
            else:
                # Parse text response
                return self._parse_text_response(ai_response, analysis_type, user_id, project_id)
                
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._create_fallback_analysis(analysis_type, user_id, project_id)
    
    def _parse_text_response(self, ai_response: AIResponse, analysis_type: AnalysisType, user_id: str, project_id: str) -> AnalysisResult:
        """Parse text-based AI response"""
        content = ai_response.content
        
        # Extract insights using simple text parsing
        insights = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        return AnalysisResult(
            user_id=user_id or "unknown",
            project_id=project_id,
            analysis_type=analysis_type.value,
            overall_score=0.7,  # Default score
            emotional_analysis={"summary": content[:200]},
            communication_patterns={"analysis": content},
            relationship_insights={"insights": insights[:5]},
            red_flags=[],
            positive_indicators=insights[:3],
            recommendations=insights[-3:] if len(insights) > 3 else insights,
            therapy_suggestions=[],
            confidence=ai_response.confidence
        )
    
    def _create_fallback_analysis(self, analysis_type: AnalysisType, user_id: str, project_id: str) -> AnalysisResult:
        """Create fallback analysis when AI fails"""
        return AnalysisResult(
            user_id=user_id or "unknown",
            project_id=project_id,
            analysis_type=analysis_type.value,
            overall_score=0.5,
            emotional_analysis={"status": "Analysis unavailable"},
            communication_patterns={"status": "Analysis unavailable"},
            relationship_insights={"status": "Basic analysis completed"},
            red_flags=[],
            positive_indicators=["Communication is active"],
            recommendations=["Continue regular communication", "Consider professional guidance if needed"],
            therapy_suggestions=[],
            confidence=0.3
        )
    
    def _create_fallback_intervention(self, intervention_type: InterventionType, therapy_approach: TherapyApproach) -> Dict[str, Any]:
        """Create fallback intervention"""
        return {
            "intervention_type": intervention_type.value,
            "therapy_approach": therapy_approach.value,
            "content": "Consider taking a moment to reflect on your communication patterns and seek professional guidance if needed.",
            "confidence": 0.3,
            "timestamp": datetime.now(timezone.utc),
            "metadata": {"fallback": True}
        }
    
    def _create_fallback_coaching(self) -> Dict[str, Any]:
        """Create fallback coaching response"""
        return {
            "suggestion": "Take a moment to consider your response carefully.",
            "urgency": "low",
            "confidence": 0.3,
            "timestamp": datetime.now(timezone.utc)
        }
    
    def _assess_urgency(self, message: str, context: Dict[str, Any]) -> str:
        """Assess urgency of coaching intervention"""
        urgent_keywords = ['angry', 'furious', 'hate', 'never', 'always', 'divorce', 'break up']
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in urgent_keywords):
            return "high"
        elif len(message) > 200 or '!' in message:
            return "medium"
        else:
            return "low"
    
    # Template methods for different analysis types
    def _get_sentiment_template(self) -> str:
        return """
You are an expert relationship analyst. Analyze the following conversation for sentiment and emotional patterns.

Provide your analysis in JSON format with the following structure:
{
    "overall_score": 0.0-1.0,
    "emotional_analysis": {
        "dominant_emotions": [],
        "emotional_stability": 0.0-1.0,
        "emotional_reciprocity": 0.0-1.0
    },
    "communication_patterns": {
        "tone": "positive/neutral/negative",
        "engagement_level": 0.0-1.0,
        "response_patterns": []
    },
    "relationship_insights": {
        "connection_strength": 0.0-1.0,
        "communication_health": 0.0-1.0
    },
    "red_flags": [],
    "positive_indicators": [],
    "recommendations": []
}
"""
    
    def _get_communication_template(self) -> str:
        return """
You are an expert communication analyst specializing in relationship dynamics. Analyze the communication patterns in the following conversation.

Focus on:
- Communication styles of each participant
- Turn-taking patterns
- Active listening indicators
- Conflict resolution approaches
- Emotional intelligence displays

Provide structured analysis in JSON format.
"""
    
    def _get_relationship_health_template(self) -> str:
        return """
You are a relationship health specialist. Evaluate the overall health of the relationship based on the conversation.

Assess:
- Trust indicators
- Intimacy levels
- Conflict resolution skills
- Mutual respect
- Future orientation
- Support patterns

Provide comprehensive health assessment in JSON format.
"""
    
    def _get_conflict_detection_template(self) -> str:
        return """
You are a conflict resolution expert. Analyze the conversation for signs of conflict, tension, or disagreement.

Identify:
- Explicit conflicts
- Underlying tensions
- Escalation patterns
- De-escalation attempts
- Resolution strategies
- Unresolved issues

Provide detailed conflict analysis in JSON format.
"""
    
    def _get_comprehensive_template(self) -> str:
        return """
You are a comprehensive relationship analyst with expertise in psychology, communication, and relationship dynamics.

Provide a thorough analysis covering:
1. Emotional patterns and sentiment
2. Communication effectiveness
3. Relationship health indicators
4. Potential areas of concern
5. Strengths and positive patterns
6. Actionable recommendations
7. Therapeutic suggestions

Format your response as detailed JSON with all analysis categories.
"""
    
    def _get_intervention_template(self, intervention_type: InterventionType, therapy_approach: TherapyApproach) -> str:
        return f"""
You are a licensed relationship therapist specializing in {therapy_approach.value} approach.

Based on the following analysis context, provide a {intervention_type.value} intervention:

Context: {{context}}

Provide:
1. Immediate guidance or intervention
2. Specific techniques or exercises
3. Long-term strategies
4. Warning signs to watch for
5. When to seek additional help

Tailor your response to the {therapy_approach.value} therapeutic approach.
"""
    
    def _get_real_time_coaching_template(self) -> str:
        return """
You are a real-time relationship coach. Someone is about to send this message in their relationship:

Message: {message}
Context: {context}
Project ID: {project_id}

Provide immediate, actionable coaching advice:
1. Should they send this message as-is?
2. How could they improve it?
3. What tone should they aim for?
4. Any potential risks or benefits?
5. Alternative approaches?

Be concise but helpful. Focus on immediate actionable advice.
"""