from django.db import models


class SomeModel(models.Model):
    marker = models.CharField(max_length=10)

    def some_heavy_method(self, *args, **kwargs):
        return
