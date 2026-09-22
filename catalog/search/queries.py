from catalog.models import Product


def search_products(q="", category=None, tags=None, tag_mode="all"):
    product_queryset = Product.objects.all()

    if q != "":
        product_queryset = product_queryset.filter(description__icontains=q)

    if category is not None:
        product_queryset = product_queryset.filter(category=category)

    if tags:
        match tag_mode:
            case "any":
                product_queryset = product_queryset.filter(tags__in=tags).distinct()
            case "all":
                for tag in tags:
                    product_queryset = product_queryset.filter(tags=tag)

    return product_queryset.select_related("category").prefetch_related("tags")
