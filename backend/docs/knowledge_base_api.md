# Knowledge Base API Documentation

## Overview

The Knowledge Base API provides endpoints for managing documents, performing semantic search, and handling document metadata such as tags and categories.

## Base URL

`/api/knowledge-base`

## Authentication

All endpoints require authentication. Include your API token in the Authorization header:

```
Authorization: Bearer your-api-token
```

## Endpoints

### Document Management

#### Upload Document

Upload a new document to the knowledge base.

- **URL**: `/documents/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): The document file to upload (supported formats: PDF, DOCX, TXT, images)
  - `tags` (optional): Comma-separated list of tags
  - `category` (optional): Document category
  - `auto_tag` (optional): Enable automatic tagging (default: true)
  - `auto_categorize` (optional): Enable automatic categorization (default: true)

**Response**:

```json
{
  "document_id": "string",
  "filename": "string",
  "status": "string",
  "message": "string",
  "chunks_created": 0,
  "auto_tags": ["string"],
  "auto_category": "string"
}
```

#### List Documents

Get a list of documents in the knowledge base.

- **URL**: `/documents`
- **Method**: `GET`
- **Query Parameters**:
  - `skip` (optional): Number of documents to skip (default: 0)
  - `limit` (optional): Maximum number of documents to return (default: 100, max: 1000)
  - `category` (optional): Filter by category
  - `tags` (optional): Filter by tags (comma-separated)
  - `search_query` (optional): Text search in document titles/content

**Response**:

```json
[
  {
    "document_id": "string",
    "filename": "string",
    "title": "string",
    "content_type": "string",
    "file_size": 0,
    "document_type": "string",
    "category": "string",
    "tags": ["string"],
    "chunk_count": 0,
    "created_at": "string",
    "updated_at": "string",
    "status": "string"
  }
]
```

#### Get Document

Get detailed information about a specific document.

- **URL**: `/documents/{document_id}`
- **Method**: `GET`
- **URL Parameters**:
  - `document_id` (required): The ID of the document to retrieve

**Response**:

```json
{
  "document_id": "string",
  "filename": "string",
  "title": "string",
  "content_type": "string",
  "file_size": 0,
  "document_type": "string",
  "category": "string",
  "tags": ["string"],
  "chunk_count": 0,
  "created_at": "string",
  "updated_at": "string",
  "status": "string",
  "content": "string"
}
```

#### Delete Document

Delete a document from the knowledge base.

- **URL**: `/documents/{document_id}`
- **Method**: `DELETE`
- **URL Parameters**:
  - `document_id` (required): The ID of the document to delete

**Response**:

```json
{
  "message": "Document deleted successfully",
  "document_id": "string"
}
```

#### Update Document Tags

Update tags for a specific document.

- **URL**: `/documents/{document_id}/tags`
- **Method**: `POST`
- **URL Parameters**:
  - `document_id` (required): The ID of the document to update
- **Request Body**:

```json
{
  "tags": ["string"],
  "replace": true
}
```

**Response**:

```json
{
  "message": "Tags updated successfully",
  "document_id": "string"
}
```

#### Download Document

Download the original document file.

- **URL**: `/documents/{document_id}/download`
- **Method**: `GET`
- **URL Parameters**:
  - `document_id` (required): The ID of the document to download

**Response**: The document file with appropriate Content-Type header.

### Search

#### Semantic Search

Perform semantic search across the knowledge base.

- **URL**: `/search`
- **Method**: `POST`
- **Request Body**:

```json
{
  "query": "string",
  "limit": 10,
  "threshold": 0.7,
  "filters": {
    "category": "string",
    "tags": ["string"],
    "document_type": "string",
    "status": "string",
    "created_after": "string",
    "created_before": "string",
    "search_query": "string"
  },
  "include_content": true
}
```

**Response**:

```json
{
  "query": "string",
  "results": [
    {
      "document_id": "string",
      "chunk_id": "string",
      "content": "string",
      "score": 0.95,
      "metadata": {
        "title": "string",
        "tags": ["string"],
        "document_type": "string",
        "category": "string"
      }
    }
  ],
  "total_results": 0,
  "execution_time": 0.05
}
```

### Metadata

#### List Categories

Get all available document categories.

- **URL**: `/categories`
- **Method**: `GET`

**Response**:

```json
{
  "categories": ["string"]
}
```

#### List Tags

Get all available document tags.

- **URL**: `/tags`
- **Method**: `GET`

**Response**:

```json
{
  "tags": ["string"]
}
```

### Analytics

#### Knowledge Base Analytics

Get analytics and statistics about the knowledge base.

- **URL**: `/analytics`
- **Method**: `GET`

**Response**:

```json
{
  "total_documents": 0,
  "total_size": 0,
  "document_types": {
    "pdf": 0,
    "docx": 0,
    "txt": 0,
    "image": 0
  },
  "category_count": 0,
  "tag_count": 0,
  "tag_usage": {
    "tag1": 10,
    "tag2": 5
  },
  "recent_activity": [
    {
      "type": "upload",
      "description": "Document uploaded: document.pdf",
      "timestamp": "string"
    }
  ]
}
```

### Maintenance

#### Reindex Knowledge Base

Reindex all documents in the knowledge base.

- **URL**: `/reindex`
- **Method**: `POST`

**Response**:

```json
{
  "task_id": "string",
  "status": "string",
  "message": "Reindexing started"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds maximum limit
- `500 Internal Server Error`: Server-side error

Error responses include a detailed message:

```json
{
  "detail": "Error message"
}
```

## Rate Limiting

API requests are rate-limited to 100 requests per minute per authenticated user.

## Supported Document Types

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain text (`.txt`)
- Images (`.jpg`, `.png`, `.gif`) with OCR support
