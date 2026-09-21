from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase

from catalog.models import Category, Product

from .helpers import create_category, create_product


class ProductCategoryRelationshipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = create_category()
        cls.product = create_product(category=cls.category)

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


class ProductNameTests(SimpleTestCase):
    def validate(self, product):
        product.full_clean(
            validate_unique=False,
            validate_constraints=False,
            exclude=["description", "category"],
        )

    def test_name_is_trimmed_and_case_is_preserved(self):
        product = Product(
            name="  400A Panelboard  ",
        )

        self.validate(product)
        self.assertEqual(product.name, "400A Panelboard")

    def test_whitespace_only_name_is_rejected(self):
        product = Product(name="   ")

        with self.assertRaises(ValidationError) as context:
            self.validate(product)
        self.assertIn("name", context.exception.message_dict)

    def test_name_length_limit_applies_after_trimming(self):
        product = Product(name=f"  {'A' * 100}  ")

        self.validate(product)
        self.assertEqual(product.name, "A" * 100)

        product.name = "A" * 101

        with self.assertRaises(ValidationError) as context:
            self.validate(product)
        self.assertIn("name", context.exception.message_dict)
