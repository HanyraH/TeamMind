from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Пользователи'

    def ready(self):
        """Python 3.14 compatibility patch for Django template BaseContext.__copy__."""
        try:
            from django.template import context
            def patched_copy(self):
                duplicate = self.__class__.__new__(self.__class__)
                duplicate.__dict__.update(self.__dict__)
                duplicate.dicts = self.dicts[:]
                return duplicate
            context.BaseContext.__copy__ = patched_copy
        except Exception:
            pass
