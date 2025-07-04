"""
Enhanced Multi-Provider LLM Router
Supports OpenAI, Mistral, Anthropic, OpenRouter, Ollama, Groq, and Huggingface
"""

import asyncio
import logging
import os
import time
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict

try:
    import httpx
except ImportError:
    httpx = None

# Import AI provider clients
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from mistralai.client import MistralClient as MistralAIClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralAIClient = None
    ChatMessage = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import groq
except ImportError:
    groq = None

# Configure logging
logger = logging.getLogger(__name__)

# Define classes for AI provider management
class AIProviderType:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    GEMINI = "gemini"
    LOCAL = "local"
    CUSTOM = "custom"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    DEEPSEEK = "deepseek"
    
    @classmethod
    def get_all_types(cls):
        """Get all available provider types"""
        return [cls.OPENAI, cls.ANTHROPIC, cls.MISTRAL, cls.OPENROUTER, 
                cls.OLLAMA, cls.GROQ, cls.HUGGINGFACE, cls.GOOGLE, cls.GEMINI, 
                cls.DEEPSEEK]

@dataclass
class AIResponse:
    """Response object from AI providers"""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    cost: float
    latency: float
    timestamp: datetime
    success: bool = True
    confidence: Optional[float] = None
    analysis_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: Optional[float] = None

@dataclass
class ProviderTestResult:
    """Response object for provider connectivity tests"""
    success: bool
    latency: float
    error: Optional[str]
    timestamp: datetime
    provider_type: Optional[str] = None
    provider_id: Optional[int] = None
    message: Optional[str] = None
    response_time_ms: Optional[float] = None

@dataclass 
class AIRequest:
    """Request object for AI providers"""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    provider_type: AIProviderType
    name: str
    base_url: str
    api_key: Optional[str] = None
    default_model: str = ""
    enabled: bool = True
    priority: int = 1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60  # requests per minute
    confidence_score: float = 0.8

class BaseProviderClient:
    """Base class for AI provider clients"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None
        self._last_request_time = 0
        self._request_count = 0
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the specific provider client"""
        # Base implementation - subclasses should override
        logger.warning(f"No client initialization implemented for {self.config.provider_type}")
        self.client = None
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using this provider"""
        # Base implementation with fallback response
        logger.warning(f"No response generation implemented for {self.config.provider_type}")
        return AIResponse(
            content="Provider not fully implemented",
            model=request.get("model", "unknown"),
            provider=self.config.provider_type,
            usage={"input_tokens": 0, "output_tokens": 0},
            cost=0.0,
            latency=0.0,
            timestamp=datetime.now(timezone.utc),
            success=False
        )
    
    async def test_connection(self) -> ProviderTestResult:
        """Test provider connectivity"""
        try:
            if self.client is None:
                return ProviderTestResult(
                    success=False,
                    latency=0.0,
                    error="Client not initialized",
                    timestamp=datetime.now(timezone.utc)
                )
            
            # Basic connectivity test
            start_time = time.time()
            await asyncio.sleep(0.1)  # Simulate network latency
            latency = time.time() - start_time
            
            return ProviderTestResult(
                success=True,
                latency=latency,
                error=None,
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            return ProviderTestResult(
                success=False,
                latency=0.0,
                error=str(e),
                timestamp=datetime.now(timezone.utc)
            )
    
    def _rate_limit_check(self) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Simple rate limiting implementation
        if current_time - self._last_request_time < 60 / self.config.rate_limit_rpm:
            return False
        
        self._last_request_time = current_time
        return True
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for the request - override in subclasses"""
        return 0.0

class OpenAIClient(BaseProviderClient):
    """OpenAI provider client"""
    
    def _initialize_client(self):
        if not openai:
            raise ImportError("OpenAI library not installed")
        
        if not self.config.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url if self.config.base_url != "https://api.openai.com/v1" else None
        )
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using OpenAI"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages
            messages = []
            for msg in request.get("messages", []):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7),
                stream=False
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = response.usage
            cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens, model)
            
            return AIResponse(
                content=response.choices[0].message.content,
                provider=self.config.provider_type,
                model=model,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                cost=cost,
                latency=response_time / 1000,  # Convert to seconds
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test OpenAI connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OPENAI,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                latency=response_time / 1000,
                error=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OPENAI,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                latency=(time.time() - start_time),
                error=str(e),
                timestamp=datetime.now(timezone.utc)
            )

class AnthropicClient(BaseProviderClient):
    """Anthropic provider client"""
    
    def _initialize_client(self):
        if not anthropic:
            raise ImportError("Anthropic library not installed")
        
        if not self.config.api_key:
            raise ValueError("Anthropic API key not configured")
        
        self.client = anthropic.Anthropic(api_key=self.config.api_key)
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Anthropic"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages for Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in request.get("messages", []):
                if msg.get("role") == "system":
                    system_message = msg.get("content", "")
                else:
                    user_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Make API call
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7),
                system=system_message if system_message else None,
                messages=user_messages
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens, model)
            
            return AIResponse(
                content=response.content[0].text,
                provider=AIProviderType.ANTHROPIC,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence
                },
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                cost=cost,
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Anthropic connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.ANTHROPIC.value,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.ANTHROPIC.value,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

class MistralClient(BaseProviderClient):
    """Mistral AI provider client"""
    
    def _initialize_client(self):
        if not MistralAIClient:
            raise ImportError("Mistral library not installed")
        
        if not self.config.api_key:
            raise ValueError("Mistral API key not configured")
        
        self.client = MistralAIClient(api_key=self.config.api_key)
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Mistral"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages
            messages = []
            for msg in request.get("messages", []):
                messages.append(ChatMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
            
            # Make API call
            response = await asyncio.to_thread(
                self.client.chat,
                model=model,
                messages=messages,
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7)
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = response.usage
            cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens, model)
            
            return AIResponse(
                content=response.choices[0].message.content,
                provider=AIProviderType.MISTRAL,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "finish_reason": response.choices[0].finish_reason
                },
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                cost=cost,
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Mistral connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.config.default_model,
                messages=[ChatMessage(role="user", content="Hello")],
                max_tokens=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.MISTRAL.value,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.MISTRAL.value,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

class OpenRouterClient(BaseProviderClient):
    """OpenRouter provider client (OpenAI-compatible)"""
    
    def _initialize_client(self):
        if not openai:
            raise ImportError("OpenAI library required for OpenRouter")
        
        if not self.config.api_key:
            raise ValueError("OpenRouter API key not configured")
        
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using OpenRouter"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages
            messages = []
            for msg in request.get("messages", []):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call with OpenRouter-specific headers
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7),
                extra_headers={
                    "HTTP-Referer": "https://catalyst-ai.com",
                    "X-Title": "Catalyst AI Platform"
                }
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = response.usage
            cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens, model)
            
            return AIResponse(
                content=response.choices[0].message.content,
                provider=AIProviderType.OPENROUTER,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model_version": response.model
                },
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                cost=cost,
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test OpenRouter connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OPENROUTER.value,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OPENROUTER.value,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

class OllamaClient(BaseProviderClient):
    """Ollama local provider client"""
    
    def _initialize_client(self):
        # Ollama doesn't require a client library, just HTTP requests
        if not httpx:
            raise ImportError("httpx library not installed")
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Ollama"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Use Ollama's chat API format
            messages = []
            for msg in request.get("messages", []):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call to Ollama chat endpoint
            response = await self.client.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": request.get("temperature", 0.7),
                        "num_predict": request.get("max_tokens", 1000)
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            
            # Extract response content
            content = ""
            if "message" in result and "content" in result["message"]:
                content = result["message"]["content"]
            
            return AIResponse(
                content=content,
                provider=AIProviderType.OLLAMA,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "done": result.get("done", False),
                    "done_reason": result.get("done_reason", "")
                },
                usage={
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                },
                cost=0.0,  # Ollama is free
                latency=response_time / 1000,
                timestamp=datetime.now(timezone.utc),
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Ollama connectivity"""
        start_time = time.time()
        
        try:
            # Test with the /api/tags endpoint to check if Ollama is running
            response = await self.client.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OLLAMA,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                latency=response_time / 1000,
                error=None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.OLLAMA,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                latency=(time.time() - start_time),
                error=str(e),
                timestamp=datetime.now(timezone.utc)
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

class GroqClient(BaseProviderClient):
    """Groq provider client (OpenAI-compatible)"""
    
    def _initialize_client(self):
        if not openai:
            raise ImportError("OpenAI library required for Groq")
        
        if not self.config.api_key:
            raise ValueError("Groq API key not configured")
        
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Groq"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages
            messages = []
            for msg in request.get("messages", []):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7)
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = response.usage
            cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens, model)
            
            return AIResponse(
                content=response.choices[0].message.content,
                provider=AIProviderType.GROQ,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model_version": response.model
                },
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                cost=cost,
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Groq connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.GROQ.value,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.GROQ.value,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

class HuggingFaceClient(BaseProviderClient):
    """Hugging Face provider client"""
    
    def _initialize_client(self):
        self.client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        )
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Hugging Face Inference API"""
        start_time = time.time()
        model = request.get("model", self.config.default_model)
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare input text from messages
            input_text = ""
            for msg in request.get("messages", []):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    input_text += f"System: {content}\n"
                elif role == "user":
                    input_text += f"User: {content}\n"
                elif role == "assistant":
                    input_text += f"Assistant: {content}\n"
            
            # Make API call to Hugging Face
            response = await self.client.post(
                f"{self.config.base_url}/models/{model}",
                json={
                    "inputs": input_text,
                    "parameters": {
                        "temperature": request.get("temperature", 0.7),
                        "max_new_tokens": request.get("max_tokens", 1000),
                        "do_sample": True
                    }
                }
            )
            
            response.raise_for_status()
            result = response.model_dump_json()
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            
            # Extract generated text
            generated_text = ""
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    generated_text = result[0]["generated_text"]
                    # Remove the input text from the generated text
                    if generated_text.startswith(input_text):
                        generated_text = generated_text[len(input_text):].strip()
            
            return AIResponse(
                content=generated_text,
                provider=AIProviderType.HUGGINGFACE,
                model=model,
                confidence=self.config.confidence_score,
                analysis_type=request.get("analysis_type", "general"),
                metadata={
                    "model_loaded": True
                },
                usage={
                    "prompt_tokens": len(input_text.split()),
                    "completion_tokens": len(generated_text.split()),
                    "total_tokens": len(input_text.split()) + len(generated_text.split())
                },
                cost=0.0,  # Hugging Face Inference API is often free
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Hugging Face connectivity"""
        start_time = time.time()
        
        try:
            # Test with a simple model info request
            response = await self.client.get(f"{self.config.base_url}/models/{self.config.default_model}")
            response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.HUGGINGFACE.value,
                success=True,
                message="Connection successful",
                response_time_ms=response_time,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            return ProviderTestResult(
                provider_id=0,
                provider_type=AIProviderType.HUGGINGFACE.value,
                success=False,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

class GoogleGeminiClient(BaseProviderClient):
    """Google Gemini provider client"""
    
    def _initialize_client(self):
        if not genai:
            raise ImportError("Google Generative AI library not installed")
        
        if not self.config.api_key:
            raise ValueError("Google AI API key not configured")
        
        genai.configure(api_key=self.config.api_key)
        self.client = genai.GenerativeModel(self.config.default_model or "gemini-pro")
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Google Gemini"""
        start_time = time.time()
        model_name = request.get("model", self.config.default_model or "gemini-pro")
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Create a new model instance if needed
            if model_name != (self.config.default_model or "gemini-pro"):
                model = genai.GenerativeModel(model_name)
            else:
                model = self.client
            
            # Prepare input text from messages
            input_text = ""
            for msg in request.get("messages", []):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    input_text += f"System: {content}\n"
                elif role == "user":
                    input_text += f"User: {content}\n"
                elif role == "assistant":
                    input_text += f"Assistant: {content}\n"
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=request.get("temperature", 0.7),
                max_output_tokens=request.get("max_tokens", 1000),
            )
            
            # Make API call
            response = await asyncio.to_thread(
                model.generate_content,
                input_text,
                generation_config=generation_config
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            
            # Extract content
            content = response.text if response.text else ""
            
            # Estimate token usage (Gemini doesn't provide exact counts)
            prompt_tokens = len(input_text.split())
            completion_tokens = len(content.split())
            
            return AIResponse(
                content=content,
                provider=AIProviderType.GEMINI,
                model=model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                cost=0.0,  # Estimate based on pricing
                latency=response_time / 1000,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "candidates": len(response.candidates) if response.candidates else 0,
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None
                }
            )
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Google Gemini connectivity"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.generate_content,
                "Hello",
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                success=True,
                latency=response_time / 1000,
                error=None,
                timestamp=datetime.now(timezone.utc),
                provider_type=AIProviderType.GEMINI,
                message="Connection successful",
                response_time_ms=response_time
            )
            
        except Exception as e:
            return ProviderTestResult(
                success=False,
                latency=(time.time() - start_time),
                error=str(e),
                timestamp=datetime.now(timezone.utc),
                provider_type=AIProviderType.GEMINI,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )

class DeepseekClient(BaseProviderClient):
    """Deepseek provider client (OpenAI-compatible)"""
    
    def _initialize_client(self):
        if not httpx:
            raise ImportError("httpx library required for Deepseek")
        
        if not self.config.api_key:
            raise ValueError("Deepseek API key not configured")
        
        self.client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.base_url = self.config.base_url or "https://api.deepseek.com/v1"
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using Deepseek"""
        start_time = time.time()
        model = request.get("model", self.config.default_model or "deepseek-chat")
        
        try:
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages
            messages = []
            for msg in request.get("messages", []):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": request.get("temperature", 0.7),
                    "max_tokens": request.get("max_tokens", 1000),
                    "stream": False
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = result.get("usage", {})
            
            return AIResponse(
                content=result["choices"][0]["message"]["content"],
                provider=AIProviderType.DEEPSEEK,
                model=model,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                cost=0.0,  # Calculate based on Deepseek pricing
                latency=response_time / 1000,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "finish_reason": result["choices"][0].get("finish_reason"),
                    "model_version": result.get("model")
                }
            )
            
        except Exception as e:
            logger.error(f"Deepseek API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResult:
        """Test Deepseek connectivity"""
        start_time = time.time()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.config.default_model or "deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            )
            
            response.raise_for_status()
            response_time = (time.time() - start_time) * 1000
            
            return ProviderTestResult(
                success=True,
                latency=response_time / 1000,
                error=None,
                timestamp=datetime.now(timezone.utc),
                provider_type=AIProviderType.DEEPSEEK,
                message="Connection successful",
                response_time_ms=response_time
            )
            
        except Exception as e:
            return ProviderTestResult(
                success=False,
                latency=(time.time() - start_time),
                error=str(e),
                timestamp=datetime.now(timezone.utc),
                provider_type=AIProviderType.DEEPSEEK,
                message=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

class EnhancedLLMRouter:
    """Enhanced LLM Router supporting multiple providers"""
    
    def __init__(self):
        self.clients: Dict[AIProviderType, BaseProviderClient] = {}
        self.provider_configs: Dict[AIProviderType, ProviderConfig] = {}
        self.usage_metrics: Dict[str, Any] = defaultdict(dict)
        self.response_cache: Dict[str, AIResponse] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        # This would typically load from database or configuration
        # For now, we'll use environment variables
        
        provider_configs = {
            AIProviderType.OPENAI: ProviderConfig(
                provider_type=AIProviderType.OPENAI,
                name="OpenAI",
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                api_key=os.getenv("OPENAI_API_KEY"),
                default_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),  # Updated to match docs
                priority=1
            ),
            AIProviderType.ANTHROPIC: ProviderConfig(
                provider_type=AIProviderType.ANTHROPIC,
                name="Anthropic",
                base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                default_model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),  # Keep Sonnet for cost efficiency
                priority=2
            ),
            AIProviderType.MISTRAL: ProviderConfig(
                provider_type=AIProviderType.MISTRAL,
                name="Mistral",
                base_url=os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
                api_key=os.getenv("MISTRAL_API_KEY"),
                default_model=os.getenv("MISTRAL_MODEL", "mistral-medium-latest"),  # Keep medium for quality
                priority=3
            ),
            AIProviderType.OPENROUTER: ProviderConfig(
                provider_type=AIProviderType.OPENROUTER,
                name="OpenRouter",
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                api_key=os.getenv("OPENROUTER_API_KEY"),
                default_model=os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-3.5-turbo"),  # Updated to match docs
                priority=4
            ),
            AIProviderType.OLLAMA: ProviderConfig(
                provider_type=AIProviderType.OLLAMA,
                name="Ollama",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                api_key=None,  # Ollama doesn't need API key
                default_model=os.getenv("OLLAMA_MODEL", "llama2"),  # Updated to match docs
                priority=5
            ),
            AIProviderType.GROQ: ProviderConfig(
                provider_type=AIProviderType.GROQ,
                name="Groq",
                base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
                api_key=os.getenv("GROQ_API_KEY"),
                default_model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),  # Updated to match docs
                priority=6
            ),
            AIProviderType.HUGGINGFACE: ProviderConfig(
                provider_type=AIProviderType.HUGGINGFACE,
                name="Hugging Face",
                base_url=os.getenv("HUGGINGFACE_BASE_URL", "https://api-inference.huggingface.co"),
                api_key=os.getenv("HUGGINGFACE_API_KEY"),
                default_model=os.getenv("HUGGINGFACE_MODEL", "google/gemma-7b-it"),  # Updated to match docs
                priority=7
            ),
            AIProviderType.GEMINI: ProviderConfig(
                provider_type=AIProviderType.GEMINI,
                name="Google Gemini",
                base_url=os.getenv("GOOGLE_AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
                api_key=os.getenv("GOOGLE_AI_API_KEY"),  # Updated to match docs
                default_model=os.getenv("GOOGLE_AI_MODEL", "gemini-pro"),  # Updated to match docs
                priority=8
            ),
            AIProviderType.DEEPSEEK: ProviderConfig(
                provider_type=AIProviderType.DEEPSEEK,
                name="Deepseek",
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                default_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),  # Updated to match docs
                priority=9
            )
        }
        
        # Initialize clients for configured providers
        client_classes = {
            AIProviderType.OPENAI: OpenAIClient,
            AIProviderType.ANTHROPIC: AnthropicClient,
            AIProviderType.MISTRAL: MistralClient,
            AIProviderType.OPENROUTER: OpenRouterClient,
            AIProviderType.OLLAMA: OllamaClient,
            AIProviderType.GROQ: GroqClient,
            AIProviderType.HUGGINGFACE: HuggingFaceClient,
            AIProviderType.GEMINI: GoogleGeminiClient,
            AIProviderType.DEEPSEEK: DeepseekClient
        }
        
        for provider_type, config in provider_configs.items():
            # Allow initialization if API key exists or if it's Ollama (which doesn't need API key)
            if config.enabled and (config.api_key or provider_type == AIProviderType.OLLAMA):
                try:
                    client_class = client_classes.get(provider_type)
                    if client_class:
                        self.clients[provider_type] = client_class(config)
                        self.provider_configs[provider_type] = config
                        logger.info(f"Initialized {provider_type} client")
                    else:
                        logger.warning(f"No client class found for {provider_type}")
                except Exception as e:
                    logger.warning(f"Failed to initialize {provider_type} client: {str(e)}")
    
    async def generate_response(self, request: Dict[str, Any]) -> AIResponse:
        """Generate response using the best available provider"""
        # Select provider based on request preferences and availability
        provider_type = self._select_provider(request)
        
        if provider_type not in self.clients:
            raise Exception(f"Provider {provider_type} not available")
        
        client = self.clients[provider_type]
        
        # Generate response with retries
        max_retries = self.provider_configs[provider_type].max_retries
        for attempt in range(max_retries):
            try:
                response = await client.generate_response(request)
                
                # Record usage metrics
                self._record_usage(provider_type, response)
                
                return response
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {provider_type}: {str(e)}")
                
                if attempt < max_retries - 1:
                    # Try fallback provider
                    fallback_provider = self._get_fallback_provider(provider_type)
                    if fallback_provider and fallback_provider in self.clients:
                        provider_type = fallback_provider
                        client = self.clients[provider_type]
                        logger.info(f"Falling back to {provider_type}")
                    else:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        raise Exception("All retry attempts failed")
    
    def _select_provider(self, request: Dict[str, Any]) -> AIProviderType:
        """Select the best provider for the request"""
        # Check if provider is explicitly requested
        if "provider_preference" in request:
            provider_pref = AIProviderType(request["provider_preference"])
            if provider_pref in self.clients:
                return provider_pref
        
        # Select based on priority and availability
        available_providers = sorted(
            self.provider_configs.items(),
            key=lambda x: x[1].priority
        )
        
        for provider_type, config in available_providers:
            if provider_type in self.clients and config.enabled:
                return provider_type
        
        raise Exception("No available providers")
    
    def _get_fallback_provider(self, current_provider: AIProviderType) -> Optional[AIProviderType]:
        """Get fallback provider for the current one"""
        available_providers = sorted(
            [(pt, config) for pt, config in self.provider_configs.items() 
             if pt != current_provider and pt in self.clients],
            key=lambda x: x[1].priority
        )
        
        return available_providers[0][0] if available_providers else None
    
    def _record_usage(self, provider_type: AIProviderType, response: AIResponse):
        """Record usage metrics"""
        metrics_key = f"{provider_type}_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        
        if metrics_key not in self.usage_metrics:
            self.usage_metrics[metrics_key] = {
                "requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "total_time": 0.0
            }
        
        metrics = self.usage_metrics[metrics_key]
        metrics["requests"] += 1
        metrics["total_tokens"] += response.usage.get("total_tokens", 0)
        metrics["total_cost"] += response.cost
        metrics["total_time"] += response.response_time_ms

# Global router instance
enhanced_llm_router = EnhancedLLMRouter()

# Backward compatibility function
async def generate_ai_response(request: Dict[str, Any]) -> AIResponse:
    """Generate AI response using the enhanced router"""
    return await enhanced_llm_router.generate_response(request)
