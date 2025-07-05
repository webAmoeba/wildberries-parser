from django.contrib import admin

from w_parser.models import Product, Search, SearchProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "wb_id",
        "name",
        "price",
        "discount_price",
        "rating",
        "reviews",
    )
    search_fields = ("name", "wb_id")
    list_filter = ("reviews",)


class SearchProductInline(admin.TabularInline):
    model = SearchProduct
    extra = 0
    readonly_fields = ("product",)
    can_delete = False


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    inlines = [SearchProductInline]
    date_hierarchy = "created_at"
    search_fields = ("name",)


@admin.register(SearchProduct)
class SearchProductAdmin(admin.ModelAdmin):
    list_display = ("search", "product")
    list_filter = ("search",)
