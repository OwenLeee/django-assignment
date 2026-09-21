from django.db import models
from django.db.models.functions import Lower


class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name_plural = "tags"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="catalog_tag_name_ci_unique",
                violation_error_message="A tag with this name already exists.",
            ),
        ]

    def clean_fields(self, exclude=None):
        if (exclude is None or "name" not in exclude) and isinstance(self.name, str):
            self.name = self.name.strip()
        super().clean_fields(exclude=exclude)

    def save(self, **kwargs):
        self.clean_fields()
        return super().save(**kwargs)

    def __str__(self):
        return self.name
