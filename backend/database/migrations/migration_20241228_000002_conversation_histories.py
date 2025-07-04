"""Migration: Add Conversation History Tracking
# VERSION: 1.0
# DESCRIPTION: Create conversation_histories table for comprehensive conversation analysis
# CREATED: 2024-12-28T00:00:00
"""

# SQL_START
CREATE TABLE IF NOT EXISTS conversation_histories (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    
    -- Conversation metadata
    conversation_title TEXT NOT NULL,
    participants TEXT, -- JSON array
    platform TEXT CHECK (platform IN ('whatsapp', 'messenger', 'discord', 'slack', 'teams', 'telegram', 'sms', 'email', 'zoom', 'google_meet', 'instagram', 'facebook', 'generic')),
    
    -- Comprehensive statistics
    message_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    avg_message_length REAL DEFAULT 0.0,
    
    -- Temporal analysis
    conversation_duration_seconds INTEGER,
    most_active_periods TEXT, -- JSON array
    response_time_patterns TEXT, -- JSON object
    
    -- Communication patterns
    sentiment_trends TEXT, -- JSON array
    emotional_progression TEXT, -- JSON array
    communication_style_evolution TEXT, -- JSON object
    
    -- Relationship insights
    relationship_health_indicators TEXT, -- JSON object
    conflict_patterns TEXT, -- JSON array
    positive_interaction_patterns TEXT, -- JSON array
    
    -- Advanced analysis results
    topic_analysis TEXT, -- JSON object
    language_complexity TEXT, -- JSON object
    attachment_style_indicators TEXT, -- JSON object
    
    -- Version control and history
    analysis_version TEXT DEFAULT '1.0',
    previous_analyses TEXT, -- JSON array of analysis IDs
    reanalysis_triggers TEXT, -- JSON array
    
    -- Flags and alerts
    requires_attention BOOLEAN DEFAULT FALSE,
    crisis_indicators TEXT, -- JSON array
    intervention_triggers TEXT, -- JSON array
    
    -- Processing information
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_errors TEXT, -- JSON array
    last_processed_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_histories_conversation ON conversation_histories(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_histories_project ON conversation_histories(project_id);
CREATE INDEX IF NOT EXISTS idx_conversation_histories_user ON conversation_histories(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_histories_status ON conversation_histories(processing_status, requires_attention);
CREATE INDEX IF NOT EXISTS idx_conversation_histories_updated ON conversation_histories(updated_at);

-- SQL_END

# ROLLBACK_START
DROP INDEX IF EXISTS idx_conversation_histories_updated;
DROP INDEX IF EXISTS idx_conversation_histories_status;
DROP INDEX IF EXISTS idx_conversation_histories_user;
DROP INDEX IF EXISTS idx_conversation_histories_project;
DROP INDEX IF EXISTS idx_conversation_histories_conversation;
DROP TABLE IF EXISTS conversation_histories;
# ROLLBACK_END
