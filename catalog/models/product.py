from django.core.validators import MaxLengthValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        max_length=2000, validators=[MaxLengthValidator(2000)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT
    )  # Protecting the category from being deleted if there are products associated with it

    tags = models.ManyToManyField(
        "Tag", related_name="products", blank=True
    )  # Allowing products to have no or multiple tags and tags to be associated with multiple products

    def clean_fields(self, exclude=None):
        if (exclude is None or "name" not in exclude) and isinstance(self.name, str):
            self.name = self.name.strip()

        if (exclude is None or "description" not in exclude) and isinstance(
            self.description, str
        ):
            self.description = self.description.strip()

        super().clean_fields(exclude=exclude)

    def save(self, **kwargs):
        self.clean_fields()
        return super().save(**kwargs)

    def __str__(self):
        return self.name
