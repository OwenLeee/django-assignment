from django import forms

from catalog.models import Category


class CategoryChoiceField(forms.ModelChoiceField):
    """Distinguish malformed category IDs from unavailable categories.

    Validation order: to_python() -> validate() -> run_validators()
    -> form.clean_category() (only if field validation succeeds).

    Check ID syntax before the parent to_python() looks up the category.
    """

    def to_python(self, value):
        # Let the parent field handle an omitted or empty selection.
        if value is None or value == "":
            return super().to_python(value)

        # Accept positive IDs written with ASCII digits, including leading zeros.
        # Examples: "1" and "001" are valid; "0", "000", "+1", and " 1 " are invalid.
        if value.isascii() and value.isdigit() and value.lstrip("0") != "":
            return super().to_python(value)

        raise forms.ValidationError("Invalid category selection.")


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=200, strip=True)
    category = CategoryChoiceField(
        required=False,
        queryset=Category.objects.all(),
        error_messages={
            "invalid_choice": "The selected category is no longer available.",
        },
    )
