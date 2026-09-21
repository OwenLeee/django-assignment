from django.db import IntegrityError, transaction
from django.test import TestCase

from catalog.models import Product

from .helpers import create_category, create_product


class ProductTagTests(TestCase):
    def test_product_can_be_saved_without_tags(self):
        product = create_product()

        self.assertEqual(product.tags.count(), 0)

    def test_product_can_have_multiple_tags(self):
        product = create_product()

        tag1 = product.tags.create(name="Tag 1")
        tag2 = product.tags.create(name="Tag 2")

        self.assertEqual(product.tags.count(), 2)
        self.assertIn(tag1, product.tags.all())
        self.assertIn(tag2, product.tags.all())

    def test_tag_can_be_assigned_to_multiple_products(self):
        category = create_category()
        product1 = create_product(category=category)
        product2 = create_product(category=category)

        tag = product1.tags.create(name="Shared Tag")
        product2.tags.add(tag)

        self.assertIn(tag, product1.tags.all())
        self.assertIn(tag, product2.tags.all())

    def test_adding_same_tag_twice_does_not_duplicate_relationship(self):
        product = create_product()
        tag = product.tags.create(name="Unique Tag")

        product.tags.add(tag)

        self.assertEqual(product.tags.count(), 1)
        self.assertIn(tag, product.tags.all())

    def test_database_rejects_duplicate_product_tag_pair(self):
        product = create_product()
        tag = product.tags.create(name="Unique Tag")
        # Access Django's auto-generated junction model for direct database writes. If using add(), Django handles duplicates gracefully, but direct writes to the junction table will raise an IntegrityError for duplicates.
        ProductTag = Product.tags.through

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductTag.objects.create(product=product, tag=tag)
        self.assertEqual(product.tags.count(), 1)
