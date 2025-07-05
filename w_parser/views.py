import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from w_parser.models import Product, Search, SearchProduct
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


@csrf_exempt
def save_products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query", "").strip()
            products = data.get("products", [])

            if not query:
                return JsonResponse(
                    {"success": False, "error": "Query is required"}, status=400
                )
            if not products:
                return JsonResponse(
                    {"success": False, "error": "No products provided"},
                    status=400,
                )

            search, _ = Search.objects.get_or_create(name=query)

            for item in products:
                if not item.get("wb_id") or not isinstance(
                    item.get("wb_id"), int
                ):
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"Invalid or missing wb_id for item {item.get('name', 'Unknown')}",
                        },
                        status=400,
                    )

                product, _ = Product.objects.get_or_create(
                    wb_id=item["wb_id"],
                    defaults={
                        "name": item["name"],
                        "price": item["price"],
                        "discount_price": item["discount_price"],
                        "rating": item.get("rating"),
                        "reviews": item.get("reviews", 0),
                    },
                )

                SearchProduct.objects.get_or_create(
                    search=search, product=product
                )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"detail": "Method not allowed"}, status=405)
