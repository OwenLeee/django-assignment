from django.db import IntegrityError, transaction
from django.test import TestCase

from catalog.models import Product, Tag

from .helpers import create_category, create_product, create_tag


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

    def test_removing_tag_preserves_product_and_tags(self):
        product = create_product()
        tag_to_remove = create_tag(name="Tag to Remove")
        tag_to_keep = create_tag(name="Tag to Keep")

        product.tags.add(tag_to_remove, tag_to_keep)

        # Verify that both tags are associated with the product before removal
        self.assertEqual(product.tags.count(), 2)

        product.tags.remove(tag_to_remove)

        # Verify that the tag was removed and the other tag is still associated
        self.assertEqual(product.tags.count(), 1)
        self.assertIn(tag_to_keep, product.tags.all())

        # Verify product, tag_to_remove, and tag_to_keep still exist in the database
        self.assertTrue(Product.objects.filter(id=product.id).exists())
        self.assertTrue(Tag.objects.filter(id=tag_to_remove.id).exists())
        self.assertTrue(Tag.objects.filter(id=tag_to_keep.id).exists())

    def test_deleting_product_cleans_relationships_and_preserves_tags(self):
        category = create_category()
        tag = create_tag()
        product_to_delete = create_product(category=category)
        product_to_delete.tags.add(tag)
        product_to_keep = create_product(category=category)
        product_to_keep.tags.add(tag)

        ProductTag = Product.tags.through

        product_to_delete_pk = product_to_delete.pk

        product_to_delete.delete()

        # Verify product_to_delete is removed from the database
        self.assertFalse(Product.objects.filter(pk=product_to_delete_pk).exists())

        # Verify product_to_delete and that tag associated with it is not in the association table
        self.assertFalse(
            ProductTag.objects.filter(
                tag_id=tag.pk, product_id=product_to_delete_pk
            ).exists()
        )

        # Verify product_to_keep and tag are still in the database and associated
        self.assertTrue(Product.objects.filter(pk=product_to_keep.pk).exists())
        self.assertTrue(Tag.objects.filter(pk=tag.pk).exists())
        self.assertTrue(
            ProductTag.objects.filter(
                tag_id=tag.pk, product_id=product_to_keep.pk
            ).exists()
        )

    def test_deleting_tag_cleans_relationships_and_preserves_products(self):
        product = create_product()
        tag_to_delete = create_tag(name="Tag to Delete")
        tag_to_keep = create_tag(name="Tag to Keep")
        product.tags.add(tag_to_delete)
        product.tags.add(tag_to_keep)
        ProductTag = Product.tags.through

        # Verify that the product and tags are associated before deletion
        self.assertEqual(product.tags.count(), 2)

        tag_to_delete_pk = tag_to_delete.pk
        tag_to_delete.delete()

        # Verify that the tag_to_delete is removed from the database
        self.assertFalse(Tag.objects.filter(pk=tag_to_delete_pk).exists())

        # Verify that the tag_to_keep is kept in the database
        self.assertTrue(Tag.objects.filter(pk=tag_to_keep.pk).exists())

        # Verify that the product is still in the database
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())

        # Verify that the tag_to_delete is no longer associated with the product
        self.assertFalse(
            ProductTag.objects.filter(
                tag_id=tag_to_delete_pk, product_id=product.pk
            ).exists()
        )

        # Verify that the tag_to_keep is still associated with the product
        self.assertTrue(
            ProductTag.objects.filter(
                tag_id=tag_to_keep.pk, product_id=product.pk
            ).exists()
        )
