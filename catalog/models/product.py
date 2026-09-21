from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT
    )  # Protecting the category from being deleted if there are products associated with it

    def __str__(self):
        return self.name
