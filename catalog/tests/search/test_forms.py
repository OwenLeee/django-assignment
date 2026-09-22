from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from catalog.search.forms import ProductSearchForm
from catalog.tests.models.helpers import create_category


class KeywordFieldTests(SimpleTestCase):
    def test_keyword_trims_outer_whitespace(self):
        form = ProductSearchForm(data={"q": "  Test Query  "})

        self.assertTrue(form.is_valid(), form.errors)

        keyword_param = form.cleaned_data["q"]

        self.assertEqual(keyword_param, "Test Query")

    def test_keyword_length_limit(self):
        cases = [
            ("A" * 200, True),
            ("A" * 201, False),
            (" " + "A" * 200 + " ", True),
        ]  # (input_value, expected_valid)

        for input_value, expected_valid in cases:
            with self.subTest(length=len(input_value)):
                form = ProductSearchForm(data={"q": input_value})
                self.assertEqual(form.is_valid(), expected_valid, form.errors)

    def test_empty_keyword_is_valid(self):
        cases = [{}, {"q": ""}, {"q": "    "}]

        for data in cases:
            with self.subTest(data=data):
                form = ProductSearchForm(data=data)

                self.assertTrue(form.is_valid(), form.errors)

                keyword_param = form.cleaned_data["q"]

                self.assertEqual(keyword_param, "")


class CategoryFieldTests(TestCase):
    def test_valid_category_returns_category_instance(self):
        created_category = create_category()

        category_id = str(created_category.pk)

        cases = [
            {"category": category_id},
            {"category": "00" + category_id},
        ]

        for case in cases:
            with self.subTest(category=case["category"]):
                form = ProductSearchForm(data=case)

                self.assertTrue(form.is_valid(), form.errors)

                retrieved_category = form.cleaned_data["category"]

                self.assertEqual(retrieved_category, created_category)

    def test_empty_category_is_acceptable(self):
        cases = [{}, {"category": ""}]

        for case in cases:
            with self.subTest(case=case):
                form = ProductSearchForm(data=case)
                self.assertTrue(form.is_valid(), form.errors)
                retrieved_category = form.cleaned_data["category"]
                self.assertIsNone(retrieved_category)

    def test_malformed_category_is_rejected(self):
        cases = [
            {"category": "abc"},
            {"category": "  "},
            {"category": "0"},
            {"category": "000"},
            {"category": "+1"},
            {"category": "-1"},
            {"category": "1.5"},
            {"category": " 1 "},
            {"category": "１"},  # Full-width digit, not ASCII.
        ]

        for case in cases:
            with self.subTest(category=case["category"]):
                form = ProductSearchForm(data=case)

                self.assertFalse(form.is_valid())
                self.assertIn("category", form.errors)
                self.assertIn("Invalid category selection.", form.errors["category"])

    def test_unavailable_category_will_return_error_message(self):
        created_category = create_category()
        category_id = created_category.pk
        created_category.delete()

        form_data = {"category": str(category_id)}
        form = ProductSearchForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)
        self.assertIn(
            "The selected category is no longer available.", form.errors["category"]
        )

    def test_repeated_category_is_rejected(self):
        category1 = create_category(name="Wire & Cable")
        category2 = create_category(name="Conduit")
        cases = [
            QueryDict(f"category={category1.id}&category={category1.id}"),
            QueryDict(f"category={category1.id}&category={category2.id}"),
        ]

        for case in cases:
            with self.subTest(categories=case.getlist("category")):
                form = ProductSearchForm(data=case)
                self.assertFalse(form.is_valid())
                self.assertIn("category", form.errors)
                self.assertIn("Select only one category.", form.errors["category"])
