from django.shortcuts import render

from w_parser.utils import fetch_wb_products


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )


def index(request):
    query = request.GET.get("query", "").strip()
    products = []

    if query:
        products = fetch_wb_products(query, limit=10)

    return render(request, "index.html", {"query": query, "products": products})
