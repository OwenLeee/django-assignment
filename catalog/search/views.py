from django.core.paginator import Paginator
from django.shortcuts import render

from catalog.search.forms import ProductSearchForm
from catalog.search.queries import search_products


def product_list(request):
    form_data = request.GET.copy()
    mode_values = form_data.getlist("tag_mode")

    if not mode_values or mode_values == [""]:
        form_data["tag_mode"] = "all"

    template_name = "catalog/search/product_list.html"
    form = ProductSearchForm(data=form_data)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        products = search_products(
            q=cleaned_data["q"],
            category=cleaned_data["category"],
            tags=cleaned_data["tag"],
            tag_mode=cleaned_data["tag_mode"],
        )
        paginator = Paginator(products, 10)
        page_obj = paginator.get_page(request.GET.get("page"))
        status = 200

    else:
        page_obj = None
        status = 400

    context = {"form": form, "page_obj": page_obj}
    return render(request, template_name, context, status=status)
