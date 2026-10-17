# Config package
# Compatibility patch for Python 3.14+ where super().__copy__ behavior changed
try:
    from django.template.context import BaseContext

    def _basecontext_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _basecontext_copy
except Exception:
    pass
