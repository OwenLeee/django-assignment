def create_category(name="Electrical Distribution"):
    from catalog.models import Category

    return Category.objects.create(name=name)


def create_product(
    name="400A Panelboard",
    description="400A panelboard for commercial power distribution, planned as a major equipment purchase.",
    category=None,
):
    from catalog.models import Product

    if category is None:
        category = create_category()

    return Product.objects.create(
        name=name,
        description=description,
        category=category,
    )


def create_tag(name="Commercial"):
    from catalog.models import Tag

    return Tag.objects.create(name=name)
