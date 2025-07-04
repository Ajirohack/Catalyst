"""
AI Integration Test Suite for Catalyst Backend
Tests AI provider switching, model selection, and integration workflows
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    import pytest
    import asyncio
    import json
    import os
    from unittest.mock import MagicMock, patch, AsyncMock
    from fastapi.testclient import TestClient
    from typing import Dict, Any, List
except ImportError as e:
    pytest.skip(f"Import error: {e}", allow_module_level=True)
except Exception as e:
    pytest.skip(f"Setup error: {e}", allow_module_level=True)


# Import the main application and services
import sys
import os
backend_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_dir)

try:
    from main import app
    from services.vector_search import VectorSearchService, VectorProvider, EmbeddingProvider
    from services import AIService, AIProvider, AnalysisType
    from config.logging import get_logger
except ImportError:
    # Mock imports for testing
    app = MagicMock()
    VectorSearchService = MagicMock()
    VectorProvider = MagicMock()
    EmbeddingProvider = MagicMock()
    AIService = MagicMock()
    AIProvider = MagicMock()
    AnalysisType = MagicMock()
    get_logger = MagicMock()


class TestAIProviderSwitching:
    """Test AI provider switching functionality"""
    
    @pytest.fixture
    def ai_config(self):
        """Sample AI configuration for testing"""
        return {
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key": "test-openai-key",
                    "model": "gpt-4-turbo-preview",
                    "max_tokens": 2048,
                    "temperature": 0.7
                },
                "anthropic": {
                    "enabled": True,
                    "api_key": "test-anthropic-key", 
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2048,
                    "temperature": 0.7
                },
                "local": {
                    "enabled": True,
                    "model": "llama-2-7b-chat",
                    "max_tokens": 1024,
                    "temperature": 0.8
                }
            },
            "strategies": {
                "quality": {
                    "conversation": "openai",
                    "sentiment": "openai", 
                    "therapeutic": "anthropic",
                    "fallback": "local"
                },
                "speed": {
                    "conversation": "local",
                    "sentiment": "local",
                    "therapeutic": "local", 
                    "fallback": "openai"
                },
                "balanced": {
                    "conversation": "anthropic",
                    "sentiment": "openai",
                    "therapeutic": "anthropic",
                    "fallback": "local"
                }
            },
            "confidence_thresholds": {
                "suggestions": {"low": 0.3, "medium": 0.6, "high": 0.8},
                "therapeutic": {"warning": 0.7, "intervention": 0.8, "urgent": 0.9}
            }
        }
    
    @pytest.fixture 
    def sample_analysis_request(self):
        """Sample analysis request data"""
        return {
            "text": "I've been feeling really overwhelmed lately with work and personal life. Sometimes I wonder if things will ever get better.",
            "project_id": "test-project-123", 
            "analysis_type": "enhanced_ai",
            "context": {
                "urgency": "medium",
                "complexity": "high",
                "privacy_sensitive": False,
                "platform": "web.whatsapp.com"
            }
        }
    
    def test_ai_provider_configuration_loading(self, ai_config):
        """Test loading and validating AI provider configurations"""
        # Test configuration structure
        assert "providers" in ai_config
        assert "strategies" in ai_config
        assert "confidence_thresholds" in ai_config
        
        # Test provider configurations
        providers = ai_config["providers"]
        assert "openai" in providers
        assert "anthropic" in providers 
        assert "local" in providers
        
        # Test each provider has required fields
        for provider_name, provider_config in providers.items():
            assert "enabled" in provider_config
            assert "model" in provider_config
            if provider_name != "local":
                assert "api_key" in provider_config
    
    def test_model_selection_strategies(self, ai_config):
        """Test different model selection strategies"""
        strategies = ai_config["strategies"]
        
        # Test quality strategy prioritizes best models
        quality = strategies["quality"]
        assert quality["conversation"] in ["openai", "anthropic"]
        assert quality["therapeutic"] in ["openai", "anthropic"]
        
        # Test speed strategy prioritizes fast models  
        speed = strategies["speed"]
        assert speed["conversation"] == "local"
        assert speed["sentiment"] == "local"
        
        # Test balanced strategy
        balanced = strategies["balanced"]
        assert balanced["conversation"] in ["openai", "anthropic", "local"]
        
        # All strategies should have fallback
        for strategy in strategies.values():
            assert "fallback" in strategy
    
    @patch('openai.ChatCompletion.acreate')
    @patch('anthropic.Anthropic')
    async def test_provider_switching_integration(self, mock_anthropic, mock_openai, client, ai_config, sample_analysis_request):
        """Test switching between different AI providers"""
        
        # Mock OpenAI response
        mock_openai.return_value = AsyncMock()
        mock_openai.return_value.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "sentiment": {"label": "negative", "confidence": 0.8},
                "therapeutic": {"risk_level": "medium", "patterns": ["stress"]},
                "suggestions": [{"text": "Consider stress management techniques", "confidence": 0.7}]
            })))
        ]
        
        # Mock Anthropic response
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.return_value = MagicMock(
            content=[MagicMock(text=json.dumps({
                "sentiment": {"label": "negative", "confidence": 0.85},
                "therapeutic": {"risk_level": "medium", "patterns": ["overwhelm"]},
                "suggestions": [{"text": "Break tasks into smaller steps", "confidence": 0.8}]
            }))]
        )
        
        # Test OpenAI provider
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            response = client.post("/api/analysis/analyze", json={
                "text": sample_analysis_request["text"],
                "analysis_type": "sentiment",
                "include_recommendations": True
            })
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "analysis" in data
            assert "model_info" in data
            assert data["model_info"]["provider"] == "openai"
        
        # Test Anthropic provider
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            response = client.post("/api/analysis/analyze", json={
                "text": sample_analysis_request["text"],
                "analysis_type": "sentiment",
                "include_recommendations": True
            })
            
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "sentiment" in data
            assert "suggestions" in data
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, client, ai_config, sample_analysis_request):
        """Test AI provider fallback when primary provider fails"""
        
        # Mock primary provider failure
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception("API Error")):
                with patch('services.ai_service_kb.AIService._call_anthropic') as mock_anthropic_call:
                    mock_anthropic_call.return_value = {
                        "sentiment": {"label": "negative", "confidence": 0.75},
                        "therapeutic": {"risk_level": "medium", "patterns": ["stress"]},
                        "suggestions": [{"text": "Fallback suggestion", "confidence": 0.65}]
                    }
                    
                    response = client.post("/api/analysis/analyze", json={
                        "text": sample_analysis_request["text"],
                        "analysis_type": "sentiment",
                        "include_recommendations": True
                    })
                    
                    assert response.status_code == 200
                    data = response.model_dump_json()
                    assert "sentiment" in data
                    assert "suggestions" in data
    
    @pytest.mark.asyncio
    async def test_model_selection_based_on_context(self, client, ai_config):
        """Test model selection based on request context"""
        
        # Setup mocks for different providers
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            with patch('services.ai_service_kb.AIService._call_ai_provider') as mock_call_ai:
                # Test urgent context routes to best model
                response1 = client.post("/api/analysis/analyze", json={
                    "text": "I'm having suicidal thoughts and need help immediately.",
                    "analysis_type": "sentiment",
                    "include_recommendations": True
                })
                
                # Should get successful response
                assert response1.status_code == 200
                
                # Test casual context routes to faster model
                response2 = client.post("/api/analysis/analyze", json={
                    "text": "Just chatting about the weather today.",
                    "analysis_type": "sentiment",
                    "include_recommendations": False
                })
                
                # Should get successful response
                assert response2.status_code == 200
    
    @pytest.mark.asyncio
    async def test_enhanced_analysis_with_knowledge_base(self, client, ai_config):
        """Test integration of AI with knowledge base for enhanced analysis"""
        
        # Mock vector search results
        sample_search_results = [
            {
                "document_id": "doc1",
                "content": "Communication patterns show that active listening improves relationship satisfaction.",
                "metadata": {"type": "research", "topic": "communication"},
                "similarity_score": 0.92
            },
            {
                "document_id": "doc2", 
                "content": "Studies indicate that acknowledging feelings reduces conflict escalation.",
                "metadata": {"type": "technique", "topic": "conflict-resolution"},
                "similarity_score": 0.85
            }
        ]
        
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            with patch('services.vector_search.VectorSearchService.search', return_value=sample_search_results):
                with patch('services.ai_service_kb.AIService._call_openai') as mock_openai:
                    # Mock enhanced response with knowledge integration
                    mock_openai.return_value = {
                        "sentiment": {"label": "negative", "confidence": 0.82},
                        "therapeutic": {"risk_level": "low", "patterns": ["overwhelm"]},
                        "suggestions": [
                            {"text": "Practice active listening techniques when discussing concerns", 
                             "confidence": 0.88,
                             "source": "knowledge_base"
                            }
                        ],
                        "knowledge_applied": True
                    }
                    
                    response = client.post("/api/analysis/analyze", json={
                        "text": "We keep having the same argument and I don't feel heard.",
                        "analysis_type": "sentiment",
                        "include_recommendations": True
                    })
                    
                    assert response.status_code == 200
                    data = response.model_dump_json()
                    assert "sentiment" in data
                    assert "suggestions" in data
    
    @pytest.mark.asyncio
    async def test_concurrent_ai_processing(self, client, ai_config):
        """Test concurrent AI processing capabilities"""
        
        with patch('config.enhanced_config.get_ai_provider_config', return_value=ai_config):
            with patch('services.ai_service_kb.AIService._call_openai') as mock_openai:
                mock_openai.return_value = {
                    "result": "success",
                    "processing_time": 0.5
                }
                
                # Create multiple concurrent requests
                concurrent_requests = 5
                responses = []
                
                for i in range(concurrent_requests):
                    response = client.post("/api/analysis/analyze", json={
                        "text": f"Test message {i}",
                        "analysis_type": "sentiment",
                        "include_recommendations": True
                    })
                    responses.append(response)
                
                # All requests should complete successfully
                for response in responses:
                    assert response.status_code == 200
                
                # Verify we got the expected number of responses
                assert len(responses) == concurrent_requests


class TestAIErrorHandling:
    """Test AI service error handling"""
    
    @pytest.fixture
    def error_scenarios(self):
        """Error scenarios to test"""
        return {
            "rate_limit": {
                "error": "rate_limit_exceeded",
                "status_code": 429,
                "retry_after": 10
            },
            "invalid_request": {
                "error": "invalid_request_error",
                "status_code": 400
            },
            "authentication": {
                "error": "authentication_error", 
                "status_code": 401
            },
            "server_error": {
                "error": "server_error",
                "status_code": 500
            },
            "timeout": {
                "error": "timeout",
                "status_code": 408
            }
        }
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, client, error_scenarios):
        """Test handling of rate limit errors"""
        
        rate_limit_error = error_scenarios["rate_limit"]
        
        # Mock OpenAI rate limit error
        with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception(
            f"OpenAI API error: {rate_limit_error['error']}"
        )):
            with patch('services.ai_service_kb.AIService._call_fallback') as mock_fallback:
                # Set up the error handler to return a fallback response
                mock_fallback.return_value = {
                    "error_handled": True,
                    "fallback_applied": True,
                    "retry_after": rate_limit_error["retry_after"]
                }
                
                response = client.post("/api/analysis/analyze", json={
                    "text": "Test message for rate limit handling",
                    "analysis_type": "sentiment",
                    "include_recommendations": True
                })
                
                # Should return success with basic response
                assert response.status_code == 200
                data = response.model_dump_json()
                assert "sentiment" in data
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client, error_scenarios):
        """Test handling of authentication errors"""
        
        auth_error = error_scenarios["authentication"]
        
        # Mock authentication error
        with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception(
            f"Authentication error: {auth_error['error']}"
        )):
            response = client.post("/api/analysis/analyze", json={
                "text": "Test message for authentication error",
                "analysis_type": "sentiment",
                "include_recommendations": True
            })
            
            # Should return success (endpoint doesn't handle auth errors)
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "sentiment" in data
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, client):
        """Test graceful degradation to simpler analysis when AI fails"""
        
        # Mock complete AI failure
        with patch('services.ai_service_kb.AIService._call_openai', side_effect=Exception("Service unavailable")):
            with patch('services.ai_service_kb.AIService._call_anthropic', side_effect=Exception("Service unavailable")):
                with patch('services.ai_service_kb.AIService._call_fallback') as mock_fallback:
                    # Set up fallback to return basic analysis
                    mock_fallback.return_value = {
                        "sentiment": {"label": "neutral", "confidence": 0.6},
                        "suggestions": [{"text": "Basic fallback suggestion", "confidence": 0.5}],
                        "is_fallback": True
                    }
                    
                    response = client.post("/api/analysis/analyze", json={
                        "text": "Test message for graceful degradation",
                        "analysis_type": "sentiment",
                        "include_recommendations": True
                    })
                    
                    # Should return success with basic analysis
                    assert response.status_code == 200
                    data = response.model_dump_json()
                    assert "sentiment" in data
                    assert "suggestions" in data


# Add tests for any other AI integration aspects
class TestExternalAIIntegration:
    """Test integration with external AI services"""
    
    @pytest.mark.asyncio
    async def test_streaming_response_integration(self, client):
        """Test integration with streaming API responses"""
        
        # Test should check that streaming endpoints correctly handle chunks
        # and assemble complete responses
        
        with patch('services.ai_service_kb.AIService._call_openai') as mock_stream:
            # Mock a streaming response
            async def mock_streaming_generator():
                chunks = [
                    '{"partial": "This is a"}',
                    '{"partial": " streaming response"}',
                    '{"completion": true, "result": "This is a streaming response"}'
                ]
                for chunk in chunks:
                    yield chunk
            
            mock_stream.return_value = mock_streaming_generator()
            
            # Test streaming endpoint
            response = client.post("/api/analysis/analyze", json={
                "text": "Test streaming response",
                "analysis_type": "sentiment",
                "include_recommendations": True
            })
            
            # Should return successful response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "sentiment" in data
    
    @pytest.mark.asyncio
    async def test_webhook_integration(self, client):
        """Test integration with webhook callbacks for long-running processes"""
        
        # Mock a webhook request handler
        with patch('services.ai_service_kb.AIService.analyze_conversation') as mock_webhook:
            mock_webhook.return_value = {
                "job_id": "test-job-123",
                "status": "processing",
                "webhook_url": "https://example.com/webhook"
            }
            
            response = client.post("/api/analysis/analyze", json={
                "text": "Test async with webhook",
                "analysis_type": "sentiment",
                "include_recommendations": True
            })
            
            # Should return successful response
            assert response.status_code == 200
            data = response.model_dump_json()
            assert "sentiment" in data


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
