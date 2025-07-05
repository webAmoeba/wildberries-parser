from django.db import models


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    price = models.PositiveIntegerField("Цена (₽)")
    discount_price = models.PositiveIntegerField("Цена со скидкой (₽)")
    rating = models.FloatField("Рейтинг", null=True, blank=True)
    reviews = models.PositiveIntegerField("Число отзывов")
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
