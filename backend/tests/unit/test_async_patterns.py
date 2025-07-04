#!/usr/bin/env python3
"""
Async Test Patterns and Examples
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, List, Any

class TestAsyncPatterns:
    """Test class demonstrating proper async test patterns"""
    
    @pytest.mark.asyncio
    async def test_async_function_basic(self):
        """Test basic async function"""
        async def sample_async_function():
            await asyncio.sleep(0.01)
            return "success"
        
        result = await sample_async_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_async_with_mock(self):
        """Test async function with mocking"""
        mock_service = AsyncMock()
        mock_service.process_data.return_value = {"status": "processed"}
        
        # Test the mocked async function
        result = await mock_service.process_data({"test": "data"})
        assert result["status"] == "processed"
        mock_service.process_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_with_patch(self):
        """Test async function with patch decorator"""
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_sleep.return_value = None
            
            async def test_function():
                await asyncio.sleep(1)
                return "completed"
            
            result = await test_function()
            assert result == "completed"
            mock_sleep.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_async_exception_handling(self):
        """Test async function exception handling"""
        async def failing_function():
            await asyncio.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await failing_function()
    
    @pytest.mark.asyncio
    async def test_async_timeout(self):
        """Test async function with timeout"""
        async def slow_function():
            await asyncio.sleep(2)
            return "slow result"
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_function(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_multiple_async_calls(self):
        """Test multiple async calls"""
        async def async_task(value):
            await asyncio.sleep(0.01)
            return value * 2
        
        # Test concurrent execution
        tasks = [async_task(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        assert results == [0, 2, 4]
    
    def test_sync_function(self):
        """Test regular sync function"""
        def sync_function(x, y):
            return x + y
        
        result = sync_function(2, 3)
        assert result == 5

class TestAsyncServicePatterns:
    """Test patterns for async services"""
    
    @pytest.fixture
    def mock_async_service(self):
        """Fixture for mocked async service"""
        service = AsyncMock()
        service.initialize.return_value = True
        service.process.return_value = {"result": "success"}
        return service
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_async_service):
        """Test async service initialization"""
        result = await mock_async_service.initialize()
        assert result is True
        mock_async_service.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_processing(self, mock_async_service):
        """Test async service processing"""
        data = {"input": "test data"}
        result = await mock_async_service.process(data)
        
        assert result["result"] == "success"
        mock_async_service.process.assert_called_once_with(data)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
