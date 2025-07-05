from django.contrib import admin

from w_parser.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "discount_price",
        "rating",
        "reviews",
        "created_at",
    )
    list_filter = ("created_at", "rating")
    search_fields = ("name",)
