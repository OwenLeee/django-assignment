from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from catalog.search.forms import ProductSearchForm
from catalog.tests.models.helpers import create_category, create_tag


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


class SingleValueParameterTests(SimpleTestCase):
    def test_repeated_keyword_is_rejected(self):
        cases = ["q=wire&q=wire", "q=wire&q=conduit"]

        for query in cases:
            with self.subTest(query=query):
                form = ProductSearchForm(data=QueryDict(query))

                self.assertFalse(form.is_valid())
                self.assertIn("q", form.errors)
                self.assertIn("Enter only one search query.", form.errors["q"])

    def test_repeated_tag_mode_is_rejected(self):
        cases = ["tag_mode=all&tag_mode=all", "tag_mode=all&tag_mode=any"]

        for query in cases:
            with self.subTest(query=query):
                form = ProductSearchForm(data=QueryDict(query))

                self.assertFalse(form.is_valid())
                self.assertIn("tag_mode", form.errors)
                self.assertIn(
                    "Select only one tag matching mode.", form.errors["tag_mode"]
                )

    def test_repeated_page_is_rejected(self):
        cases = ["page=1&page=1", "page=1&page=2"]

        for query in cases:
            with self.subTest(query=query):
                form = ProductSearchForm(data=QueryDict(query))

                self.assertFalse(form.is_valid())
                self.assertIn("Specify only one page.", form.non_field_errors())


class TagModeFieldTests(SimpleTestCase):
    def test_missing_or_empty_tag_mode_defaults_to_all(self):
        cases = ["", "tag_mode="]

        for query in cases:
            with self.subTest(query=query):
                form = ProductSearchForm(data=QueryDict(query))

                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data["tag_mode"], "all")

    def test_valid_tag_mode_is_retained_without_tags(self):
        cases = ["all", "any"]

        for mode in cases:
            with self.subTest(mode=mode):
                form = ProductSearchForm(data=QueryDict(f"tag_mode={mode}"))

                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data["tag_mode"], mode)

    def test_invalid_tag_mode_is_rejected_without_tags(self):
        form = ProductSearchForm(data=QueryDict("tag_mode=banana"))

        self.assertFalse(form.is_valid())
        self.assertIn("tag_mode", form.errors)


class TagFieldTests(TestCase):
    def test_valid_tags_return_selected_tags(self):
        tag1 = create_tag(name="Tag 1")
        tag2 = create_tag(name="Tag 2")

        data = QueryDict(f"tag={tag1.pk}&tag={tag2.pk}")
        form = ProductSearchForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertCountEqual(form.cleaned_data["tag"], [tag1, tag2])

    def test_empty_tags_are_acceptable(self):
        data = QueryDict()
        form = ProductSearchForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertCountEqual(form.cleaned_data["tag"], [])

    def test_repeated_tag_ids_are_deduplicated(self):
        tag1 = create_tag(name="Tag 1")

        data = QueryDict(f"tag={tag1.pk}&tag={tag1.pk}")
        form = ProductSearchForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertCountEqual(form.cleaned_data["tag"], [tag1])

    def test_malformed_tag_is_rejected(self):
        valid_tag = create_tag(name="Valid tag")
        data = QueryDict(f"tag={valid_tag.pk}&tag=abc")
        form = ProductSearchForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("tag", form.errors)
        self.assertIn("Invalid tag selection.", form.errors["tag"])

    def test_unavailable_tag_is_rejected(self):
        valid_tag = create_tag(name="Valid tag")
        deleted_tag = create_tag(name="Deleted tag")
        unavailable_id = deleted_tag.pk
        deleted_tag.delete()

        data = QueryDict(f"tag={valid_tag.pk}&tag={unavailable_id}")
        form = ProductSearchForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("tag", form.errors)
        self.assertIn("The selected tag is no longer available.", form.errors["tag"])
