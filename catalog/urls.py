from django.urls import path
from django.views.generic.base import RedirectView

from catalog.search.views import product_list

app_name = "catalog"
urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            pattern_name="catalog:product_list",
            permanent=False,
        ),
    ),
    path("products/", product_list, name="product_list"),
]
