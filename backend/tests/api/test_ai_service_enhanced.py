"""Enhanced tests for AI service to improve coverage."""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    import pytest
    from unittest.mock import Mock, patch, AsyncMock
    from datetime import datetime, timezone
    import asyncio
    import json
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)


try:
    from services.ai_service import AIService
except ImportError:
    AIService = None

try:
    from services.ai_service_kb import AIService as AIServiceKB
except ImportError:
    AIServiceKB = None


class TestAIServiceEnhanced:
    """Enhanced test suite for AI service with comprehensive coverage."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService()
    
    @pytest.fixture
    def ai_service_kb(self):
        """Create AI service KB instance for testing."""
        return AIServiceKB()
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_ai_service_initialization(self, ai_service):
        """Test AI service initialization."""
        assert ai_service is not None
        assert hasattr(ai_service, 'analyze_text')
        assert hasattr(ai_service, 'get_sentiment')
    
    @patch('services.ai_service.openai')
    def test_analyze_text_success(self, mock_openai, ai_service):
        """Test successful text analysis."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sentiment": "positive", "confidence": 0.8}'
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        result = ai_service.analyze_text("This is a great day!")
        
        assert result is not None
        assert 'sentiment' in str(result)
    
    @patch('services.ai_service.openai')
    def test_analyze_text_api_error(self, mock_openai, ai_service):
        """Test API error handling in text analysis."""
        mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            ai_service.analyze_text("Test text")
    
    def test_get_sentiment_positive(self, ai_service):
        """Test sentiment analysis for positive text."""
        with patch.object(ai_service, 'analyze_text') as mock_analyze:
            mock_analyze.return_value = {"sentiment": "positive", "confidence": 0.9}
            
            result = ai_service.get_sentiment("I love this!")
            
            assert result["sentiment"] == "positive"
            assert result["confidence"] == 0.9
    
    def test_get_sentiment_negative(self, ai_service):
        """Test sentiment analysis for negative text."""
        with patch.object(ai_service, 'analyze_text') as mock_analyze:
            mock_analyze.return_value = {"sentiment": "negative", "confidence": 0.8}
            
            result = ai_service.get_sentiment("This is terrible!")
            
            assert result["sentiment"] == "negative"
            assert result["confidence"] == 0.8
    
    def test_get_sentiment_neutral(self, ai_service):
        """Test sentiment analysis for neutral text."""
        with patch.object(ai_service, 'analyze_text') as mock_analyze:
            mock_analyze.return_value = {"sentiment": "neutral", "confidence": 0.7}
            
            result = ai_service.get_sentiment("The weather is okay.")
            
            assert result["sentiment"] == "neutral"
            assert result["confidence"] == 0.7
    
    @patch('services.ai_service_kb.AIService._call_openai')
    def test_kb_service_analyze_conversation(self, mock_call, ai_service_kb):
        """Test knowledge base service conversation analysis."""
        mock_call.return_value = {
            "sentiment": {"label": "positive", "confidence": 0.8},
            "therapeutic": {"risk_level": "low", "patterns": []},
            "suggestions": [{"text": "Great progress!", "confidence": 0.9}]
        }
        
        result = ai_service_kb.analyze_conversation(
            "I'm feeling much better today.",
            analysis_type="sentiment"
        )
        
        assert "sentiment" in result
        assert "therapeutic" in result
        assert "suggestions" in result
    
    @patch('services.ai_service_kb.AIService._call_anthropic')
    def test_kb_service_fallback_to_anthropic(self, mock_anthropic, ai_service_kb):
        """Test fallback to Anthropic when OpenAI fails."""
        mock_anthropic.return_value = {
            "sentiment": {"label": "neutral", "confidence": 0.7},
            "therapeutic": {"risk_level": "medium", "patterns": ["anxiety"]},
            "suggestions": [{"text": "Consider relaxation techniques", "confidence": 0.8}]
        }
        
        with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception("API Error")):
            result = ai_service_kb.analyze_conversation(
                "I'm feeling anxious about tomorrow.",
                analysis_type="therapeutic"
            )
        
        assert "sentiment" in result
        assert "therapeutic" in result
        assert "suggestions" in result
        mock_anthropic.assert_called_once()
    
    def test_kb_service_error_handling(self, ai_service_kb):
        """Test error handling in KB service."""
        with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception("Network Error")):
            with patch('services.ai_service_kb.AIService._call_anthropic', side_effect=Exception("Fallback Error")):
                with pytest.raises(Exception):
                    ai_service_kb.analyze_conversation(
                        "Test text",
                        analysis_type="sentiment"
                    )
    
    @pytest.mark.asyncio
    async def test_async_analysis(self, ai_service_kb):
        """Test asynchronous analysis capabilities."""
        with patch('services.ai_service_kb.AIService._call_openai') as mock_call:
            mock_call.return_value = {
                "sentiment": {"label": "positive", "confidence": 0.8},
                "suggestions": [{"text": "Keep it up!", "confidence": 0.9}]
            }
            
            # Simulate async analysis
            tasks = []
            for i in range(3):
                task = asyncio.create_task(
                    asyncio.to_thread(
                        ai_service_kb.analyze_conversation,
                        f"Test message {i}",
                        "sentiment"
                    )
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            for result in results:
                assert "sentiment" in result
                assert "suggestions" in result
    
    def test_service_configuration(self, ai_service):
        """Test service configuration and settings."""
        # Test default configuration
        assert hasattr(ai_service, 'analyze_text')
        
        # Test with custom configuration
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            service = AIService()
            assert service is not None
    
    def test_rate_limiting_simulation(self, ai_service_kb):
        """Test rate limiting behavior simulation."""
        with patch('services.ai_service_kb.AIService._call_openai') as mock_call:
            # Simulate rate limit error
            mock_call.side_effect = Exception("Rate limit exceeded")
            
            with pytest.raises(Exception) as exc_info:
                ai_service_kb.analyze_conversation(
                    "Test text",
                    analysis_type="sentiment"
                )
            
            assert "Rate limit" in str(exc_info.value)
    
    def test_large_text_handling(self, ai_service_kb):
        """Test handling of large text inputs."""
        large_text = "This is a test. " * 1000  # Large text input
        
        with patch('services.ai_service_kb.AIService._call_openai') as mock_call:
            mock_call.return_value = {
                "sentiment": {"label": "neutral", "confidence": 0.7},
                "suggestions": [{"text": "Text processed successfully", "confidence": 0.8}]
            }
            
            result = ai_service_kb.analyze_conversation(
                large_text,
                analysis_type="sentiment"
            )
            
            assert "sentiment" in result
            assert "suggestions" in result
    
    def test_empty_text_handling(self, ai_service_kb):
        """Test handling of empty or invalid text inputs."""
        with pytest.raises((ValueError, Exception)):
            ai_service_kb.analyze_conversation(
                "",
                analysis_type="sentiment"
            )
        
        with pytest.raises((ValueError, Exception)):
            ai_service_kb.analyze_conversation(
                None,
                analysis_type="sentiment"
            )
    
    def test_different_analysis_types(self, ai_service_kb):
        """Test different analysis types."""
        analysis_types = ["sentiment", "therapeutic", "comprehensive"]
        
        for analysis_type in analysis_types:
            with patch('services.ai_service_kb.AIService._call_openai') as mock_call:
                mock_call.return_value = {
                    "sentiment": {"label": "positive", "confidence": 0.8},
                    "therapeutic": {"risk_level": "low", "patterns": []},
                    "suggestions": [{"text": f"Analysis for {analysis_type}", "confidence": 0.8}]
                }
                
                result = ai_service_kb.analyze_conversation(
                    "Test text for analysis",
                    analysis_type=analysis_type
                )
                
                assert "sentiment" in result
                assert "suggestions" in result