from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    verbose_name = 'PMS Integration'

    def ready(self):
        # Importing signals connects the receivers so booking status
        # transitions (confirmed / cancelled) push to the management system.
        from . import signals  # noqa: F401
