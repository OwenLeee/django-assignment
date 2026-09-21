from django.contrib import admin

from .models import Category, Product, Tag

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
