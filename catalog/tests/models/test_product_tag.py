from django.test import TestCase

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
