from django.shortcuts import render


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
        products = [
            {
                "name": f"Товар «{query}» пример 1",
                "price": 5000,
                "discount_price": 4000,
                "rating": 4.5,
                "reviews": 120,
            },
            {
                "name": f"Товар «{query}» пример 2",
                "price": 3200,
                "discount_price": 2900,
                "rating": 4.0,
                "reviews": 75,
            },
        ]

    return render(request, "index.html", {"query": query, "products": products})
