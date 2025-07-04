-- Catalyst Database Initialization Script
-- PostgreSQL initialization for Catalyst backend

-- Create database if it doesn't exist (handled by docker-compose environment)
-- This script runs after the database is created

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types/enums
CREATE TYPE project_status AS ENUM (
    'active', 'paused', 'completed', 'archived', 'on_hold'
);

CREATE TYPE project_type AS ENUM (
    'romantic', 'family', 'friendship', 'professional', 'therapy', 'coaching', 'other'
);

CREATE TYPE relationship_stage AS ENUM (
    'dating', 'committed', 'engaged', 'married', 'long_term', 
    'complicated', 'separated', 'divorced', 'unknown'
);

CREATE TYPE user_role AS ENUM (
    'user', 'premium', 'therapist', 'coach', 'admin'
);

CREATE TYPE analysis_type AS ENUM (
    'comprehensive', 'sentiment', 'communication_style', 'relationship_health',
    'conflict_detection', 'pattern_analysis', 'real_time', 'therapeutic', 'whisper'
);

CREATE TYPE message_platform AS ENUM (
    'whatsapp', 'messenger', 'discord', 'slack', 'teams', 'telegram',
    'sms', 'email', 'zoom', 'google_meet', 'instagram', 'facebook', 'generic'
);

CREATE TYPE intervention_type AS ENUM (
    'immediate_response', 'communication_coaching', 'conflict_resolution',
    'emotional_regulation', 'relationship_building', 'boundary_setting', 'crisis_intervention'
);

CREATE TYPE therapy_approach AS ENUM (
    'cognitive_behavioral', 'emotionally_focused', 'gottman_method',
    'solution_focused', 'narrative_therapy', 'systemic_therapy', 'mindfulness_based'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_analyses_project ON analyses(project_id);

-- Insert default AI providers
INSERT INTO ai_providers (id, name, provider_type, is_active, config) VALUES
    (uuid_generate_v4(), 'OpenAI GPT-4', 'openai', true, '{"model": "gpt-4", "max_tokens": 4000}'),
    (uuid_generate_v4(), 'OpenAI GPT-3.5 Turbo', 'openai', true, '{"model": "gpt-3.5-turbo", "max_tokens": 4000}'),
    (uuid_generate_v4(), 'Anthropic Claude', 'anthropic', true, '{"model": "claude-3-sonnet-20240229", "max_tokens": 4000}'),
    (uuid_generate_v4(), 'Local Ollama', 'ollama', false, '{"model": "llama2", "base_url": "http://localhost:11434"}')
ON CONFLICT (name) DO NOTHING;

-- Create default admin user (password should be changed in production)
-- Password: 'admin123' (hashed)
INSERT INTO users (id, email, username, role, first_name, last_name, is_active, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'admin@catalyst.local', 'admin', 'admin', 'System', 'Administrator', true, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO catalyst_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO catalyst_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO catalyst_user;

-- Create application-specific functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Catalyst database initialized successfully at %', NOW();
END $$;