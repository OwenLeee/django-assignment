from django import forms

from catalog.models import Category, Tag


def is_positive_ascii_id(value):
    # Accept positive IDs written with ASCII digits, including leading zeros.
    # Examples: "1" and "001" are valid; "0", "000", "+1", and " 1 " are invalid.
    return value.isascii() and value.isdigit() and value.lstrip("0") != ""


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

        if is_positive_ascii_id(value):
            return super().to_python(value)

        raise forms.ValidationError("Invalid category selection.")


class TagMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        if not value:
            return super().clean(value)
        normalized_values = []
        for raw_id in value:
            if is_positive_ascii_id(raw_id):
                normalized_values.append(str(int(raw_id)))
            else:
                raise forms.ValidationError("Invalid tag selection.")
        return super().clean(normalized_values)


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=200, strip=True)
    category = CategoryChoiceField(
        required=False,
        queryset=Category.objects.all(),
        error_messages={
            "invalid_choice": "The selected category is no longer available.",
        },
    )
    tag = TagMultipleChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={
            "invalid_pk_value": "Invalid tag selection.",
            "invalid_choice": "The selected tag is no longer available.",
        },
    )

    tag_mode = forms.ChoiceField(
        required=False,
        initial="all",
        widget=forms.RadioSelect,
        choices=[("all", "Match all selected tags"), ("any", "Match any selected tag")],
    )

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self.data, "getlist"):
            if len(self.data.getlist("category")) > 1:
                self.add_error("category", "Select only one category.")
            if len(self.data.getlist("q")) > 1:
                self.add_error("q", "Enter only one search query.")
            if len(self.data.getlist("tag_mode")) > 1:
                self.add_error("tag_mode", "Select only one tag matching mode.")
            if len(self.data.getlist("page")) > 1:
                self.add_error(None, "Specify only one page.")
        return cleaned_data

    def clean_tag_mode(self):
        return (
            "all"
            if self.cleaned_data["tag_mode"] == ""
            else self.cleaned_data["tag_mode"]
        )
