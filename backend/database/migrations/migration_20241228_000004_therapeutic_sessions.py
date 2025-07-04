"""Migration: Add Therapeutic Session Tracking
# VERSION: 1.0
# DESCRIPTION: Create therapeutic_sessions table for comprehensive session management
# CREATED: 2024-12-28T00:00:00
"""

# SQL_START
CREATE TABLE IF NOT EXISTS therapeutic_sessions (
    id TEXT PRIMARY KEY,
    
    -- Session identification
    session_number INTEGER NOT NULL CHECK (session_number >= 1),
    session_type TEXT NOT NULL CHECK (session_type IN ('individual', 'couples', 'family', 'group', 'crisis', 'follow_up', 'assessment', 'consultation')),
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', 'rescheduled')),
    
    -- Participants
    primary_user_id TEXT NOT NULL,
    participant_ids TEXT, -- JSON array
    therapist_id TEXT NOT NULL,
    observer_ids TEXT, -- JSON array
    
    -- Session details
    project_id TEXT NOT NULL,
    session_title TEXT NOT NULL,
    session_goals TEXT, -- JSON array
    
    -- Scheduling
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    duration_minutes INTEGER,
    
    -- Session content
    therapy_approach TEXT NOT NULL CHECK (therapy_approach IN ('cognitive_behavioral', 'emotionally_focused', 'gottman_method', 'solution_focused', 'narrative_therapy', 'systemic_therapy', 'mindfulness_based')),
    interventions_used TEXT, -- JSON array
    exercises_completed TEXT, -- JSON array
    
    -- Pre-session data
    pre_session_mood TEXT, -- JSON object
    pre_session_goals TEXT, -- JSON array
    pre_session_concerns TEXT, -- JSON array
    
    -- Session notes and observations
    therapist_notes TEXT DEFAULT '',
    client_feedback TEXT DEFAULT '',
    session_dynamics TEXT, -- JSON object
    breakthrough_moments TEXT, -- JSON array
    
    -- Assessments and measurements
    pre_session_assessments TEXT, -- JSON object
    post_session_assessments TEXT, -- JSON object
    progress_indicators TEXT, -- JSON object
    
    -- Homework and follow-up
    homework_assigned TEXT, -- JSON array
    homework_completion TEXT, -- JSON object
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP,
    
    -- Crisis and risk assessment
    crisis_risk_level TEXT DEFAULT 'low' CHECK (crisis_risk_level IN ('low', 'medium', 'high', 'critical')),
    safety_plan_updated BOOLEAN DEFAULT FALSE,
    emergency_contacts_verified BOOLEAN DEFAULT FALSE,
    
    -- Outcomes and effectiveness
    session_effectiveness INTEGER CHECK (session_effectiveness >= 1 AND session_effectiveness <= 10),
    client_satisfaction INTEGER CHECK (client_satisfaction >= 1 AND client_satisfaction <= 10),
    therapeutic_alliance_score REAL CHECK (therapeutic_alliance_score >= 0 AND therapeutic_alliance_score <= 10),
    
    -- Next session planning
    next_session_focus TEXT DEFAULT '',
    recommended_interventions TEXT, -- JSON array
    preparation_needed TEXT, -- JSON array
    
    -- Documentation and compliance
    consent_obtained BOOLEAN DEFAULT TRUE,
    documentation_complete BOOLEAN DEFAULT FALSE,
    billing_code TEXT,
    
    -- Session recording and analysis
    recording_consent BOOLEAN DEFAULT FALSE,
    recording_path TEXT,
    analysis_results TEXT, -- JSON object
    
    -- Metadata
    metadata TEXT, -- JSON object
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (primary_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (therapist_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_user ON therapeutic_sessions(primary_user_id);
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_therapist ON therapeutic_sessions(therapist_id);
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_project ON therapeutic_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_status ON therapeutic_sessions(status);
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_scheduled ON therapeutic_sessions(scheduled_start);
CREATE INDEX IF NOT EXISTS idx_therapeutic_sessions_type ON therapeutic_sessions(session_type, therapy_approach);

-- SQL_END

# ROLLBACK_START
DROP INDEX IF EXISTS idx_therapeutic_sessions_type;
DROP INDEX IF EXISTS idx_therapeutic_sessions_scheduled;
DROP INDEX IF EXISTS idx_therapeutic_sessions_status;
DROP INDEX IF EXISTS idx_therapeutic_sessions_project;
DROP INDEX IF EXISTS idx_therapeutic_sessions_therapist;
DROP INDEX IF EXISTS idx_therapeutic_sessions_user;
DROP TABLE IF EXISTS therapeutic_sessions;
# ROLLBACK_END
