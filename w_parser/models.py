from django.db import models


class Product(models.Model):
    wb_id = models.BigIntegerField("WB ID", unique=True, db_index=True)
    name = models.CharField("Название", max_length=255)
    price = models.PositiveIntegerField("Цена (₽)")
    discount_price = models.PositiveIntegerField("Цена со скидкой (₽)")
    rating = models.FloatField("Рейтинг", null=True, blank=True)
    reviews = models.PositiveIntegerField("Число отзывов")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.wb_id})"


class Search(models.Model):
    name = models.CharField("Имя поиска", max_length=255)
    created_at = models.DateTimeField("Дата поиска", auto_now_add=True)
    products = models.ManyToManyField(
        Product,
        through="SearchProduct",
        related_name="searches",
        verbose_name="Товары"
    )

    class Meta:
        verbose_name = "Поиск"
        verbose_name_plural = "Поиски"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SearchProduct(models.Model):
    search = models.ForeignKey(
        Search, 
        on_delete=models.CASCADE, 
        verbose_name="Поиск"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Товар"
    )

    class Meta:
        verbose_name = "Связь Поиск–Товар"
        verbose_name_plural = "Связи Поиск–Товар"
        unique_together = (("search", "product"),)

    def __str__(self):
        return f"{self.search.name} → {self.product.name}"
