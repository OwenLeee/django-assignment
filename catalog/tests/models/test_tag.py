from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from catalog.models import Tag


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


class TagUniquenessTests(TestCase):
    def test_duplicate_name_is_rejected_ignoring_case_and_spaces(self):
        Tag.objects.create(name="Industrial")
        duplicate = Tag(name="  industrial  ")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_existing_tag_can_change_its_own_capitalization(self):
        tag = Tag.objects.create(name="Industrial")
        tag.name = "INDUSTRIAL"
        tag.full_clean()
        tag.save()
        tag.refresh_from_db()

        self.assertEqual(tag.name, "INDUSTRIAL")

    def test_database_rejects_case_insensitive_duplicate(self):
        Tag.objects.create(name="Industrial")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="industrial")


class TagSaveTests(TestCase):
    def test_create_stores_trimmed_name(self):
        tag = Tag.objects.create(name="  Industrial  ")
        tag.refresh_from_db()

        self.assertEqual(tag.name, "Industrial")

    def test_save_rejects_whitespace_only_name(self):
        tag = Tag(name="   ")

        with self.assertRaises(ValidationError):
            tag.save()
        self.assertEqual(Tag.objects.count(), 0)
