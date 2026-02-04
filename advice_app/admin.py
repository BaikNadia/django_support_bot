from django.contrib import admin
from .models import Advice


# Кастомизация отображения в админке
@admin.register(Advice)
class AdviceAdmin(admin.ModelAdmin):
    # Что показываем в списке
    list_display = ("id", "category", "short_text", "created_at", "is_active")

    # Фильтры справа
    list_filter = ("category", "is_active")

    # Поиск
    search_fields = ("text",)

    # Что можно редактировать прямо в списке
    list_editable = ("is_active",)

    # Пагинация
    list_per_page = 20

    # Метод для сокращенного текста
    def short_text(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text

    short_text.short_description = "Текст"
