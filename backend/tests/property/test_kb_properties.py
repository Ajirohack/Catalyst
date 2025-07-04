"""
Property-based tests for Knowledge Base operations
"""
import pytest
from hypothesis import given, strategies as st
import asyncio
from typing import List, Dict, Any

from services.knowledge_base import KnowledgeBaseService, DocumentType

# Custom Hypothesis strategies
@st.composite
def document_content(draw):
    """Generate valid document content"""
    return draw(st.text(
        alphabet=st.characters(blacklist_categories=('Cs',)),  # Exclude surrogate characters
        min_size=1,
        max_size=1000000  # 1MB max
    ))

@st.composite
def document_metadata(draw):
    """Generate valid document metadata"""
    return {
        "title": draw(st.text(min_size=1, max_size=200)),
        "type": draw(st.sampled_from([t.value for t in DocumentType])),
        "tags": draw(st.lists(
            st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=10
        )),
        "metadata": draw(st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(
                st.text(),
                st.integers(),
                st.floats(allow_infinity=False, allow_nan=False),
                st.booleans()
            ),
            max_size=10
        ))
    }

class TestKnowledgeBaseProperties:
    @pytest.fixture
    async def property_test_service(self, temp_storage):
        """Create a service instance for property testing."""
        service = KnowledgeBaseService(storage_path=str(temp_storage))
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    @given(
        content=document_content(),
        metadata=document_metadata()
    )
    async def test_document_indexing_properties(self, property_test_service, content, metadata):
        """Test document indexing with property-based input"""
        # Index the document
        result = await property_test_service.index_document(
            content=content,
            title=metadata["title"],
            doc_type=metadata["type"],
            tags=metadata["tags"]
        )

        # Properties that should always hold
        assert "document_id" in result
        assert "success" in result
        assert isinstance(result["success"], bool)
        
        if result["success"]:
            # Properties for successful indexing
            assert len(result["document_id"]) > 0
            
            # Retrieve the document and verify properties
            doc = await property_test_service.get_document(result["document_id"])
            assert doc is not None
            assert doc.title == metadata["title"]
            assert doc.document_type.value == metadata["type"]
            assert set(doc.tags) == set(metadata["tags"])
            
            # Search should find the document
            search_results = await property_test_service.search(
                query=metadata["title"],
                limit=10
            )
            assert any(r.document_id == result["document_id"] for r in search_results)

    @pytest.mark.asyncio
    @given(
        queries=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=5
        )
    )
    async def test_search_properties(self, property_test_service, queries):
        """Test search operation properties"""
        for query in queries:
            results = await property_test_service.search(query=query, limit=10)
            
            # Properties that should always hold for search results
            assert isinstance(results, list)
            assert len(results) <= 10  # Respects limit
            
            if results:
                # Properties for non-empty results
                for result in results:
                    assert 0 <= result.similarity_score <= 1  # Scores are normalized
                    assert result.document_id  # Has valid document ID
                    assert result.content  # Has content
                    
                # Results should be sorted by similarity score
                scores = [r.similarity_score for r in results]
                assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    @given(
        batch_size=st.integers(min_value=1, max_value=10),
        content=st.lists(document_content(), min_size=1, max_size=10)
    )
    async def test_batch_processing_properties(self, property_test_service, batch_size, content):
        """Test batch processing properties"""
        async def process_batch(docs):
            tasks = []
            for doc in docs:
                task = property_test_service.index_document(
                    content=doc,
                    title=f"Batch Doc {len(tasks)}",
                    doc_type=DocumentType.REFERENCE.value,
                    tags=["batch", "test"]
                )
                tasks.append(task)
            return await asyncio.gather(*tasks)

        # Process documents in batches
        results = []
        for i in range(0, len(content), batch_size):
            batch = content[i:i + batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)

        # Properties that should hold for batch processing
        assert len(results) == len(content)  # All documents processed
        assert all("document_id" in r for r in results)  # All have IDs
        
        # No duplicate IDs should be generated
        doc_ids = [r["document_id"] for r in results]
        assert len(doc_ids) == len(set(doc_ids))

    @pytest.mark.asyncio
    @given(
        original=document_content(),
        update=document_content()
    )
    async def test_document_update_properties(self, property_test_service, original, update):
        """Test document update properties"""
        # Index original document
        orig_result = await property_test_service.index_document(
            content=original,
            title="Original Doc",
            doc_type=DocumentType.REFERENCE.value,
            tags=["original"]
        )

        if orig_result["success"]:
            doc_id = orig_result["document_id"]
            
            # Update the document
            update_result = await property_test_service.update_document(
                document_id=doc_id,
                content=update,
                title="Updated Doc",
                tags=["updated"]
            )

            # Properties that should hold after update
            assert update_result["success"]
            assert update_result["document_id"] == doc_id  # ID remains same
            
            # Get updated document
            updated_doc = await property_test_service.get_document(doc_id)
            assert updated_doc is not None
            assert updated_doc.title == "Updated Doc"
            assert "updated" in updated_doc.tags
            
            # Original content should not be findable
            orig_search = await property_test_service.search(query=original, limit=1)
            assert not any(r.document_id == doc_id for r in orig_search)
            
            # Updated content should be findable
            update_search = await property_test_service.search(query=update, limit=1)
            assert any(r.document_id == doc_id for r in update_search)
