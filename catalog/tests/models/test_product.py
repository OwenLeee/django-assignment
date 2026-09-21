from django.db.models.deletion import ProtectedError
from django.test import TestCase

from catalog.models import Category, Product


class ProductCategoryRelationshipTests(TestCase):
    def test_product_category_id_is_equal_to_category_id(self):
        category = Category.objects.create(name="Electrical Distribution")
        product = Product.objects.create(
            name="400A Panelboard",
            description="400A panelboard for commercial power distribution, planned as a major equipment purchase.",
            category=category,
        )
        product.refresh_from_db()

        # use pk to ensure that the test is not dependent on the specific field name of the primary key
        self.assertEqual(
            product.category_id,
            category.pk,
        )

    def test_protect_category_deletion_when_products_exist(self):
        category = Category.objects.create(name="Electrical Distribution")
        product = Product.objects.create(
            name="400A Panelboard",
            description="400A panelboard for commercial power distribution, planned as a major equipment purchase.",
            category=category,
        )

        with self.assertRaises(ProtectedError):
            category.delete()

        # 1. Ensure the category still exists after the failed deletion attempt
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())

        # 2. Ensure the product still exists after the failed deletion attempt
        self.assertTrue(Product.objects.filter(id=product.id).exists())
