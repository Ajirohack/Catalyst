"""Migration: Add Progress Tracking
# VERSION: 1.0
# DESCRIPTION: Create progress_tracking table for comprehensive progress monitoring
# CREATED: 2024-12-28T00:00:00
"""

# SQL_START
CREATE TABLE IF NOT EXISTS progress_tracking (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    
    -- Tracking period
    tracking_period TEXT DEFAULT 'monthly' CHECK (tracking_period IN ('daily', 'weekly', 'monthly', 'quarterly')),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    -- Relationship health metrics
    overall_relationship_score REAL DEFAULT 0.0 CHECK (overall_relationship_score >= 0 AND overall_relationship_score <= 10),
    communication_score REAL DEFAULT 0.0 CHECK (communication_score >= 0 AND communication_score <= 10),
    emotional_intimacy_score REAL DEFAULT 0.0 CHECK (emotional_intimacy_score >= 0 AND emotional_intimacy_score <= 10),
    conflict_resolution_score REAL DEFAULT 0.0 CHECK (conflict_resolution_score >= 0 AND conflict_resolution_score <= 10),
    satisfaction_score REAL DEFAULT 0.0 CHECK (satisfaction_score >= 0 AND satisfaction_score <= 10),
    
    -- Individual progress metrics
    personal_growth_indicators TEXT, -- JSON object
    skill_development TEXT, -- JSON object
    goal_achievement TEXT, -- JSON object
    
    -- Behavioral changes
    communication_improvements TEXT, -- JSON array
    negative_patterns_reduced TEXT, -- JSON array
    positive_patterns_increased TEXT, -- JSON array
    
    -- Therapy engagement
    session_attendance_rate REAL DEFAULT 0.0 CHECK (session_attendance_rate >= 0 AND session_attendance_rate <= 100),
    homework_completion_rate REAL DEFAULT 0.0 CHECK (homework_completion_rate >= 0 AND homework_completion_rate <= 100),
    intervention_engagement TEXT, -- JSON object
    
    -- Milestone tracking
    milestones_achieved TEXT, -- JSON array
    milestones_pending TEXT, -- JSON array
    
    -- Risk factors and protective factors
    risk_factors TEXT, -- JSON array
    protective_factors TEXT, -- JSON array
    
    -- Comparative analysis
    previous_period_comparison TEXT, -- JSON object
    trend_analysis TEXT, -- JSON object
    
    -- Predictive indicators
    future_risk_indicators TEXT, -- JSON array
    recommended_focus_areas TEXT, -- JSON array
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_progress_tracking_user ON progress_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_project ON progress_tracking(project_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_period ON progress_tracking(tracking_period, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_scores ON progress_tracking(overall_relationship_score, communication_score);

-- SQL_END

# ROLLBACK_START
DROP INDEX IF EXISTS idx_progress_tracking_scores;
DROP INDEX IF EXISTS idx_progress_tracking_period;
DROP INDEX IF EXISTS idx_progress_tracking_project;
DROP INDEX IF EXISTS idx_progress_tracking_user;
DROP TABLE IF EXISTS progress_tracking;
# ROLLBACK_END
