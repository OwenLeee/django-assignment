from django.db.models.deletion import ProtectedError
from django.test import TestCase

from catalog.models import Category, Product


class ProductCategoryRelationshipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Electrical Distribution")
        cls.product = Product.objects.create(
            name="400A Panelboard",
            description="400A panelboard for commercial power distribution, planned as a major equipment purchase.",
            category=cls.category,
        )

    def test_product_category_id_is_equal_to_category_id(self):
        self.product.refresh_from_db()

        # use pk to ensure that the test is not dependent on the specific field name of the primary key
        self.assertEqual(
            self.product.category_id,
            self.category.pk,
        )

    def test_protect_category_deletion_when_products_exist(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

        # 1. Ensure the category still exists after the failed deletion attempt
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

        # 2. Ensure the product still exists after the failed deletion attempt
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
