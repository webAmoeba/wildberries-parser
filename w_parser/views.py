from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.views.decorators.http import require_POST

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


@require_POST
def save_search(request):
    query = request.POST.get("query", "").strip()
    if not query:
        messages.error(request, "Не указан запрос")
        return redirect("index")

    min_price = request.POST.get("min_price")
    max_price = request.POST.get("max_price")
    min_rating = request.POST.get("min_rating")
    min_reviews = request.POST.get("min_reviews")
    sort_by = request.POST.get("sort_by")

    products = fetch_wb_products(query, limit=10)
    products = apply_price_filters(products, min_price, max_price)
    products = apply_rating_filter(products, min_rating)
    products = apply_reviews_filter(products, min_reviews)

    if sort_by and "_" in sort_by:
        field, order = sort_by.split("_", 1)
        key_map = {
            "name": lambda p: p["name"].lower(),
            "price": lambda p: p["price"],
            "rating": lambda p: p.get("rating") or 0,
            "reviews": lambda p: p.get("reviews", 0),
        }
        rev = order == "desc"
        products = sorted(products, key=key_map[field], reverse=rev)

    search = Search.objects.create(name=query)
    for p in products:
        prod, _ = Product.objects.get_or_create(
            wb_id=p["wb_id"],
            defaults={
                "name": p["name"],
                "price": p["price"],
                "discount_price": p["discount_price"],
                "rating": p.get("rating"),
                "reviews": p.get("reviews", 0),
            },
        )
        SearchProduct.objects.get_or_create(search=search, product=prod)

    messages.success(
        request, format_html("Поиск <b>{}</b> успешно сохранён.", query)
    )
    return redirect("search_products", search_id=search.id)


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
