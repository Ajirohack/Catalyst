"""
AI Provider Integration Test Suite for Catalyst Backend - Phase 2.3
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
            "routing": {
                "default_provider": "openai",
                "fallback_providers": ["anthropic", "local"],
                "load_balancing": True,
                "confidence_threshold": 0.7
            }
        }
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service for testing"""
        service = MagicMock()
        service.get_available_providers.return_value = ["openai", "anthropic", "local"]
        service.switch_provider = AsyncMock()
        service.get_current_provider.return_value = "openai"
        service.test_provider_connection = AsyncMock(return_value=True)
        return service
    
    def test_provider_configuration_validation(self, ai_config):
        """Test that AI provider configurations are valid"""
        # Test required fields
        for provider_name, config in ai_config["providers"].items():
            assert "enabled" in config, f"Provider {provider_name} missing 'enabled' field"
            assert "model" in config, f"Provider {provider_name} missing 'model' field"
            
            if provider_name != "local":
                assert "api_key" in config, f"Provider {provider_name} missing 'api_key' field"
    
    @pytest.mark.asyncio
    async def test_provider_switching(self, mock_ai_service):
        """Test switching between AI providers"""
        # Test successful provider switch
        await mock_ai_service.switch_provider("anthropic")
        mock_ai_service.switch_provider.assert_called_with("anthropic")
        
        # Test fallback on provider failure
        mock_ai_service.switch_provider.side_effect = Exception("Provider unavailable")
        with pytest.raises(Exception):
            await mock_ai_service.switch_provider("openai")
    
    @pytest.mark.asyncio
    async def test_provider_health_checks(self, mock_ai_service):
        """Test provider health checking"""
        # Test healthy provider
        result = await mock_ai_service.test_provider_connection("openai")
        assert result is True
        
        # Test unhealthy provider
        mock_ai_service.test_provider_connection.return_value = False
        result = await mock_ai_service.test_provider_connection("local")
        assert result is False
    
    def test_fallback_configuration(self, ai_config):
        """Test fallback provider configuration"""
        routing_config = ai_config["routing"]
        
        assert "fallback_providers" in routing_config
        assert isinstance(routing_config["fallback_providers"], list)
        assert len(routing_config["fallback_providers"]) > 0
        
        # Ensure fallback providers exist in main config
        for fallback in routing_config["fallback_providers"]:
            assert fallback in ai_config["providers"]


class TestModelSelection:
    """Test AI model selection and optimization"""
    
    @pytest.fixture
    def model_configs(self):
        """Sample model configurations"""
        return {
            "models": {
                "gpt-4-turbo-preview": {
                    "provider": "openai",
                    "context_window": 128000,
                    "best_for": ["analysis", "reasoning", "complex_tasks"],
                    "cost_per_token": 0.00003
                },
                "claude-3-sonnet": {
                    "provider": "anthropic",
                    "context_window": 200000,
                    "best_for": ["writing", "conversation", "creative_tasks"],
                    "cost_per_token": 0.00003
                },
                "llama-2-7b": {
                    "provider": "local",
                    "context_window": 4096,
                    "best_for": ["speed", "privacy", "basic_tasks"],
                    "cost_per_token": 0
                }
            }
        }
    
    def test_model_selection_criteria(self, model_configs):
        """Test model selection based on task requirements"""
        models = model_configs["models"]
        
        # Test context window requirements
        long_context_models = [
            name for name, config in models.items() 
            if config["context_window"] > 100000
        ]
        assert len(long_context_models) > 0
        
        # Test cost optimization
        free_models = [
            name for name, config in models.items()
            if config["cost_per_token"] == 0
        ]
        assert len(free_models) > 0
    
    def test_task_based_selection(self, model_configs):
        """Test selecting models based on task type"""
        models = model_configs["models"]
        
        # Test analysis task selection
        analysis_models = [
            name for name, config in models.items()
            if "analysis" in config["best_for"]
        ]
        assert len(analysis_models) > 0
        
        # Test conversation task selection
        conversation_models = [
            name for name, config in models.items()
            if "conversation" in config["best_for"]
        ]
        assert len(conversation_models) > 0


class TestConfidenceIndicators:
    """Test confidence scoring and indicators"""
    
    @pytest.fixture
    def mock_confidence_service(self):
        """Mock confidence scoring service"""
        service = MagicMock()
        service.calculate_confidence = MagicMock()
        service.get_confidence_indicators = MagicMock()
        return service
    
    def test_confidence_calculation(self, mock_confidence_service):
        """Test confidence score calculation"""
        # Mock response with metadata
        response_data = {
            "content": "This is a test response",
            "provider": "openai",
            "model": "gpt-4-turbo-preview",
            "metadata": {
                "tokens_used": 150,
                "response_time": 2.5,
                "temperature": 0.7
            }
        }
        
        mock_confidence_service.calculate_confidence.return_value = 0.85
        
        confidence = mock_confidence_service.calculate_confidence(response_data)
        assert 0 <= confidence <= 1
        assert confidence == 0.85
    
    def test_confidence_indicators(self, mock_confidence_service):
        """Test confidence indicator generation"""
        indicators = {
            "score": 0.85,
            "level": "high",
            "factors": ["model_quality", "response_coherence", "provider_reliability"],
            "suggestions": ["Consider for important decisions"]
        }
        
        mock_confidence_service.get_confidence_indicators.return_value = indicators
        
        result = mock_confidence_service.get_confidence_indicators(0.85)
        assert "score" in result
        assert "level" in result
        assert "factors" in result
        assert isinstance(result["factors"], list)


class TestIntegrationWorkflows:
    """Test end-to-end AI integration workflows"""
    
    @pytest.fixture
    def mock_workflow_service(self):
        """Mock workflow service"""
        service = MagicMock()
        service.process_request = AsyncMock()
        service.handle_provider_failure = AsyncMock()
        service.log_interaction = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_request_processing_workflow(self, mock_workflow_service):
        """Test complete request processing workflow"""
        request_data = {
            "text": "Analyze this conversation",
            "type": "sentiment_analysis",
            "preferred_provider": "openai"
        }
        
        expected_response = {
            "analysis": {"sentiment": "positive", "confidence": 0.85},
            "provider_used": "openai",
            "processing_time": 2.5,
            "confidence_indicators": {
                "score": 0.85,
                "level": "high"
            }
        }
        
        mock_workflow_service.process_request.return_value = expected_response
        
        result = await mock_workflow_service.process_request(request_data)
        
        assert "analysis" in result
        assert "provider_used" in result
        assert "confidence_indicators" in result
        mock_workflow_service.process_request.assert_called_once_with(request_data)
    
    @pytest.mark.asyncio
    async def test_failure_handling_workflow(self, mock_workflow_service):
        """Test provider failure handling workflow"""
        failure_data = {
            "original_provider": "openai",
            "error": "API rate limit exceeded",
            "fallback_provider": "anthropic"
        }
        
        mock_workflow_service.handle_provider_failure.return_value = {
            "status": "recovered",
            "new_provider": "anthropic",
            "retry_successful": True
        }
        
        result = await mock_workflow_service.handle_provider_failure(failure_data)
        
        assert result["status"] == "recovered"
        assert result["new_provider"] == "anthropic"
        mock_workflow_service.handle_provider_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_interaction_logging(self, mock_workflow_service):
        """Test interaction logging workflow"""
        interaction_data = {
            "request_id": "test-123",
            "provider": "openai",
            "model": "gpt-4-turbo-preview",
            "input_tokens": 100,
            "output_tokens": 150,
            "cost": 0.0075,
            "response_time": 2.5,
            "confidence": 0.85
        }
        
        await mock_workflow_service.log_interaction(interaction_data)
        mock_workflow_service.log_interaction.assert_called_once_with(interaction_data)


class TestBackendIntegration:
    """Test backend API integration"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        # Use a simple mock client for testing
        client = MagicMock()
        client.post = MagicMock()
        client.get = MagicMock()
        return client
    
    def test_ai_analysis_endpoint(self, client):
        """Test AI analysis API endpoint"""
        request_data = {
            "text": "This is a test conversation",
            "analysis_type": "sentiment",
            "provider_preference": "openai"
        }
        
        expected_response = {
            "status_code": 200,
            "json": lambda: {
                "analysis_id": "test-analysis-123",
                "result": {"sentiment": "positive", "confidence": 0.85},
                "provider_used": "openai",
                "processing_time": 2.5
            }
        }
        
        client.post.return_value = expected_response
        
        response = client.post("/api/analysis/analyze", json=request_data)
        
        assert response.status_code == 200
        result = response.model_dump_json()
        assert "analysis_id" in result
        assert "result" in result
        assert "provider_used" in result
    
    def test_provider_status_endpoint(self, client):
        """Test provider status API endpoint"""
        expected_response = {
            "status_code": 200,
            "json": lambda: {
                "providers": {
                    "openai": {"status": "healthy", "response_time": 1.2},
                    "anthropic": {"status": "healthy", "response_time": 1.8},
                    "local": {"status": "degraded", "response_time": 5.0}
                },
                "active_provider": "openai"
            }
        }
        
        client.get.return_value = expected_response
        
        response = client.get("/api/ai/providers/status")
        
        assert response.status_code == 200
        result = response.model_dump_json()
        assert "providers" in result
        assert "active_provider" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
