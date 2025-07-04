"""Performance monitoring middleware for Catalyst backend."""
import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("catalyst.performance")


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance and log metrics."""
    
    def __init__(self, app: ASGIApp, log_slow_requests: bool = True, slow_threshold: float = 1.0):
        super().__init__(app)
        self.log_slow_requests = log_slow_requests
        self.slow_threshold = slow_threshold  # seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record start time
        start_time = time.time()
        
        # Get request info
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log metrics
            status_code = response.status_code
            self._log_request_metrics(
                method, url, status_code, process_time, client_ip
            )
            
            # Log slow requests if enabled
            if self.log_slow_requests and process_time > self.slow_threshold:
                logger.warning(
                    f"Slow request detected: {method} {url} took {process_time:.3f}s "
                    f"(status: {status_code}, client: {client_ip})"
                )
            
            return response
            
        except Exception as e:
            # Calculate processing time even for errors
            process_time = time.time() - start_time
            
            # Log error metrics
            logger.error(
                f"Request failed: {method} {url} after {process_time:.3f}s "
                f"(client: {client_ip}, error: {str(e)})"
            )
            
            # Re-raise the exception
            raise
    
    def _log_request_metrics(
        self, method: str, url: str, status_code: int, 
        process_time: float, client_ip: str
    ):
        """Log request metrics."""
        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Log the request
        logger.log(
            log_level,
            f"{method} {url} - {status_code} - {process_time:.3f}s - {client_ip}"
        )
        
        # Log additional metrics for monitoring
        if process_time > 0.5:  # Log requests taking more than 500ms
            logger.info(
                f"Performance metric: {method} {url} took {process_time:.3f}s"
            )


class RequestCounterMiddleware(BaseHTTPMiddleware):
    """Middleware to count requests by endpoint and method."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_counts: Dict[str, int] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract endpoint info
        method = request.method
        path = request.url.path
        
        # Create key for counting
        key = f"{method} {path}"
        
        # Increment counter
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        
        # Process request
        response = await call_next(request)
        
        # Add request count header (useful for debugging)
        response.headers["X-Request-Count"] = str(self.request_counts[key])
        
        # Log request counts periodically
        total_requests = sum(self.request_counts.values())
        if total_requests % 100 == 0:  # Log every 100 requests
            logger.info(f"Total requests processed: {total_requests}")
            logger.debug(f"Request counts by endpoint: {self.request_counts}")
        
        return response
    
    def get_stats(self) -> dict:
        """Get current request statistics."""
        return {
            "total_requests": sum(self.request_counts.values()),
            "endpoints": dict(self.request_counts)
        }