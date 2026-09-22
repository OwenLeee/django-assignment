from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html, format_html_join

from .models import Category, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "display_category",
        "display_tags",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "description",
    )
    list_filter = ("category", "tags")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Product Information",
            {"fields": ("name", "description")},
        ),
        ("Classification", {"fields": ("category", "tags")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    formfield_overrides = {
        models.ManyToManyField: {"widget": forms.CheckboxSelectMultiple}
    }

    list_select_related = ("category",)

    @admin.display(description="Tags")
    def display_tags(self, obj):
        return format_html_join(
            " ",
            '<span style="color: #006B75; background-color: #E6F3F4; '
            "padding: 2px 8px; border-radius: 999px; display: inline-block; "
            'margin: 2px 0; overflow-wrap: anywhere;">{}</span>',
            ((tag.name,) for tag in obj.tags.all()),
        )

    @admin.display(description="Category", ordering="category")
    def display_category(self, obj):
        return format_html(
            '<span style="color: #111111; background-color: #F2F2F2; '
            "padding: 2px 8px; border-radius: 999px; display: inline-block; "
            'margin: 2px 0; overflow-wrap: anywhere;">{}</span>',
            obj.category,
        )

    # Overriding get_queryset: Solving the N+1 query problem by prefetching related tags for products in the admin list view
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")
