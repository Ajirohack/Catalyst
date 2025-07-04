"""
Performance benchmark tests for Knowledge Base operations
"""
import pytest
import time
import psutil
import asyncio
from datetime import datetime
from pathlib import Path

from services.knowledge_base import KnowledgeBaseService, DocumentType

def get_process_memory():
    """Get current process memory usage in bytes"""
    process = psutil.Process()
    return process.memory_info().rss

class TestKnowledgeBasePerformance:
    @pytest.fixture
    async def benchmark_service(self, temp_storage):
        """Create a service instance for benchmarking."""
        service = KnowledgeBaseService(storage_path=str(temp_storage))
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_indexing_performance(self, benchmark_service, sample_knowledge_doc, performance_thresholds):
        """Benchmark document indexing performance"""
        # Prepare test data
        docs_to_index = 100
        start_memory = get_process_memory()
        results = []
        
        start_time = time.time()
        
        # Index multiple documents
        for i in range(docs_to_index):
            doc = sample_knowledge_doc.copy()
            doc["title"] = f"Benchmark Doc {i}"
            result = await benchmark_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            results.append(result)
        
        total_time = time.time() - start_time
        memory_used = get_process_memory() - start_memory
        
        # Performance assertions
        assert total_time < performance_thresholds["indexing"]["max_time"] * (docs_to_index / 10)
        assert memory_used < performance_thresholds["indexing"]["max_memory"]
        
        # Calculate and print metrics
        avg_time_per_doc = total_time / docs_to_index
        memory_per_doc = memory_used / docs_to_index
        
        print(f"\nIndexing Performance Metrics:")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per document: {avg_time_per_doc:.3f}s")
        print(f"Memory used: {memory_used / 1024 / 1024:.1f}MB")
        print(f"Average memory per document: {memory_per_doc / 1024:.1f}KB")

    @pytest.mark.asyncio
    async def test_search_performance(self, benchmark_service, sample_knowledge_doc, performance_thresholds):
        """Benchmark search performance"""
        # Index some test documents first
        docs_to_index = 1000
        index_tasks = []
        
        # Prepare and index documents
        for i in range(docs_to_index):
            doc = sample_knowledge_doc.copy()
            doc["title"] = f"Search Benchmark Doc {i}"
            doc["content"] = f"This is test content for document {i}. " * 10
            task = benchmark_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            index_tasks.append(task)
        
        await asyncio.gather(*index_tasks)
        
        # Perform search benchmarks
        search_queries = [
            "test content",
            "benchmark doc",
            "nonexistent term",
            "document 500",
            "this is test"
        ]
        
        start_memory = get_process_memory()
        search_times = []
        
        for query in search_queries:
            start_time = time.time()
            results = await benchmark_service.search(query=query, limit=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        memory_used = get_process_memory() - start_memory
        avg_search_time = sum(search_times) / len(search_times)
        
        # Performance assertions
        assert avg_search_time < performance_thresholds["search"]["max_time"]
        assert memory_used < performance_thresholds["search"]["max_memory"]
        
        print(f"\nSearch Performance Metrics:")
        print(f"Average search time: {avg_search_time:.3f}s")
        print(f"Memory used: {memory_used / 1024 / 1024:.1f}MB")
        print(f"95th percentile search time: {sorted(search_times)[int(len(search_times) * 0.95)]:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_performance(self, benchmark_service, sample_knowledge_doc, performance_thresholds):
        """Benchmark concurrent operation performance"""
        concurrent_operations = 50
        
        async def concurrent_operation(i):
            # Perform a mix of operations
            start_time = time.time()
            
            # Index a document
            doc = sample_knowledge_doc.copy()
            doc["title"] = f"Concurrent Doc {i}"
            index_result = await benchmark_service.index_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["type"],
                tags=doc["tags"]
            )
            
            # Perform a search
            search_result = await benchmark_service.search(
                query=f"concurrent doc {i}",
                limit=5
            )
            
            return time.time() - start_time
        
        start_memory = get_process_memory()
        start_time = time.time()
        
        # Run concurrent operations
        tasks = [concurrent_operation(i) for i in range(concurrent_operations)]
        operation_times = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        memory_used = get_process_memory() - start_memory
        
        # Calculate metrics
        avg_operation_time = sum(operation_times) / len(operation_times)
        max_operation_time = max(operation_times)
        throughput = concurrent_operations / total_time
        
        print(f"\nConcurrent Performance Metrics:")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average operation time: {avg_operation_time:.3f}s")
        print(f"Max operation time: {max_operation_time:.3f}s")
        print(f"Throughput: {throughput:.1f} operations/second")
        print(f"Memory used: {memory_used / 1024 / 1024:.1f}MB")
        
        # Performance assertions
        assert avg_operation_time < 1.0  # Each operation should complete within 1 second on average
        assert throughput > 10.0  # Should handle at least 10 operations per second
