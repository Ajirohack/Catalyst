"""Database Migration Script
Migrates existing Catalyst data to the new unified schema
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
import logging
from pathlib import Path

# Import the unified models
from unified_models import (
    User, UserProfile, Project, Conversation, Message, Analysis,
    ProjectStatus, ProjectType, RelationshipStage, UserRole,
    AnalysisType, MessagePlatform
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handles migration from old schema to unified schema"""
    
    def __init__(self, old_db_path: str = None, new_db_path: str = None):
        self.old_db_path = old_db_path or "catalyst_old.db"
        self.new_db_path = new_db_path or "catalyst_unified.db"
        self.backup_dir = Path("migration_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> str:
        """Create backup of existing data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"catalyst_backup_{timestamp}.json"
        
        try:
            # Export existing data to JSON
            existing_data = self.export_existing_data()
            
            with open(backup_file, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            logger.info(f"Backup created: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def export_existing_data(self) -> Dict[str, Any]:
        """Export existing data from current database"""
        data = {
            "projects": [],
            "analyses": [],
            "conversations": [],
            "messages": [],
            "metadata": {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0"
            }
        }
        
        # Since Catalyst currently uses in-memory storage,
        # we'll check for any existing data files
        try:
            # Check for any existing project data files
            project_files = list(Path(".").glob("*projects*.json"))
            for file_path in project_files:
                try:
                    with open(file_path, 'r') as f:
                        file_data = json.load(f)
                        if isinstance(file_data, list):
                            data["projects"].extend(file_data)
                        elif isinstance(file_data, dict) and "projects" in file_data:
                            data["projects"].extend(file_data["projects"])
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
            
            # Check for analysis data
            analysis_files = list(Path(".").glob("*analysis*.json"))
            for file_path in analysis_files:
                try:
                    with open(file_path, 'r') as f:
                        file_data = json.load(f)
                        if isinstance(file_data, list):
                            data["analyses"].extend(file_data)
                        elif isinstance(file_data, dict) and "analyses" in file_data:
                            data["analyses"].extend(file_data["analyses"])
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
            
            logger.info(f"Exported {len(data['projects'])} projects and {len(data['analyses'])} analyses")
            
        except Exception as e:
            logger.warning(f"Error during data export: {e}")
        
        return data
    
    def create_unified_schema(self) -> None:
        """Create the new unified database schema"""
        try:
            conn = sqlite3.connect(self.new_db_path)
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'user',
                    first_name TEXT,
                    last_name TEXT,
                    age INTEGER,
                    subscription_type TEXT DEFAULT 'free',
                    subscription_expires TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    therapist_id TEXT,
                    coach_id TEXT,
                    therapy_goals TEXT, -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    preferences TEXT, -- JSON object
                    metadata TEXT -- JSON object
                )
            """)
            
            # Create User Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    relationship_status TEXT,
                    relationship_stage TEXT,
                    relationship_duration_months INTEGER,
                    partner_name TEXT,
                    communication_style TEXT,
                    preferred_platforms TEXT, -- JSON array
                    relationship_goals TEXT, -- JSON array
                    personal_goals TEXT, -- JSON array
                    therapy_objectives TEXT, -- JSON array
                    attachment_style TEXT,
                    communication_assessment TEXT, -- JSON object
                    personality_traits TEXT, -- JSON object
                    data_sharing_consent BOOLEAN DEFAULT FALSE,
                    analysis_consent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT DEFAULT 'other',
                    status TEXT DEFAULT 'active',
                    owner_id TEXT NOT NULL,
                    participants TEXT, -- JSON array
                    therapist_id TEXT,
                    coach_id TEXT,
                    relationship_stage TEXT,
                    relationship_duration_months INTEGER,
                    goals TEXT, -- JSON array
                    milestones TEXT, -- JSON array
                    success_metrics TEXT, -- JSON object
                    analysis_frequency TEXT DEFAULT 'weekly',
                    auto_analysis_enabled BOOLEAN DEFAULT TRUE,
                    real_time_coaching_enabled BOOLEAN DEFAULT FALSE,
                    is_private BOOLEAN DEFAULT TRUE,
                    sharing_permissions TEXT, -- JSON object
                    total_conversations INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    total_analyses INTEGER DEFAULT 0,
                    last_activity TIMESTAMP,
                    settings TEXT, -- JSON object
                    notification_preferences TEXT, -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (id)
                )
            """)
            
            # Create Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    platform TEXT DEFAULT 'generic',
                    participants TEXT, -- JSON array
                    file_path TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    file_format TEXT,
                    message_count INTEGER DEFAULT 0,
                    character_count INTEGER DEFAULT 0,
                    date_range_start TIMESTAMP,
                    date_range_end TIMESTAMP,
                    processing_status TEXT DEFAULT 'pending',
                    processing_error TEXT,
                    analysis_summary TEXT, -- JSON object
                    last_analysis_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    timestamp TIMESTAMP NOT NULL,
                    platform TEXT,
                    platform_message_id TEXT,
                    sentiment_score REAL,
                    emotion_tags TEXT, -- JSON array
                    analysis_metadata TEXT, -- JSON object
                    is_processed BOOLEAN DEFAULT FALSE,
                    needs_attention BOOLEAN DEFAULT FALSE,
                    flagged_content BOOLEAN DEFAULT FALSE,
                    metadata TEXT, -- JSON object
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Create Analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    conversation_id TEXT,
                    user_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_depth TEXT DEFAULT 'standard',
                    overall_score REAL NOT NULL,
                    confidence_score REAL DEFAULT 0.8,
                    sentiment_analysis TEXT, -- JSON object
                    communication_patterns TEXT, -- JSON object
                    emotional_analysis TEXT, -- JSON object
                    relationship_insights TEXT, -- JSON object
                    pattern_analysis TEXT, -- JSON object
                    key_insights TEXT, -- JSON array
                    positive_indicators TEXT, -- JSON array
                    red_flags TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    therapy_suggestions TEXT, -- JSON array
                    intervention_recommendations TEXT, -- JSON array
                    conversation_metrics TEXT, -- JSON object
                    participant_analysis TEXT, -- JSON object
                    ai_provider TEXT,
                    ai_model TEXT,
                    processing_time_seconds REAL,
                    raw_data TEXT, -- JSON object
                    metadata TEXT, -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Therapeutic Interventions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS therapeutic_interventions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    analysis_id TEXT,
                    user_id TEXT NOT NULL,
                    therapist_id TEXT,
                    intervention_type TEXT NOT NULL,
                    therapy_approach TEXT NOT NULL,
                    urgency_level TEXT DEFAULT 'medium',
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    exercises TEXT, -- JSON array
                    resources TEXT, -- JSON array
                    delivery_method TEXT DEFAULT 'in_app',
                    is_delivered BOOLEAN DEFAULT FALSE,
                    delivered_at TIMESTAMP,
                    is_acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_at TIMESTAMP,
                    user_feedback TEXT,
                    effectiveness_rating INTEGER,
                    requires_follow_up BOOLEAN DEFAULT FALSE,
                    follow_up_date TIMESTAMP,
                    follow_up_completed BOOLEAN DEFAULT FALSE,
                    metadata TEXT, -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Real-time Coaching table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS real_time_coaching (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    trigger_message TEXT NOT NULL,
                    trigger_platform TEXT NOT NULL,
                    trigger_context TEXT, -- JSON object
                    suggestion TEXT NOT NULL,
                    urgency TEXT DEFAULT 'low',
                    confidence REAL DEFAULT 0.8,
                    alternatives TEXT, -- JSON array
                    is_viewed BOOLEAN DEFAULT FALSE,
                    viewed_at TIMESTAMP,
                    user_action TEXT,
                    user_feedback TEXT,
                    was_helpful BOOLEAN,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    target_value REAL,
                    current_value REAL,
                    unit TEXT,
                    target_date TIMESTAMP,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_completed BOOLEAN DEFAULT FALSE,
                    completed_date TIMESTAMP,
                    progress_percentage REAL DEFAULT 0.0,
                    milestones TEXT, -- JSON array
                    progress_updates TEXT, -- JSON array
                    priority INTEGER DEFAULT 3,
                    tags TEXT, -- JSON array
                    metadata TEXT, -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT, -- JSON object
                    summary TEXT,
                    analysis_ids TEXT, -- JSON array
                    conversation_ids TEXT, -- JSON array
                    date_range_start TIMESTAMP,
                    date_range_end TIMESTAMP,
                    generation_status TEXT DEFAULT 'pending',
                    generation_error TEXT,
                    file_path TEXT,
                    file_format TEXT DEFAULT 'pdf',
                    is_shared BOOLEAN DEFAULT FALSE,
                    shared_with TEXT, -- JSON array
                    access_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    generated_at TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id)",
                "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_analyses_project ON analyses(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(analysis_type)",
                "CREATE INDEX IF NOT EXISTS idx_interventions_project ON therapeutic_interventions(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_coaching_project ON real_time_coaching(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_goals_project ON goals(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_reports_project ON reports(project_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Unified database schema created: {self.new_db_path}")
            
        except Exception as e:
            logger.error(f"Schema creation failed: {e}")
            raise
    
    def migrate_existing_data(self, backup_data: Dict[str, Any]) -> None:
        """Migrate existing data to new schema"""
        try:
            conn = sqlite3.connect(self.new_db_path)
            cursor = conn.cursor()
            
            # Create default admin user if no users exist
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                admin_user = {
                    "id": str(uuid.uuid4()),
                    "email": "admin@catalyst.ai",
                    "username": "admin",
                    "role": "admin",
                    "first_name": "System",
                    "last_name": "Administrator",
                    "subscription_type": "premium",
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "preferences": json.dumps({}),
                    "metadata": json.dumps({"migrated": True})
                }
                
                cursor.execute("""
                    INSERT INTO users (id, email, username, role, first_name, last_name, 
                                     subscription_type, is_active, created_at, updated_at, 
                                     preferences, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    admin_user["id"], admin_user["email"], admin_user["username"],
                    admin_user["role"], admin_user["first_name"], admin_user["last_name"],
                    admin_user["subscription_type"], admin_user["is_active"],
                    admin_user["created_at"], admin_user["updated_at"],
                    admin_user["preferences"], admin_user["metadata"]
                ))
                
                logger.info("Created default admin user")
            
            # Migrate projects
            for project_data in backup_data.get("projects", []):
                try:
                    # Get admin user ID for ownership
                    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                    admin_id = cursor.fetchone()[0]
                    
                    migrated_project = {
                        "id": project_data.get("id", str(uuid.uuid4())),
                        "name": project_data.get("name", "Migrated Project"),
                        "description": project_data.get("description", ""),
                        "project_type": project_data.get("type", "other"),
                        "status": project_data.get("status", "active"),
                        "owner_id": admin_id,
                        "participants": json.dumps(project_data.get("participants", [])),
                        "goals": json.dumps(project_data.get("goals", [])),
                        "milestones": json.dumps(project_data.get("milestones", [])),
                        "settings": json.dumps(project_data.get("settings", {})),
                        "created_at": project_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO projects 
                        (id, name, description, project_type, status, owner_id, participants, 
                         goals, milestones, settings, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        migrated_project["id"], migrated_project["name"], 
                        migrated_project["description"], migrated_project["project_type"],
                        migrated_project["status"], migrated_project["owner_id"],
                        migrated_project["participants"], migrated_project["goals"],
                        migrated_project["milestones"], migrated_project["settings"],
                        migrated_project["created_at"], migrated_project["updated_at"]
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate project {project_data.get('id', 'unknown')}: {e}")
            
            # Migrate analyses
            for analysis_data in backup_data.get("analyses", []):
                try:
                    # Get admin user and first project for analysis
                    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                    admin_id = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT id FROM projects LIMIT 1")
                    project_result = cursor.fetchone()
                    if not project_result:
                        continue
                    project_id = project_result[0]
                    
                    migrated_analysis = {
                        "id": analysis_data.get("id", str(uuid.uuid4())),
                        "project_id": project_id,
                        "user_id": admin_id,
                        "analysis_type": analysis_data.get("type", "comprehensive"),
                        "overall_score": analysis_data.get("overall_score", 0.5),
                        "confidence_score": analysis_data.get("confidence", 0.8),
                        "sentiment_analysis": json.dumps(analysis_data.get("sentiment", {})),
                        "key_insights": json.dumps(analysis_data.get("insights", [])),
                        "recommendations": json.dumps(analysis_data.get("recommendations", [])),
                        "raw_data": json.dumps(analysis_data),
                        "created_at": analysis_data.get("created_at", datetime.now(timezone.utc).isoformat())
                    }
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO analyses 
                        (id, project_id, user_id, analysis_type, overall_score, confidence_score,
                         sentiment_analysis, key_insights, recommendations, raw_data, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        migrated_analysis["id"], migrated_analysis["project_id"],
                        migrated_analysis["user_id"], migrated_analysis["analysis_type"],
                        migrated_analysis["overall_score"], migrated_analysis["confidence_score"],
                        migrated_analysis["sentiment_analysis"], migrated_analysis["key_insights"],
                        migrated_analysis["recommendations"], migrated_analysis["raw_data"],
                        migrated_analysis["created_at"]
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate analysis {analysis_data.get('id', 'unknown')}: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info("Data migration completed successfully")
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            raise
    
    def run_migration(self) -> str:
        """Run the complete migration process"""
        try:
            logger.info("Starting database migration...")
            
            # Step 1: Create backup
            backup_file = self.create_backup()
            
            # Step 2: Load backup data
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Step 3: Create new schema
            self.create_unified_schema()
            
            # Step 4: Migrate data
            self.migrate_existing_data(backup_data)
            
            logger.info(f"Migration completed successfully. New database: {self.new_db_path}")
            return self.new_db_path
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify the migration was successful"""
        try:
            conn = sqlite3.connect(self.new_db_path)
            cursor = conn.cursor()
            
            verification = {
                "database_file": self.new_db_path,
                "tables": {},
                "total_records": 0,
                "verification_time": datetime.now(timezone.utc).isoformat()
            }
            
            tables = [
                "users", "user_profiles", "projects", "conversations", "messages",
                "analyses", "therapeutic_interventions", "real_time_coaching",
                "goals", "reports"
            ]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                verification["tables"][table] = count
                verification["total_records"] += count
            
            conn.close()
            
            logger.info(f"Migration verification completed: {verification['total_records']} total records")
            return verification
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            raise

def main():
    """Main migration function"""
    try:
        migration = DatabaseMigration()
        
        # Run migration
        new_db_path = migration.run_migration()
        
        # Verify migration
        verification = migration.verify_migration()
        
        print("\n" + "="*50)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"New database: {new_db_path}")
        print(f"Total records migrated: {verification['total_records']}")
        print("\nTable counts:")
        for table, count in verification["tables"].items():
            print(f"  {table}: {count}")
        print("\nNext steps:")
        print("1. Update your application configuration to use the new database")
        print("2. Test the application with the migrated data")
        print("3. Archive the old database files once verified")
        
    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")
        print("Please check the logs for more details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())