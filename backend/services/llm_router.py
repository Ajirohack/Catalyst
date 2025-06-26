"""LLM Router Service for Catalyst
Advanced routing and management system for multiple AI providers
"""

import asyncio
import logging
import os
import time
try:
    from datetime import datetime, timedelta, timezone
    from typing import Dict, List, Optional, Any, Tuple
    import json
    import hashlib
    from dataclasses import dataclass, field
    from collections import defaultdict
    import uuid
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

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
    import httpx
except ImportError:
    httpx = None

# Define placeholder classes and functions for imports that may not be available
class AIProviderType:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    LOCAL = "local"
    CUSTOM = "custom"

class ProviderConfig:
    def __init__(self, **kwargs):
        self.provider_type = kwargs.get('provider_type', AIProviderType.OPENAI)
        self.default_model = kwargs.get('default_model', 'gpt-3.5-turbo')
        self.enabled = kwargs.get('enabled', True)
        self.models = kwargs.get('models', {
            'gpt-3.5-turbo': {
                'cost_per_1k_tokens': {
                    'input': 0.001,
                    'output': 0.002
                }
            }
        })
        self.rate_limits = kwargs.get('rate_limits', {
            'requests_per_minute': 60
        })
        self.base_url = kwargs.get('base_url', None)
        
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def get_api_key(self):
        """Get API key from environment or config"""
        if self.provider_type == AIProviderType.OPENAI:
            return os.getenv("OPENAI_API_KEY", "")
        elif self.provider_type == AIProviderType.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY", "")
        return ""

class AIProvidersConfig:
    def __init__(self, **kwargs):
        self.enable_response_caching = kwargs.get('enable_response_caching', True)
        self.cache_ttl = kwargs.get('cache_ttl', 3600)  # 1 hour by default
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_base_delay = kwargs.get('retry_base_delay', 2)
        self.fallback_enabled = kwargs.get('fallback_enabled', True)
        self.rate_limit_delay_ms = kwargs.get('rate_limit_delay_ms', 100)
        self.openai_confidence = kwargs.get('openai_confidence', 0.9)
        self.anthropic_confidence = kwargs.get('anthropic_confidence', 0.85)
        self.local_confidence = kwargs.get('local_confidence', 0.7)
        
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

def get_provider_config(provider_type):
    """Get provider configuration"""
    return ProviderConfig(provider_type=provider_type)

def get_available_providers():
    """Get list of available provider configurations"""
    return [
        ProviderConfig(provider_type=AIProviderType.OPENAI)
    ]

def get_default_provider():
    """Get default provider type"""
    return AIProviderType.OPENAI
# Define placeholder classes for schemas
class AIRequest:
    def __init__(self, **kwargs):
        self.messages = kwargs.get('messages', [])
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.temperature = kwargs.get('temperature', 0.7)
        self.analysis_type = kwargs.get('analysis_type', 'general')
        self.provider_preference = kwargs.get('provider_preference', None)
        self.model_preference = kwargs.get('model_preference', None)
        
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class AIResponse:
    def __init__(self, **kwargs):
        self.content = kwargs.get('content', '')
        self.provider = kwargs.get('provider', AIProviderType.OPENAI)
        self.model = kwargs.get('model', 'default')
        self.confidence = kwargs.get('confidence', 0.0)
        self.analysis_type = kwargs.get('analysis_type', 'general')
        self.metadata = kwargs.get('metadata', {})
        self.usage = kwargs.get('usage', {})
        self.cost = kwargs.get('cost', 0.0)
        self.response_time_ms = kwargs.get('response_time_ms', 0.0)
        self.timestamp = kwargs.get('timestamp', datetime.now(timezone.utc))
        
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

class AnalysisResult:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProviderStatus:
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    ACTIVE = "active"
    INACTIVE = "inactive"

class UsageMetrics:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class CostAnalysis:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProviderTestResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class RouteAnalysisRequest:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class RouteAnalysisResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Metrics for individual requests"""
    provider: str  # Changed from AIProviderType to str for compatibility
    model: str
    tokens_used: int
    cost: float
    response_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ProviderClient:
    """Base class for AI provider clients"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None
        self._last_request_time = 0
        self._request_count = 0
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the specific provider client"""
        raise NotImplementedError
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using this provider"""
        raise NotImplementedError
    
    async def test_connection(self) -> ProviderTestResponse:
        """Test provider connectivity"""
        raise NotImplementedError
    
    def _rate_limit_check(self) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Simple rate limiting implementation
        if "requests_per_minute" in self.config.rate_limits:
            if current_time - self._last_request_time < 60 / self.config.rate_limits["requests_per_minute"]:
                return False
        
        return True
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for the request"""
        if model not in self.config.models:
            return 0.0
        
        model_info = self.config.models[model]
        cost_info = model_info.get("cost_per_1k_tokens", {})
        
        input_cost = (input_tokens / 1000) * cost_info.get("input", 0)
        output_cost = (output_tokens / 1000) * cost_info.get("output", 0)
        
        return input_cost + output_cost

class OpenAIClient(ProviderClient):
    """OpenAI provider client"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if not openai:
            raise ImportError("OpenAI library not installed")
        
        api_key = self.config.get_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenAI"""
        start_time = time.time()
        model = request.model_preference or self.config.default_model
        
        try:
            # Rate limiting check
            if not self._rate_limit_check():
                delay_ms = llm_router.config.rate_limit_delay_ms if hasattr(llm_router, 'config') else 100
                await asyncio.sleep(delay_ms / 1000)  # Convert to seconds
            
            # Prepare messages
            messages = []
            for msg in request.messages:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Make API call
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            usage = response.usage
            cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens, model)
            
            # Get confidence from config
            config = llm_router.config if hasattr(llm_router, 'config') else None
            confidence = config.openai_confidence if config else 0.9
            
            return AIResponse(
                content=response.choices[0].message.content,
                provider=AIProviderType.OPENAI,
                model=model,
                confidence=confidence,
                analysis_type=request.analysis_type,
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
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResponse:
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
            
            return ProviderTestResponse(
                provider_type=AIProviderType.OPENAI,
                success=True,
                response_time_ms=response_time,
                model_used=self.config.default_model,
                response_preview=response.choices[0].message.content[:50]
            )
            
        except Exception as e:
            return ProviderTestResponse(
                provider_type=AIProviderType.OPENAI,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

class AnthropicClient(ProviderClient):
    """Anthropic provider client"""
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        if not anthropic:
            raise ImportError("Anthropic library not installed")
        
        api_key = self.config.get_api_key()
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using Anthropic"""
        start_time = time.time()
        model = request.model_preference or self.config.default_model
        
        try:
            # Rate limiting check
            if not self._rate_limit_check():
                await asyncio.sleep(0.1)
            
            # Prepare messages for Anthropic format
            system_message = ""
            user_messages = []
            
            for msg in request.messages:
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
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7,
                system=system_message if system_message else None,
                messages=user_messages
            )
            
            # Calculate metrics
            response_time = (time.time() - start_time) * 1000
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens, model)
            
            # Get confidence from config
            config = llm_router.config if hasattr(llm_router, 'config') else None
            confidence = config.anthropic_confidence if config else 0.85
            
            return AIResponse(
                content=response.content[0].text,
                provider=AIProviderType.ANTHROPIC,
                model=model,
                confidence=confidence,
                analysis_type=request.analysis_type,
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
    
    async def test_connection(self) -> ProviderTestResponse:
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
            
            return ProviderTestResponse(
                provider_type=AIProviderType.ANTHROPIC,
                success=True,
                response_time_ms=response_time,
                model_used=self.config.default_model,
                response_preview=response.content[0].text[:50]
            )
            
        except Exception as e:
            return ProviderTestResponse(
                provider_type=AIProviderType.ANTHROPIC,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

class LocalClient(ProviderClient):
    """Local model provider client (Ollama)"""
    
    def _initialize_client(self):
        """Initialize local client"""
        if not httpx:
            raise ImportError("httpx library not installed")
        
        default_base_url = os.getenv("LOCAL_MODEL_BASE_URL", "http://localhost:11434")
        self.client = httpx.AsyncClient(base_url=self.config.base_url or default_base_url)
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using local models"""
        start_time = time.time()
        model = request.model_preference or self.config.default_model
        
        try:
            # Prepare prompt for local model
            prompt = ""
            for msg in request.messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            
            # Make API call to Ollama
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature or 0.7,
                        "num_predict": request.max_tokens or 1000
                    }
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Local model API error: {response.status_code}")
            
            result = response.model_dump_json()
            response_time = (time.time() - start_time) * 1000
            
            # Estimate token usage (local models don't provide exact counts)
            estimated_tokens = len(result.get("response", "").split()) * 1.3
            
            # Get confidence from config
            config = llm_router.config if hasattr(llm_router, 'config') else None
            confidence = config.local_confidence if config else 0.7
            
            return AIResponse(
                content=result.get("response", ""),
                provider=AIProviderType.LOCAL,
                model=model,
                confidence=confidence,
                analysis_type=request.analysis_type,
                metadata={
                    "model_info": result.get("model_info", {}),
                    "total_duration": result.get("total_duration", 0)
                },
                usage={
                    "total_tokens": int(estimated_tokens),
                    "prompt_tokens": int(estimated_tokens * 0.6),
                    "completion_tokens": int(estimated_tokens * 0.4)
                },
                cost=0.0,  # Local models are free
                response_time_ms=response_time
            )
            
        except Exception as e:
            logger.error(f"Local model API error: {str(e)}")
            raise
    
    async def test_connection(self) -> ProviderTestResponse:
        """Test local model connectivity"""
        start_time = time.time()
        
        try:
            response = await self.client.get("/api/tags")
            
            if response.status_code == 200:
                models = response.model_dump_json().get("models", [])
                return ProviderTestResponse(
                    provider_type=AIProviderType.LOCAL,
                    success=True,
                    response_time_ms=(time.time() - start_time) * 1000,
                    model_used=self.config.default_model,
                    response_preview=f"Found {len(models)} local models"
                )
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            return ProviderTestResponse(
                provider_type=AIProviderType.LOCAL,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

class LLMRouter:
    """Main LLM Router class for managing multiple AI providers"""
    
    def __init__(self):
        self.config = AIProvidersConfig()
        self.clients = {}  # Dictionary of provider type (str) to client instance
        self.usage_metrics = {}  # Dictionary of metrics ID to RequestMetrics
        self.response_cache = {}  # Dictionary of cache key to AIResponse
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all available provider clients"""
        available_providers = get_available_providers()
        
        for provider_config in available_providers:
            try:
                if provider_config.provider_type == AIProviderType.OPENAI:
                    self.clients[AIProviderType.OPENAI] = OpenAIClient(provider_config)
                elif provider_config.provider_type == AIProviderType.ANTHROPIC:
                    self.clients[AIProviderType.ANTHROPIC] = AnthropicClient(provider_config)
                elif provider_config.provider_type == AIProviderType.LOCAL:
                    self.clients[AIProviderType.LOCAL] = LocalClient(provider_config)
                
                logger.info(f"Initialized {provider_config.provider_type} client")
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider_config.provider_type}: {str(e)}")
    
    def _generate_cache_key(self, request: AIRequest) -> str:
        """Generate cache key for request"""
        content = json.dumps(request.messages, sort_keys=True)
        key_data = f"{request.analysis_type}_{content}_{request.temperature}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _select_provider(self, request: AIRequest) -> Tuple[str, str]:
        """Select the best provider for the request"""
        # If specific provider requested and available
        if request.provider_preference and request.provider_preference in self.clients:
            config = get_provider_config(request.provider_preference)
            return request.provider_preference, request.model_preference or config.default_model
        
        # Smart selection based on analysis type and requirements
        available_providers = [p for p in get_available_providers() if p.provider_type in self.clients]
        
        if not available_providers:
            raise Exception("No available providers")
        
        # Simple selection logic (can be enhanced with more sophisticated routing)
        # For now, use priority order
        selected_provider = available_providers[0]
        
        # Analysis-specific routing
        if request.analysis_type in ["sentiment", "simple_analysis"]:
            # Prefer cost-effective options for simple analyses
            for provider in available_providers:
                if provider.provider_type == AIProviderType.LOCAL:
                    selected_provider = provider
                    break
        elif request.analysis_type in ["comprehensive", "therapeutic"]:
            # Prefer high-quality models for complex analyses
            for provider in available_providers:
                if provider.provider_type in [AIProviderType.OPENAI, AIProviderType.ANTHROPIC]:
                    selected_provider = provider
                    break
        
        model = request.model_preference or selected_provider.default_model
        return selected_provider.provider_type, model
    
    async def route_request(self, request: AIRequest) -> RouteAnalysisResponse:
        """Analyze and return routing decision without executing"""
        provider_type, model = self._select_provider(request)
        config = get_provider_config(provider_type)
        
        # Estimate cost and time
        estimated_tokens = sum(len(msg.get("content", "").split()) for msg in request.messages) * 2
        
        cost_info = config.models.get(model, {}).get("cost_per_1k_tokens", {})
        estimated_cost = (estimated_tokens / 1000) * (cost_info.get("input", 0) + cost_info.get("output", 0))
        
        # Estimate time based on provider (rough estimates)
        time_estimates = {
            "openai": 2000,      # 2 seconds
            "anthropic": 3000,   # 3 seconds
            "local": 5000        # 5 seconds
        }
        estimated_time = time_estimates.get(provider_type, 3000)
        
        return RouteAnalysisResponse(
            selected_provider=provider_type,
            selected_model=model,
            reason=f"Selected based on analysis type '{request.analysis_type}' and provider priority",
            estimated_cost=estimated_cost,
            estimated_time_ms=estimated_time
        )
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using the best available provider"""
        # Check cache first
        if self.config.enable_response_caching:
            cache_key = self._generate_cache_key(request)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                # Check if cache is still valid
                cache_age = (datetime.now(timezone.utc) - cached_response.timestamp).total_seconds()
                if cache_age < self.config.cache_ttl:
                    logger.info(f"Returning cached response for {request.analysis_type}")
                    return cached_response
        
        # Select provider
        provider_type, model = self._select_provider(request)
        
        if provider_type not in self.clients:
            raise Exception(f"Provider {provider_type} not available")
        
        client = self.clients[provider_type]
        
        # Update request with selected model
        request.model_preference = model
        
        # Generate response with retries
        for attempt in range(self.config.max_retries):
            try:
                response = await client.generate_response(request)
                
                # Record metrics
                self._record_metrics(
                    provider_type, model, response.usage.get("total_tokens", 0),
                    response.cost, response.response_time_ms, True
                )
                
                # Cache response
                if self.config.enable_response_caching:
                    self.response_cache[cache_key] = response
                
                return response
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {provider_type}: {str(e)}")
                
                if attempt < self.config.max_retries - 1:
                    # Try fallback provider
                    if self.config.fallback_enabled:
                        available_providers = get_available_providers()
                        for fallback_config in available_providers:
                            if (fallback_config.provider_type != provider_type and 
                                fallback_config.provider_type in self.clients):
                                provider_type = fallback_config.provider_type
                                model = fallback_config.default_model
                                client = self.clients[provider_type]
                                logger.info(f"Falling back to {provider_type}")
                                break
                        else:
                            base_delay = self.config.retry_base_delay if hasattr(self, 'config') else 2
                            await asyncio.sleep(base_delay ** attempt)  # Exponential backoff
                    else:
                        base_delay = self.config.retry_base_delay if hasattr(self, 'config') else 2
                        await asyncio.sleep(base_delay ** attempt)
                else:
                    # Record failed metrics
                    self._record_metrics(provider_type, model, 0, 0, 0, False, str(e))
                    raise
        
        raise Exception("All retry attempts failed")
    
    def _record_metrics(self, provider: str, model: str, tokens: int, 
                       cost: float, response_time: float, success: bool, 
                       error_message: Optional[str] = None):
        """Record request metrics"""
        metrics = RequestMetrics(
            provider=provider,
            model=model,
            tokens_used=tokens,
            cost=cost,
            response_time=response_time,
            success=success,
            error_message=error_message
        )
        
        # Store with unique ID
        metrics_id = str(uuid.uuid4())
        self.usage_metrics[metrics_id] = metrics
        
        # Cleanup old metrics (keep last 1000)
        if len(self.usage_metrics) > 1000:
            oldest_keys = sorted(self.usage_metrics.keys())[:len(self.usage_metrics) - 1000]
            for key in oldest_keys:
                del self.usage_metrics[key]
    
    async def test_all_providers(self) -> List[ProviderTestResponse]:
        """Test all configured providers"""
        results = []
        
        for provider_type, client in self.clients.items():
            try:
                result = await client.test_connection()
                results.append(result)
            except Exception as e:
                results.append(ProviderTestResponse(
                    provider_type=provider_type,
                    success=False,
                    response_time_ms=0,
                    error_message=str(e)
                ))
        
        return results
    
    def get_usage_metrics(self, time_period: str = "last_24h") -> Dict[str, UsageMetrics]:
        """Get usage metrics for specified time period"""
        now = datetime.now(timezone.utc)
        
        # Define time cutoff
        if time_period == "last_24h":
            cutoff = now - timedelta(hours=24)
        elif time_period == "last_week":
            cutoff = now - timedelta(weeks=1)
        elif time_period == "last_month":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(hours=24)  # Default
        
        # Aggregate metrics by provider
        provider_metrics = {}
        
        for metrics in self.usage_metrics.values():
            if metrics.timestamp >= cutoff:
                provider = metrics.provider
                
                # Initialize provider data if not exists
                if provider not in provider_metrics:
                    provider_metrics[provider] = {
                        "requests": 0,
                        "tokens": 0,
                        "cost": 0.0,
                        "response_times": [],
                        "errors": 0,
                        "last_used": None
                    }
                
                provider_metrics[provider]["requests"] += 1
                provider_metrics[provider]["tokens"] += metrics.tokens_used
                provider_metrics[provider]["cost"] += metrics.cost
                provider_metrics[provider]["response_times"].append(metrics.response_time)
                
                if not metrics.success:
                    provider_metrics[provider]["errors"] += 1
                
                if (provider_metrics[provider]["last_used"] is None or 
                    metrics.timestamp > provider_metrics[provider]["last_used"]):
                    provider_metrics[provider]["last_used"] = metrics.timestamp
        
        # Convert to UsageMetrics objects
        result = {}
        for provider, data in provider_metrics.items():
            avg_response_time = (sum(data["response_times"]) / len(data["response_times"]) 
                               if data["response_times"] else 0.0)
            
            result[provider] = UsageMetrics(
                provider_type=provider,
                model="aggregated",
                requests_count=data["requests"],
                total_tokens=data["tokens"],
                total_cost=data["cost"],
                average_response_time=avg_response_time,
                error_count=data["errors"],
                last_used=data["last_used"]
            )
        
        return result
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def get_provider_status(self) -> Dict[str, str]:
        """Get current status of all providers"""
        status = {}
        
        # Define provider types to check
        provider_types = [AIProviderType.OPENAI, AIProviderType.ANTHROPIC, AIProviderType.LOCAL]
        
        for provider_type in provider_types:
            if provider_type in self.clients:
                status[provider_type] = ProviderStatus.ACTIVE
            else:
                config = get_provider_config(provider_type)
                if config and config.enabled:
                    status[provider_type] = ProviderStatus.ERROR
                else:
                    status[provider_type] = ProviderStatus.INACTIVE
        
        return status

@dataclass
class AIProvider:
    """AI Provider data class"""
    provider_id: str
    provider_type: str = "unknown"
    name: str = "Unknown Provider"
    description: str = ""
    is_active: bool = True
    priority: int = 0
    models: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "name": self.name,
            "is_active": self.is_active,
            "priority": self.priority,
            "models": self.models
        }

# Helper function to get provider status (different from the method in LLMRouter)
def get_providers_status_helper():
    """Return the status of all providers"""
    # Create a sample provider with the required fields
    return {
        "providers": [{
            "provider_id": "openai",
            "provider_type": AIProviderType.OPENAI,
            "name": "OpenAI",
            "is_active": True,
            "priority": 1,
            "models": ["gpt-3.5-turbo", "gpt-4"]
        }], 
        "active_count": 1
    }

# Global router instance
llm_router = LLMRouter()

# Export main functions for easy import
async def generate_ai_response(request: AIRequest) -> AIResponse:
    """Generate AI response using the router"""
    return await llm_router.generate_response(request)

async def route_analysis_request(request: AIRequest) -> RouteAnalysisResponse:
    """Get routing analysis without executing"""
    return await llm_router.route_request(request)

async def test_providers() -> List[ProviderTestResponse]:
    """Test all providers"""
    return await llm_router.test_all_providers()

def get_system_usage_metrics(time_period: str = "last_24h") -> Dict[str, UsageMetrics]:
    """Get system usage metrics"""
    return llm_router.get_usage_metrics(time_period)

def get_providers_status() -> Dict[str, str]:
    """Get providers status"""
    return llm_router.get_provider_status()

# Initialize on import
logger.info("LLM Router initialized successfully")
logger.info(f"Available providers: {list(llm_router.clients.keys())}")
