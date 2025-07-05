import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from w_parser.models import Product
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
            for item in data:
                # избежать дублей по названию
                Product.objects.get_or_create(
                    name=item["name"],
                    defaults={
                        "price": item["price"],
                        "discount_price": item["discount_price"],
                        "rating": item.get("rating"),
                        "reviews": item.get("reviews", 0),
                    },
                )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"detail": "Method not allowed"}, status=405)
