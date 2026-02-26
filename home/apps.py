from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # Monkey-patch django_tasks to avoid TypeError
        from django_tasks.backends import immediate

        original_setattr = immediate.TaskResult.__setattr__

        def safe_setattr(self, name, value):
            if name == "__orig_class__":
                return  # skip the problematic assignment
            return original_setattr(self, name, value)

        immediate.TaskResult.__setattr__ = safe_setattr