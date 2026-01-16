import requests


def fetch_wb_products(query: str, limit: int = 10) -> list[dict]:
    url = "https://search.wb.ru/exactmatch/ru/common/v5/search"

    params = {
        "appType": 1,
        "curr": "rub",
        "dest": "-1257786",
        "query": query,
        "resultset": "catalog",
        "limit": limit,
        "page": 1,
        "sort": "popular",
        "spp": 24,
        "suppressSpellcheck": "false",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        print(f"fetch_wb_products error: {exc}")
        return []
    except ValueError as exc:
        print(f"fetch_wb_products json error: {exc}")
        return []

    raw_products = data.get("data", {}).get("products", [])

    products = []
    for item in raw_products:
        products.append(
            {
                "wb_id": item.get("id"),
                "name": item.get("name", ""),
                "price": item.get("sizes", [{}])[0]
                .get("price", {})
                .get("basic", 0)
                // 100,
                "discount_price": item.get("sizes", [{}])[0]
                .get("price", {})
                .get("product", 0)
                // 100,
                "rating": item.get("reviewRating"),
                "reviews": item.get("feedbacks", 0),
            }
        )

    return products


def filter_products(
    products, min_price=None, max_price=None, min_rating=None, min_reviews=None
):
    """Применить последовательно все фильтры к списку dict или QuerySet."""
    from w_parser.views import (
        apply_price_filters,
        apply_rating_filter,
        apply_reviews_filter,
    )

    products = apply_price_filters(products, min_price, max_price)
    products = apply_rating_filter(products, min_rating)
    products = apply_reviews_filter(products, min_reviews)
    return products


def sort_products(products, sort_by: str):
    """Отсортировать список dict по ключу или вернуть QuerySet с .order_by."""
    if not sort_by or "_" not in sort_by:
        return products

    field, order = sort_by.split("_", 1)

    # для QuerySet
    from django.db.models.query import QuerySet

    if isinstance(products, QuerySet):
        orm_map = {
            "name": "name",
            "price": "price",
            "rating": "rating",
            "reviews": "reviews",
        }
        base = orm_map.get(field)
        if base:
            prefix = "-" if order == "desc" else ""
            return products.order_by(f"{prefix}{base}")
        return products

    # для списка dict
    key_map = {
        "name": lambda p: p["name"].lower(),
        "price": lambda p: p["price"],
        "rating": lambda p: p.get("rating") or 0,
        "reviews": lambda p: p.get("reviews", 0),
    }
    key = key_map.get(field)
    if not key:
        return products
    return sorted(products, key=key, reverse=(order == "desc"))
