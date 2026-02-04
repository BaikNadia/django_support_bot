from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import random
from .models import Advice
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count



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


# Веб-страницы
def home(request):
    """Главная страница"""
    latest_advice = Advice.objects.filter(is_active=True).order_by('-created_at')[:6]
    total_advice = Advice.objects.filter(is_active=True).count()

    # Статистика по категориям
    categories_count = {}
    for cat_code, cat_name in Advice.CATEGORY_CHOICES:
        categories_count[cat_code] = Advice.objects.filter(
            category=cat_code, is_active=True
        ).count()

    return render(request, 'advice_app/home.html', {
        'latest_advice': latest_advice,
        'total_advice': total_advice,
        'categories_count': categories_count,
    })


def random_advice_page(request):
    """Страница случайного совета"""
    advice = Advice.objects.filter(is_active=True).order_by('?').first()
    if not advice:
        # Дефолтный совет если база пуста
        advice = {
            'id': 0,
            'text': 'Верь в себя! У тебя всё получится! 💫',
            'category': 'motivation',
            'get_category_display': lambda: '💪 Мотивация'
        }
    return render(request, 'advice_app/random_advice.html', {'advice': advice})


def all_advice(request):
    """Страница всех советов"""
    category = request.GET.get('category', None)

    # Получаем советы
    advice_list = Advice.objects.filter(is_active=True)
    if category and category in dict(Advice.CATEGORY_CHOICES):
        advice_list = advice_list.filter(category=category)

    advice_list = advice_list.order_by('-created_at')

    # Пагинация
    paginator = Paginator(advice_list, 12)  # 12 советов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Статистика для фильтров
    category_stats = []
    total_count = Advice.objects.filter(is_active=True).count()
    category_stats.append({
        'code': 'all',
        'name': 'Все',
        'emoji': '📚',
        'count': total_count
    })

    for cat_code, cat_name in Advice.CATEGORY_CHOICES:
        count = Advice.objects.filter(category=cat_code, is_active=True).count()
        emoji_map = {
            'motivation': '💪',
            'comfort': '🤗',
            'inspiration': '✨',
            'wisdom': '🧠'
        }
        category_stats.append({
            'code': cat_code,
            'name': cat_name,
            'emoji': emoji_map.get(cat_code, '📝'),
            'count': count
        })

    return render(request, 'advice_app/all_advice.html', {
        'page_obj': page_obj,
        'advice_list': page_obj.object_list,
        'category_stats': category_stats,
        'active_category': category,
        'total_count': total_count,
        'is_paginated': page_obj.has_other_pages(),
    })


def category_advice(request, category):
    """Страница советов по категории"""
    if category not in dict(Advice.CATEGORY_CHOICES):
        category = 'motivation'

    advice_list = Advice.objects.filter(
        category=category, is_active=True
    ).order_by('-created_at')

    category_name = dict(Advice.CATEGORY_CHOICES)[category]
    emoji_map = {
        'motivation': '💪',
        'comfort': '🤗',
        'inspiration': '✨',
        'wisdom': '🧠'
    }

    return render(request, 'advice_app/category_advice.html', {
        'advice_list': advice_list,
        'category': category,
        'category_name': category_name,
        'category_emoji': emoji_map.get(category, '📝'),
    })


def advice_detail(request, id):
    """Детальная страница совета"""
    advice = get_object_or_404(Advice, id=id, is_active=True)
    return render(request, 'advice_app/advice_detail.html', {'advice': advice})


def about(request):
    """Страница "О проекте" """
    return render(request, 'advice_app/about.html')


def license_page(request):
    """Страница с лицензией"""
    return render(request, 'advice_app/license.html')
