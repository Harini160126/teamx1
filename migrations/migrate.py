"""
Database Migration System for PyTech Arena
This script handles database schema migrations.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import *  # Import all models

class Migration:
    """Base migration class."""
    
    def __init__(self, version, description):
        self.version = version
        self.description = description
        self.created_at = datetime.utcnow()
    
    def up(self):
        """Apply the migration."""
        raise NotImplementedError
    
    def down(self):
        """Rollback the migration."""
        raise NotImplementedError


class Migration001_AddCompanyModel(Migration):
    """Add Company model to database."""
    
    def __init__(self):
        super().__init__("001", "Add Company model")
    
    def up(self):
        """Create Company table."""
        Company.__table__.create(db.engine, checkfirst=True)
        print(f"Applied migration {self.version}: {self.description}")
    
    def down(self):
        """Drop Company table."""
        Company.__table__.drop(db.engine, checkfirst=True)
        print(f"Rolled back migration {self.version}: {self.description}")


class Migration002_AddJobPostingModel(Migration):
    """Add JobPosting model to database."""
    
    def __init__(self):
        super().__init__("002", "Add JobPosting model")
    
    def up(self):
        """Create JobPosting table."""
        JobPosting.__table__.create(db.engine, checkfirst=True)
        print(f"Applied migration {self.version}: {self.description}")
    
    def down(self):
        """Drop JobPosting table."""
        JobPosting.__table__.drop(db.engine, checkfirst=True)
        print(f"Rolled back migration {self.version}: {self.description}")


class Migration003_AddNotificationModel(Migration):
    """Add Notification model to database."""
    
    def __init__(self):
        super().__init__("003", "Add Notification model")
    
    def up(self):
        """Create Notification table."""
        Notification.__table__.create(db.engine, checkfirst=True)
        print(f"Applied migration {self.version}: {self.description}")
    
    def down(self):
        """Drop Notification table."""
        Notification.__table__.drop(db.engine, checkfirst=True)
        print(f"Rolled back migration {self.version}: {self.description}")


class Migration004_AddPlacementDriveModel(Migration):
    """Add PlacementDrive model to database."""
    
    def __init__(self):
        super().__init__("004", "Add PlacementDrive model")
    
    def up(self):
        """Create PlacementDrive and association tables."""
        PlacementDrive.__table__.create(db.engine, checkfirst=True)
        drive_companies.create(db.engine, checkfirst=True)
        print(f"Applied migration {self.version}: {self.description}")
    
    def down(self):
        """Drop PlacementDrive and association tables."""
        drive_companies.drop(db.engine, checkfirst=True)
        PlacementDrive.__table__.drop(db.engine, checkfirst=True)
        print(f"Rolled back migration {self.version}: {self.description}")


# List of all migrations
MIGRATIONS = [
    Migration001_AddCompanyModel(),
    Migration002_AddJobPostingModel(),
    Migration003_AddNotificationModel(),
    Migration004_AddPlacementDriveModel(),
]


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        os.makedirs(self.migrations_dir, exist_ok=True)
        self.migration_file = os.path.join(self.migrations_dir, 'applied_migrations.txt')
    
    def get_applied_migrations(self):
        """Get list of applied migrations."""
        if not os.path.exists(self.migration_file):
            return []
        
        with open(self.migration_file, 'r') as f:
            return [line.strip() for line in f.readlines()]
    
    def mark_migration_applied(self, version):
        """Mark a migration as applied."""
        with open(self.migration_file, 'a') as f:
            f.write(f"{version}\n")
    
    def mark_migration_rolled_back(self, version):
        """Mark a migration as rolled back."""
        applied = self.get_applied_migrations()
        if version in applied:
            applied.remove(version)
            with open(self.migration_file, 'w') as f:
                for v in applied:
                    f.write(f"{v}\n")
    
    def migrate(self):
        """Apply all pending migrations."""
        applied = self.get_applied_migrations()
        
        with app.app_context():
            for migration in MIGRATIONS:
                if migration.version not in applied:
                    try:
                        migration.up()
                        self.mark_migration_applied(migration.version)
                    except Exception as e:
                        print(f"Error applying migration {migration.version}: {str(e)}")
                        break
    
    def rollback(self, target_version=None):
        """Rollback migrations."""
        applied = self.get_applied_migrations()
        
        if target_version:
            # Rollback to specific version
            to_rollback = [m for m in MIGRATIONS if m.version in applied and m.version > target_version]
        else:
            # Rollback last migration
            if applied:
                last_version = applied[-1]
                to_rollback = [m for m in MIGRATIONS if m.version == last_version]
            else:
                to_rollback = []
        
        with app.app_context():
            for migration in reversed(to_rollback):
                try:
                    migration.down()
                    self.mark_migration_rolled_back(migration.version)
                except Exception as e:
                    print(f"Error rolling back migration {migration.version}: {str(e)}")
                    break
    
    def status(self):
        """Show migration status."""
        applied = self.get_applied_migrations()
        
        print("Migration Status:")
        print("=" * 50)
        
        for migration in MIGRATIONS:
            status = "Applied" if migration.version in applied else "Pending"
            print(f"{migration.version}: {migration.description} - {status}")
        
        print("=" * 50)
        print(f"Applied: {len(applied)}/{len(MIGRATIONS)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status'], 
                       help='Migration command')
    parser.add_argument('--version', help='Target version for rollback')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.command == 'migrate':
        manager.migrate()
    elif args.command == 'rollback':
        manager.rollback(args.version)
    elif args.command == 'status':
        manager.status()
