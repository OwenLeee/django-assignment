from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from catalog.models import Category, Tag


class CategoryNameTests(SimpleTestCase):
    def validate(self, category):
        category.full_clean(
            validate_unique=False,
            validate_constraints=False,
        )

    def test_name_is_trimmed_and_case_is_preserved(self):
        category = Category(name="  Industrial  ")

        self.validate(category)
        self.assertEqual(category.name, "Industrial")

    def test_whitespace_only_name_is_rejected(self):
        category = Category(name="   ")

        with self.assertRaises(ValidationError) as context:
            self.validate(category)
        self.assertIn("name", context.exception.message_dict)

    def test_name_length_limit_applies_after_trimming(self):
        category = Category(name=f"  {'A' * 100}  ")

        self.validate(category)
        self.assertEqual(category.name, "A" * 100)

        category.name = "A" * 101

        with self.assertRaises(ValidationError) as context:
            self.validate(category)
        self.assertIn("name", context.exception.message_dict)


class CategoryUniquenessTests(TestCase):
    def test_duplicate_name_is_rejected_ignoring_case_and_spaces(self):
        Category.objects.create(name="Industrial")
        duplicate = Category(name="  industrial  ")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_existing_category_can_change_its_own_capitalization(self):
        category = Category.objects.create(name="Industrial")
        category.name = "INDUSTRIAL"
        category.full_clean()
        category.save()
        category.refresh_from_db()

        self.assertEqual(category.name, "INDUSTRIAL")

    def test_database_rejects_case_insensitive_duplicate(self):
        Category.objects.create(name="Industrial")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="industrial")


class CategorySaveTests(TestCase):
    def test_create_stores_trimmed_name(self):
        category = Category.objects.create(name="  Industrial  ")
        category.refresh_from_db()

        self.assertEqual(category.name, "Industrial")

    def test_save_rejects_whitespace_only_name(self):
        category = Category(name="   ")

        with self.assertRaises(ValidationError):
            category.save()
        self.assertEqual(Category.objects.count(), 0)


class TagNameTests(SimpleTestCase):
    def validate(self, tag):
        tag.full_clean(
            validate_unique=False,
            validate_constraints=False,
        )

    def test_name_is_trimmed_and_case_is_preserved(self):
        tag = Tag(name="  Industrial  ")

        self.validate(tag)
        self.assertEqual(tag.name, "Industrial")

    def test_whitespace_only_name_is_rejected(self):
        tag = Tag(name="   ")

        with self.assertRaises(ValidationError) as context:
            self.validate(tag)
        self.assertIn("name", context.exception.message_dict)

    def test_name_length_limit_applies_after_trimming(self):
        tag = Tag(name=f"  {'A' * 100}  ")

        self.validate(tag)
        self.assertEqual(tag.name, "A" * 100)

        tag.name = "A" * 101

        with self.assertRaises(ValidationError) as context:
            self.validate(tag)
        self.assertIn("name", context.exception.message_dict)
