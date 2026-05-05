"""
BackupRouter
============
Ensures that:
- All reads go to the primary (default) database
- Migrations run on BOTH databases so the backup schema stays in sync
- No automatic routing of writes to backup (signals handle that manually)
"""


class BackupRouter:
    BACKUP_DB = 'backup'

    def db_for_read(self, model, **hints):
        """Always read from the primary database."""
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Always write to the primary database.
        The backup receives writes via signals (sync/signals.py), not the router.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations within the same database."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Run migrations on both databases so the backup schema
        always matches the primary schema.
        """
        return True