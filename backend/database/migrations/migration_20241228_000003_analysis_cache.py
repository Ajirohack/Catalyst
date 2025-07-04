"""Migration: Add Analysis Results Caching
# VERSION: 1.0
# DESCRIPTION: Create analysis_cache table for efficient caching of analysis results
# CREATED: 2024-12-28T00:00:00
"""

# SQL_START
CREATE TABLE IF NOT EXISTS analysis_cache (
    id TEXT PRIMARY KEY,
    cache_key TEXT UNIQUE NOT NULL,
    
    -- Related entities
    project_id TEXT NOT NULL,
    conversation_id TEXT,
    analysis_id TEXT,
    user_id TEXT NOT NULL,
    
    -- Cache metadata
    cache_type TEXT NOT NULL,
    data_version TEXT DEFAULT '1.0',
    content_hash TEXT NOT NULL,
    
    -- Cached data
    cached_result TEXT NOT NULL, -- JSON
    result_summary TEXT DEFAULT '',
    
    -- Cache status and validation
    status TEXT DEFAULT 'fresh' CHECK (status IN ('fresh', 'stale', 'expired', 'invalid')),
    confidence_score REAL DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    validation_checksum TEXT NOT NULL,
    
    -- Expiration and refresh
    expires_at TIMESTAMP NOT NULL,
    refresh_after TIMESTAMP NOT NULL,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    
    -- Performance metrics
    generation_time_ms REAL DEFAULT 0.0,
    retrieval_time_ms REAL DEFAULT 0.0,
    hit_count INTEGER DEFAULT 0,
    
    -- Dependencies and invalidation
    dependencies TEXT, -- JSON array of cache keys
    invalidation_triggers TEXT, -- JSON array
    
    -- AI metadata
    ai_provider TEXT,
    ai_model TEXT,
    processing_parameters TEXT, -- JSON object
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_analysis_cache_key ON analysis_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_project ON analysis_cache(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_type ON analysis_cache(cache_type, status);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_expires ON analysis_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_accessed ON analysis_cache(last_accessed);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_hash ON analysis_cache(content_hash);

-- SQL_END

# ROLLBACK_START
DROP INDEX IF EXISTS idx_analysis_cache_hash;
DROP INDEX IF EXISTS idx_analysis_cache_accessed;
DROP INDEX IF EXISTS idx_analysis_cache_expires;
DROP INDEX IF EXISTS idx_analysis_cache_type;
DROP INDEX IF EXISTS idx_analysis_cache_project;
DROP INDEX IF EXISTS idx_analysis_cache_key;
DROP TABLE IF EXISTS analysis_cache;
# ROLLBACK_END
