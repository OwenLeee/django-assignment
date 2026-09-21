from django.contrib import admin

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
        "category",
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

    @admin.display(description="Tags")
    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    # Overriding get_queryset: Solving the N+1 query problem by prefetching related tags for products in the admin list view
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")
