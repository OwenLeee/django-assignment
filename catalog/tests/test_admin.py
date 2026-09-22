from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from catalog.models import Product
from catalog.tests.models.helpers import create_category, create_product, create_tag


class ProductAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(username="test_admin")
        self.client.force_login(user)

    def test_add_product_saves_category_and_tags(self):
        tag1 = create_tag(name="Commercial")
        tag2 = create_tag(name="Indoor")
        category = create_category(name="Wire & Cable")

        product_data = {
            "name": "MC Cable – 12/2",
            "description": "12/2 metal-clad cable for indoor commercial wiring",
            "category": category.pk,
            "tags": [tag1.pk, tag2.pk],
        }

        url = reverse("admin:catalog_product_add")
        response = self.client.post(url, product_data)

        # A successful product creation redirects with HTTP 302.
        self.assertEqual(302, response.status_code)

        product = Product.objects.get()

        self.assertEqual(product_data["name"], product.name)
        self.assertEqual(product_data["description"], product.description)
        self.assertEqual(category.pk, product.category_id)
        self.assertCountEqual(
            product.tags.values_list("pk", flat=True), [tag1.pk, tag2.pk]
        )

    def test_product_list_queries_do_not_grow_with_product_count(self):
        tag1 = create_tag(name="Commercial")
        tag2 = create_tag(name="Indoor")
        category = create_category()
        product1 = create_product(name="MC Cable – 12/2", category=category)
        product1.tags.add(tag1)
        product1.tags.add(tag2)

        url = reverse("admin:catalog_product_changelist")

        # Capture queries for the initial product list.
        with CaptureQueriesContext(connection) as queries_before:
            response_before = self.client.get(url)

        self.assertEqual(200, response_before.status_code)
        query_count_before = len(queries_before)

        product2 = create_product(name="MC Cable Connector", category=category)
        product2.tags.add(tag1)
        product2.tags.add(tag2)

        with CaptureQueriesContext(connection) as queries_after:
            response_after = self.client.get(url)

        self.assertEqual(200, response_after.status_code)
        query_count_after = len(queries_after)

        # Verify that adding another product does not increase the query count.
        self.assertEqual(query_count_after, query_count_before)

        # Verify that the updated list contains both products.
        self.assertContains(response_after, product1.name)
        self.assertContains(response_after, product2.name)
