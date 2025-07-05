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

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()

    data = resp.json()

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
