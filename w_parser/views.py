import json

from django.contrib import messages
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt

from w_parser.models import Product, Search, SearchProduct
from w_parser.utils import fetch_wb_products


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )


def apply_price_filters(products, min_price, max_price):
    """фильтры по цене к списку или Queryset товаров"""
    if min_price:
        try:
            min_val = int(min_price)
            if isinstance(products, list):
                products = [
                    p for p in products if p["discount_price"] >= min_val
                ]
            else:
                products = products.filter(discount_price__gte=min_val)
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            max_val = int(max_price)
            if isinstance(products, list):
                products = [
                    p for p in products if p["discount_price"] <= max_val
                ]
            else:
                products = products.filter(discount_price__lte=max_val)
        except (ValueError, TypeError):
            pass
    return products


def apply_reviews_filter(products, min_reviews):
    """фильтр по количеству отзывов"""
    if min_reviews:
        try:
            rev = int(min_reviews)
            if isinstance(products, list):
                products = [p for p in products if p.get("reviews", 0) >= rev]
            else:
                products = products.filter(reviews__gte=rev)
        except (ValueError, TypeError):
            pass
    return products


def apply_rating_filter(products, min_rating):
    """фильтр по рейтингу"""
    if min_rating:
        try:
            rt = float(min_rating)
            if isinstance(products, list):
                products = [p for p in products if (p.get("rating") or 0) >= rt]
            else:
                products = products.filter(rating__gte=rt)
        except (ValueError, TypeError):
            pass
    return products


def index(request):
    query = request.GET.get("query", "").strip()
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    min_rating = request.GET.get("min_rating")
    min_reviews = request.GET.get("min_reviews")
    sort_by = request.GET.get("sort_by")

    products = []

    if query:
        products = fetch_wb_products(query, limit=10)
        products = apply_price_filters(products, min_price, max_price)
        products = apply_rating_filter(products, min_rating)
        products = apply_reviews_filter(products, min_reviews)
    else:
        print("Index: No query provided, skipping fetch_wb_products")

    if query and not (min_price or max_price) and products:
        vals = [p["discount_price"] for p in products]
        min_price = str(min(vals))
        max_price = str(max(vals))

    if sort_by:
        field, order = sort_by.split("_", 1)
        key_map = {
            "name": lambda p: p["name"].lower(),
            "price": lambda p: p["price"],
            "rating": lambda p: p.get("rating") or 0,
            "reviews": lambda p: p.get("reviews", 0),
        }
        rev = order == "desc"
        products = sorted(products, key=key_map[field], reverse=rev)

    return render(
        request,
        "index.html",
        {
            "query": query,
            "products": products,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "min_reviews": min_reviews,
            "sort_by": sort_by,
        },
    )


@csrf_exempt
def save_products(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        items = data.get("products", [])

        if not query:
            return JsonResponse(
                {"success": False, "error": "Не указан запрос"}, status=400
            )
        if not items:
            return JsonResponse(
                {"success": False, "error": "Нет товаров для сохранения"},
                status=400,
            )

        search = Search.objects.create(name=query)
        for item in items:
            wb_id = item.get("wb_id")
            if not isinstance(wb_id, int):
                return JsonResponse(
                    {
                        "success": False,
                        "error": format_html(
                            'Неверный wb_id для "{}"', item.get("name", "?")
                        ),
                    },
                    status=400,
                )

            prod, _ = Product.objects.get_or_create(
                wb_id=wb_id,
                defaults={
                    "name": item["name"],
                    "price": item["price"],
                    "discount_price": item["discount_price"],
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews", 0),
                },
            )
            SearchProduct.objects.get_or_create(search=search, product=prod)

        messages.success(
            request, format_html("Поиск <b>{}</b> успешно сохранён.", query)
        )
        return JsonResponse(
            {
                "success": True,
                "redirect": reverse("search_products", args=[search.id]),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def saved_searchs(request):
    searchs = Search.objects.all()
    return render(request, "saved_searchs.html", {"searchs": searchs})


def search_products(request, search_id):
    search = get_object_or_404(Search, id=search_id)
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    min_rating = request.GET.get("min_rating")
    min_reviews = request.GET.get("min_reviews")
    sort_by = request.GET.get("sort_by")

    products = Product.objects.filter(searches=search)
    products = apply_price_filters(products, min_price, max_price)
    products = apply_rating_filter(products, min_rating)
    products = apply_reviews_filter(products, min_reviews)

    if not (min_price or max_price) and products.exists():
        prices = list(products.values_list("discount_price", flat=True))
        min_price = str(min(prices))
        max_price = str(max(prices))

    if sort_by:
        orm_map = {
            "name_asc": "name",
            "name_desc": "-name",
            "price_asc": "price",
            "price_desc": "-price",
            "rating_asc": "rating",
            "rating_desc": "-rating",
            "reviews_asc": "reviews",
            "reviews_desc": "-reviews",
        }
        order = orm_map.get(sort_by)
        if order:
            products = products.order_by(order)

    return render(
        request,
        "index.html",
        {
            "query": search.name,
            "products": products,
            "search_id": search_id,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating,
            "min_reviews": min_reviews,
            "sort_by": sort_by,
        },
    )
