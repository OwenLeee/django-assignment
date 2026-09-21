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

    def test_product_cannot_be_created_without_category(self):
        product = Product(
            name="400A Panelboard",
            description="400A panelboard for commercial power distribution",
            category=None,
        )
        product_count_before = Product.objects.count()

        with self.assertRaises(ValidationError) as context:
            product.save()

        product_count_after = Product.objects.count()
        self.assertEqual(product_count_before, product_count_after)
        self.assertIn("category", context.exception.message_dict)

    def test_products_can_share_the_same_name(self):
        product1 = create_product(name="Shared Name", category=self.category)
        product2 = create_product(name="Shared Name", category=self.category)

        self.assertEqual(product1.name, product2.name)
        self.assertNotEqual(product1.pk, product2.pk)
        self.assertEqual(Product.objects.filter(name="Shared Name").count(), 2)


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


class ProductNameSaveTests(TestCase):
    def test_create_stores_trimmed_name(self):
        product = create_product(name="  400A Panelboard  ")
        product.refresh_from_db()

        self.assertEqual(product.name, "400A Panelboard")

    def test_save_rejects_whitespace_only_name(self):
        product = Product(
            name="   ", description="Test description", category=create_category()
        )

        with self.assertRaises(ValidationError):
            product.save()
        self.assertEqual(Product.objects.count(), 0)


class ProductDescriptionTests(SimpleTestCase):
    def validate(self, product):
        product.full_clean(
            validate_unique=False,
            validate_constraints=False,
            exclude=["name", "category"],
        )

    def test_description_is_trimmed_and_case_is_preserved(self):
        product = Product(
            description="  400A panelboard for commercial power distribution  ",
        )

        self.validate(product)
        self.assertEqual(
            product.description, "400A panelboard for commercial power distribution"
        )

    def test_whitespace_only_description_is_rejected(self):
        test_cases = ["", "    ", "\n\t"]

        for test_case in test_cases:
            with self.subTest(description=test_case):
                product = Product(description=test_case)

                with self.assertRaises(ValidationError) as context:
                    self.validate(product)
                self.assertIn("description", context.exception.message_dict)

    def test_description_length_limit_applies_after_trimming(self):
        product = Product(description=f"  {'A' * 2000}  ")

        self.validate(product)
        self.assertEqual(product.description, "A" * 2000)

        product.description = "A" * 2001

        with self.assertRaises(ValidationError) as context:
            self.validate(product)
        self.assertIn("description", context.exception.message_dict)

    def test_description_preserves_internal_whitespace(self):
        product = Product(
            description="  400A panelboard for commercial power distribution\n, planned as a major  equipment purchase.  "
        )

        self.validate(product)
        self.assertEqual(
            product.description,
            "400A panelboard for commercial power distribution\n, planned as a major  equipment purchase.",
        )


class ProductDescriptionSaveTests(TestCase):
    def test_create_stores_trimmed_description(self):
        product = create_product(
            description="  400A panelboard for commercial power distribution\n, planned as a major  equipment purchase.  "
        )
        product.refresh_from_db()

        self.assertEqual(
            product.description,
            "400A panelboard for commercial power distribution\n, planned as a major  equipment purchase.",
        )

    def test_save_rejects_invalid_description(self):
        descriptions = ["   ", "A" * 2001]
        category = create_category()

        for description in descriptions:
            with self.subTest(description=description):
                product = Product(
                    name="Test Product",
                    description=description,
                    category=category,
                )

                with self.assertRaises(ValidationError) as context:
                    product.save()
                self.assertEqual(Product.objects.count(), 0)
                self.assertIn("description", context.exception.message_dict)
