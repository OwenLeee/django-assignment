from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT
    )  # Protecting the category from being deleted if there are products associated with it

    def clean_fields(self, exclude=None):
        if (exclude is None or "name" not in exclude) and isinstance(self.name, str):
            self.name = self.name.strip()
        super().clean_fields(exclude=exclude)

    def save(self, **kwargs):
        self.clean_fields()
        return super().save(**kwargs)

    def __str__(self):
        return self.name
