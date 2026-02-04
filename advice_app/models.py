from django.db import models
from django.core.validators import MinLengthValidator


class Advice(models.Model):
    # Категории советов
    CATEGORY_CHOICES = [
        ("motivation", "💪 Мотивация"),
        ("comfort", "🤗 Утешение"),
        ("inspiration", "✨ Вдохновение"),
        ("wisdom", "🧠 Мудрость"),
    ]

    # Текст совета
    text = models.TextField(
        verbose_name="Текст совета", validators=[MinLengthValidator(10)]
    )

    # Категория
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="motivation",
        verbose_name="Категория",
    )

    # Дата создания
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Активен ли совет
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.category}: {self.text[:50]}..."

    class Meta:
        verbose_name = "Совет"
        verbose_name_plural = "Советы"
