"""Migration Management System for Catalyst Database
Provides utilities for managing database schema migrations
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, db_path: str, migrations_dir: Optional[str] = None):
        """Initialize migration manager
        
        Args:
            db_path: Path to SQLite database file
            migrations_dir: Path to migrations directory
        """
        self.db_path = db_path
        self.migrations_dir = migrations_dir or os.path.join(os.path.dirname(__file__))
        self.migration_table = "schema_migrations"
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Initialize migration tracking table
        self._init_migration_table()
    
    def _init_migration_table(self):
        """Initialize the migration tracking table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.migration_table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_name TEXT UNIQUE NOT NULL,
                        version TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum TEXT,
                        metadata TEXT
                    )
                """)
                conn.commit()
                logger.info("Migration tracking table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize migration table: {e}")
            raise
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(f"""
                    SELECT migration_name, version, applied_at, checksum, metadata
                    FROM {self.migration_table}
                    ORDER BY applied_at
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        applied = {m["migration_name"] for m in self.get_applied_migrations()}
        available = self._get_available_migrations()
        return [m for m in available if m not in applied]
    
    def _get_available_migrations(self) -> List[str]:
        """Get list of available migration files"""
        migration_files = []
        try:
            for file in os.listdir(self.migrations_dir):
                if file.endswith('.py') and file.startswith('migration_'):
                    migration_files.append(file[:-3])  # Remove .py extension
            return sorted(migration_files)
        except Exception as e:
            logger.error(f"Failed to list migration files: {e}")
            return []
    
    def apply_migration(self, migration_name: str) -> bool:
        """Apply a specific migration
        
        Args:
            migration_name: Name of migration to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import and execute migration
            migration_path = os.path.join(self.migrations_dir, f"{migration_name}.py")
            if not os.path.exists(migration_path):
                logger.error(f"Migration file not found: {migration_path}")
                return False
            
            # Read migration content
            with open(migration_path, 'r') as f:
                migration_content = f.read()
            
            # Extract migration metadata
            migration_info = self._parse_migration_file(migration_content)
            
            with sqlite3.connect(self.db_path) as conn:
                # Execute migration SQL
                if migration_info.get('sql'):
                    conn.executescript(migration_info['sql'])
                
                # Record migration as applied
                conn.execute(f"""
                    INSERT INTO {self.migration_table} 
                    (migration_name, version, checksum, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    migration_name,
                    migration_info.get('version', '1.0'),
                    migration_info.get('checksum', ''),
                    json.dumps(migration_info.get('metadata', {}))
                ))
                
                conn.commit()
                logger.info(f"Applied migration: {migration_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_name}: {e}")
            return False
    
    def apply_all_pending(self) -> bool:
        """Apply all pending migrations
        
        Returns:
            True if all successful, False if any failed
        """
        pending = self.get_pending_migrations()
        if not pending:
            logger.info("No pending migrations")
            return True
        
        success = True
        for migration in pending:
            if not self.apply_migration(migration):
                success = False
                logger.error(f"Failed to apply migration: {migration}")
                break
            
        return success
    
    def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration (if rollback SQL is provided)
        
        Args:
            migration_name: Name of migration to rollback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read migration file to get rollback SQL
            migration_path = os.path.join(self.migrations_dir, f"{migration_name}.py")
            if not os.path.exists(migration_path):
                logger.error(f"Migration file not found: {migration_path}")
                return False
            
            with open(migration_path, 'r') as f:
                migration_content = f.read()
            
            migration_info = self._parse_migration_file(migration_content)
            
            if not migration_info.get('rollback_sql'):
                logger.error(f"No rollback SQL found for migration: {migration_name}")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                # Execute rollback SQL
                conn.executescript(migration_info['rollback_sql'])
                
                # Remove migration record
                conn.execute(f"""
                    DELETE FROM {self.migration_table}
                    WHERE migration_name = ?
                """, (migration_name,))
                
                conn.commit()
                logger.info(f"Rolled back migration: {migration_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_name}: {e}")
            return False
    
    def _parse_migration_file(self, content: str) -> Dict[str, Any]:
        """Parse migration file to extract metadata and SQL
        
        Args:
            content: Migration file content
            
        Returns:
            Dictionary with migration information
        """
        info = {
            'version': '1.0',
            'sql': '',
            'rollback_sql': '',
            'metadata': {}
        }
        
        # Extract SQL sections (simplified parser)
        lines = content.split('\n')
        current_section = None
        sql_lines = []
        rollback_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('# VERSION:'):
                info['version'] = line.split(':', 1)[1].strip()
            elif line.startswith('# DESCRIPTION:'):
                info['metadata']['description'] = line.split(':', 1)[1].strip()
            elif line == '# SQL_START':
                current_section = 'sql'
                continue
            elif line == '# SQL_END':
                current_section = None
                continue
            elif line == '# ROLLBACK_START':
                current_section = 'rollback'
                continue
            elif line == '# ROLLBACK_END':
                current_section = None
                continue
            elif current_section == 'sql' and not line.startswith('#'):
                sql_lines.append(line)
            elif current_section == 'rollback' and not line.startswith('#'):
                rollback_lines.append(line)
        
        info['sql'] = '\n'.join(sql_lines)
        info['rollback_sql'] = '\n'.join(rollback_lines)
        
        return info
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status
        
        Returns:
            Dictionary with migration status information
        """
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'total_migrations': len(self._get_available_migrations()),
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_migrations': applied,
            'pending_migrations': pending,
            'last_applied': applied[-1] if applied else None
        }
    
    def generate_migration_template(self, name: str, description: str = "") -> str:
        """Generate a migration file template
        
        Args:
            name: Migration name
            description: Migration description
            
        Returns:
            Path to generated migration file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"migration_{timestamp}_{name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        template = f'''"""Migration: {name}
# VERSION: 1.0
# DESCRIPTION: {description}
# CREATED: {datetime.now().isoformat()}
"""

# SQL_START
# Add your migration SQL here
# Example:
# CREATE TABLE new_table (
#     id TEXT PRIMARY KEY,
#     name TEXT NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# SQL_END

# ROLLBACK_START
# Add your rollback SQL here (optional)
# Example:
# DROP TABLE IF EXISTS new_table;

# ROLLBACK_END
'''
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        logger.info(f"Generated migration template: {filepath}")
        return filepath

# Utility functions
def create_migration_manager(db_path: Optional[str] = None) -> MigrationManager:
    """Create migration manager with default database path"""
    if db_path is None:
        # Default to database in current directory
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'catalyst.db')
    
    migrations_dir = os.path.join(os.path.dirname(__file__))
    return MigrationManager(db_path, migrations_dir)

def apply_all_migrations(db_path: Optional[str] = None) -> bool:
    """Apply all pending migrations"""
    manager = create_migration_manager(db_path)
    return manager.apply_all_pending()

def get_migration_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Get migration status"""
    manager = create_migration_manager(db_path)
    return manager.get_migration_status()

if __name__ == "__main__":
    # CLI interface for migration management
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration_manager.py <command> [args]")
        print("Commands:")
        print("  status - Show migration status")
        print("  apply - Apply all pending migrations")
        print("  create <name> [description] - Create new migration template")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = create_migration_manager()
    
    if command == "status":
        status = manager.get_migration_status()
        print(f"Total migrations: {status['total_migrations']}")
        print(f"Applied: {status['applied_count']}")
        print(f"Pending: {status['pending_count']}")
        
        if status['pending_migrations']:
            print("\nPending migrations:")
            for migration in status['pending_migrations']:
                print(f"  - {migration}")
    
    elif command == "apply":
        success = manager.apply_all_pending()
        if success:
            print("All migrations applied successfully")
        else:
            print("Some migrations failed")
            sys.exit(1)
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: python migration_manager.py create <name> [description]")
            sys.exit(1)
        
        name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        filepath = manager.generate_migration_template(name, description)
        print(f"Created migration template: {filepath}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
