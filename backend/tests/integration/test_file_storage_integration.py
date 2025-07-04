"""
Integration tests for the file storage functionality.
These tests interact with the actual file system to verify real storage operations.
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from uuid import uuid4

# Add the backend directory to the Python path
import sys
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from services.file_service import FileService
from services.storage_service import StorageService


@pytest.fixture(scope="module")
def test_storage_dir():
    """Create a temporary directory for testing file storage operations."""
    temp_dir = tempfile.mkdtemp(prefix="catalyst_test_storage_")
    yield temp_dir
    # Clean up after tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage_service(test_storage_dir):
    """Create a StorageService instance with the test storage directory."""
    service = StorageService(base_dir=test_storage_dir)
    return service


@pytest.fixture
def file_service(storage_service):
    """Create a FileService instance with the test storage service."""
    service = FileService(storage_service=storage_service)
    return service


class TestFileStorageIntegration:
    """Integration tests for file storage functionality."""

    def test_save_and_retrieve_text_file(self, file_service, test_storage_dir):
        """Test saving and retrieving a text file."""
        # Setup
        content = "This is a test file content for integration testing."
        file_id = str(uuid4())
        file_path = os.path.join("test_project", "conversations", f"{file_id}.txt")

        # Execute: Save file
        saved_path = file_service.save_file(
            content=content.encode(),
            file_path=file_path,
            metadata={"content_type": "text/plain"}
        )

        # Verify file exists on disk
        full_path = os.path.join(test_storage_dir, file_path)
        assert os.path.exists(full_path), f"File not found at {full_path}"

        # Execute: Retrieve file
        retrieved_content = file_service.get_file(file_path)

        # Verify content matches
        assert retrieved_content.decode() == content, "Retrieved content doesn't match original"

        # Cleanup
        os.remove(full_path)

    def test_file_metadata_persistence(self, file_service, test_storage_dir):
        """Test that file metadata is properly saved and retrieved."""
        # Setup
        content = "Test content with metadata"
        file_id = str(uuid4())
        file_path = os.path.join("test_project", "documents", f"{file_id}.txt")
        metadata = {
            "content_type": "text/plain",
            "author": "Test Author",
            "created_date": "2023-01-01",
            "tags": ["test", "integration", "metadata"]
        }

        # Execute: Save file with metadata
        saved_path = file_service.save_file(
            content=content.encode(),
            file_path=file_path,
            metadata=metadata
        )

        # Verify metadata file exists
        metadata_path = os.path.join(test_storage_dir, f"{file_path}.meta")
        assert os.path.exists(metadata_path), f"Metadata file not found at {metadata_path}"

        # Execute: Retrieve metadata
        retrieved_metadata = file_service.get_file_metadata(file_path)

        # Verify metadata matches
        for key, value in metadata.items():
            assert key in retrieved_metadata, f"Metadata key '{key}' not found"
            assert retrieved_metadata[key] == value, f"Metadata value for '{key}' doesn't match"

        # Cleanup
        full_path = os.path.join(test_storage_dir, file_path)
        os.remove(full_path)
        os.remove(metadata_path)

    def test_list_files_in_directory(self, file_service, test_storage_dir):
        """Test listing files in a directory."""
        # Setup: Create multiple files
        directory = os.path.join("test_project", "multiple_files")
        base_path = os.path.join(test_storage_dir, directory)
        os.makedirs(base_path, exist_ok=True)
        
        # Create 5 test files
        test_files = []
        for i in range(5):
            file_name = f"test_file_{i}.txt"
            file_path = os.path.join(directory, file_name)
            content = f"Content for test file {i}"
            file_service.save_file(
                content=content.encode(),
                file_path=file_path,
                metadata={"index": i}
            )
            test_files.append(file_name)
        
        # Execute: List files
        files = file_service.list_files(directory)
        
        # Verify all files are listed
        for file_name in test_files:
            assert file_name in [os.path.basename(f) for f in files], f"File {file_name} not found in listing"
        
        # Cleanup
        shutil.rmtree(base_path)

    def test_large_file_handling(self, file_service, test_storage_dir):
        """Test handling of larger files (5MB)."""
        # Setup: Create a 5MB file
        large_content = b"x" * (5 * 1024 * 1024)  # 5MB of data
        file_path = os.path.join("test_project", "large_file.bin")
        
        # Execute: Save large file
        start_time = time.time()
        saved_path = file_service.save_file(
            content=large_content,
            file_path=file_path,
            metadata={"size": "5MB", "type": "binary"}
        )
        save_time = time.time() - start_time
        
        # Log performance
        print(f"Time to save 5MB file: {save_time:.2f} seconds")
        
        # Execute: Retrieve large file
        start_time = time.time()
        retrieved_content = file_service.get_file(file_path)
        retrieve_time = time.time() - start_time
        
        # Log performance
        print(f"Time to retrieve 5MB file: {retrieve_time:.2f} seconds")
        
        # Verify content integrity
        assert len(retrieved_content) == len(large_content), "Retrieved content size doesn't match original"
        assert retrieved_content == large_content, "Retrieved content doesn't match original"
        
        # Verify performance is reasonable
        assert save_time < 1.0, f"File save operation took too long: {save_time:.2f} seconds"
        assert retrieve_time < 1.0, f"File retrieve operation took too long: {retrieve_time:.2f} seconds"
        
        # Cleanup
        full_path = os.path.join(test_storage_dir, file_path)
        os.remove(full_path)

    def test_concurrent_file_operations(self, file_service, test_storage_dir):
        """Test concurrent file operations using asyncio."""
        import asyncio
        import concurrent.futures
        
        # Setup
        base_dir = os.path.join("test_project", "concurrent")
        num_files = 20
        
        async def save_and_retrieve_file(index):
            """Save and retrieve a file asynchronously."""
            file_name = f"concurrent_file_{index}.txt"
            file_path = os.path.join(base_dir, file_name)
            content = f"Content for concurrent file {index}".encode()
            
            # Save file
            saved_path = file_service.save_file(
                content=content,
                file_path=file_path,
                metadata={"index": index}
            )
            
            # Retrieve file
            retrieved_content = file_service.get_file(file_path)
            
            # Verify content
            assert retrieved_content == content, f"Content mismatch for file {index}"
            
            return file_path
        
        # Execute: Run concurrent operations
        async def run_concurrent_ops():
            tasks = [save_and_retrieve_file(i) for i in range(num_files)]
            return await asyncio.gather(*tasks)
        
        # Run the async operations
        loop = asyncio.get_event_loop()
        start_time = time.time()
        file_paths = loop.run_until_complete(run_concurrent_ops())
        total_time = time.time() - start_time
        
        # Log performance
        print(f"Time to process {num_files} files concurrently: {total_time:.2f} seconds")
        print(f"Average time per file: {total_time/num_files:.4f} seconds")
        
        # Verify performance is reasonable
        assert total_time < num_files * 0.1, f"Concurrent operations took too long: {total_time:.2f} seconds"
        
        # Cleanup
        for file_path in file_paths:
            full_path = os.path.join(test_storage_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
