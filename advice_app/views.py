from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import random
from .models import Advice


@csrf_exempt  # Отключаем CSRF для API
@require_GET  # Разрешаем только GET запросы
def get_random_advice(request):
    """
    API для получения случайного совета
    Примеры запросов:
    /api/advice/ - случайный совет любой категории
    /api/advice/?category=motivation - совет мотивации
    """

    # Получаем категорию из параметров запроса
    category = request.GET.get("category", None)

    # Фильтруем только активные советы
    queryset = Advice.objects.filter(is_active=True)

    # Если указана категория - фильтруем по ней
    if category and category in dict(Advice.CATEGORY_CHOICES):
        queryset = queryset.filter(category=category)

    # Если есть советы - выбираем случайный
    if queryset.exists():
        advice = random.choice(list(queryset))
        return JsonResponse(
            {
                "text": advice.text,
                "category": advice.get_category_display(),
                "id": advice.id,
            }
        )
    else:
        # Если советов нет - возвращаем дефолтный
        return JsonResponse(
            {
                "text": "Верь в себя! У тебя всё получится! 💫",
                "category": "default",
                "id": 0,
            }
        )
