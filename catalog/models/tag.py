from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name_plural = "tags"

    def clean_fields(self, exclude=None):
        if (exclude is None or "name" not in exclude) and isinstance(self.name, str):
            self.name = self.name.strip()
        super().clean_fields(exclude=exclude)

    def __str__(self):
        return self.name
