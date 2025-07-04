"""Migration: Add Enhanced User Profiles
# VERSION: 1.0
# DESCRIPTION: Create advanced_user_profiles table with comprehensive relationship and therapy data
# CREATED: 2024-12-28T00:00:00
"""

# SQL_START
CREATE TABLE IF NOT EXISTS advanced_user_profiles (
    user_id TEXT PRIMARY KEY,
    
    -- Profile completion
    completion_status TEXT DEFAULT 'incomplete' CHECK (completion_status IN ('incomplete', 'basic', 'intermediate', 'complete', 'verified')),
    completion_percentage REAL DEFAULT 0.0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    last_profile_update TIMESTAMP,
    
    -- Basic profile info (inherited from UserProfile)
    relationship_status TEXT,
    relationship_stage TEXT CHECK (relationship_stage IN ('dating', 'committed', 'engaged', 'married', 'long_term', 'complicated', 'separated', 'divorced', 'unknown')),
    relationship_duration_months INTEGER CHECK (relationship_duration_months >= 0),
    partner_name TEXT,
    
    -- Communication preferences
    communication_style TEXT,
    preferred_platforms TEXT, -- JSON array
    
    -- Goals and objectives
    relationship_goals TEXT, -- JSON array
    personal_goals TEXT, -- JSON array
    therapy_objectives TEXT, -- JSON array
    
    -- Expanded relationship information
    relationship_history TEXT, -- JSON array
    previous_therapy_experience TEXT, -- JSON array
    current_challenges TEXT, -- JSON array
    
    -- Detailed assessments
    attachment_assessment TEXT, -- JSON object
    communication_style_assessment TEXT, -- JSON object
    conflict_resolution_style TEXT, -- JSON object
    love_languages TEXT, -- JSON object
    personality_assessment TEXT, -- JSON object
    
    -- Mental health and wellness
    stress_levels TEXT, -- JSON object
    emotional_regulation TEXT, -- JSON object
    trigger_patterns TEXT, -- JSON array
    coping_strategies TEXT, -- JSON array
    
    -- Therapy and coaching preferences
    preferred_intervention_style TEXT,
    therapy_approach_preferences TEXT, -- JSON array
    communication_preferences TEXT, -- JSON object
    boundary_preferences TEXT, -- JSON object
    
    -- Progress tracking
    milestone_achievements TEXT, -- JSON array
    skill_improvements TEXT, -- JSON object
    relationship_satisfaction_history TEXT, -- JSON array
    
    -- Emergency contacts and support system
    emergency_contacts TEXT, -- JSON array
    support_network TEXT, -- JSON object
    crisis_plan TEXT, -- JSON object
    
    -- Professional connections
    assigned_professionals TEXT, -- JSON object (role -> professional_id)
    professional_notes TEXT, -- JSON object (professional_id -> notes)
    
    -- Privacy and consent
    data_sharing_consent BOOLEAN DEFAULT FALSE,
    analysis_consent BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (if users table exists)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_advanced_profiles_completion ON advanced_user_profiles(completion_status, completion_percentage);
CREATE INDEX IF NOT EXISTS idx_advanced_profiles_relationship ON advanced_user_profiles(relationship_stage, relationship_status);
CREATE INDEX IF NOT EXISTS idx_advanced_profiles_updated ON advanced_user_profiles(updated_at);

-- SQL_END

# ROLLBACK_START
DROP INDEX IF EXISTS idx_advanced_profiles_updated;
DROP INDEX IF EXISTS idx_advanced_profiles_relationship;
DROP INDEX IF EXISTS idx_advanced_profiles_completion;
DROP TABLE IF EXISTS advanced_user_profiles;
# ROLLBACK_END
