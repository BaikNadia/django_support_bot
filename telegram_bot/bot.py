import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из .env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден! Проверь файл .env")
    exit(1)

DJANGO_API_URL = "http://127.0.0.1:8000/api/advice/"

# Константы для ConversationHandler
CATEGORY = 1

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    [["🎲 Случайный совет", "📁 По категории"], ["ℹ️ О боте"]], resize_keyboard=True
)

category_keyboard = ReplyKeyboardMarkup(
    [
        ["💪 Мотивация", "🤗 Утешение"],
        ["✨ Вдохновение", "🧠 Мудрость"],
        ["🎲 Любая категория", "🏠 Главное меню"],
    ],
    resize_keyboard=True,
)


# ========== ФУНКЦИИ БОТА ==========


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 🌸\n\n"
        "Я - бот поддержки и добрых слов. Иногда всем нам нужно немного тепла и ободрения.\n\n"
        "Выбери действие ниже:",
        reply_markup=main_keyboard,
    )


async def get_random_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение случайного совета"""
    try:
        response = requests.get(DJANGO_API_URL)
        if response.status_code == 200:
            data = response.json()
            message = f"*{data['category']}* ✨\n\n{data['text']}"
        else:
            message = "💖 Помни: ты заслуживаешь счастья и любви!\nКаждый день - это новый шанс."

        await update.message.reply_text(
            message, parse_mode="Markdown", reply_markup=main_keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка получения совета: {e}")
        await update.message.reply_text(
            "🌻 Сегодня будет хороший день! Верь в себя и свои силы!",
            reply_markup=main_keyboard,
        )


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало выбора категории"""
    await update.message.reply_text(
        "Выбери категорию совета:", reply_markup=category_keyboard
    )
    return CATEGORY


async def get_advice_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение совета по выбранной категории"""
    user_choice = update.message.text

    # Маппинг кнопок на категории API
    category_map = {
        "💪 Мотивация": "motivation",
        "🤗 Утешение": "comfort",
        "✨ Вдохновение": "inspiration",
        "🧠 Мудрость": "wisdom",
        "🎲 Любая категория": None,
    }

    # Если вернуться в главное меню
    if user_choice == "🏠 Главное меню":
        await update.message.reply_text(
            "Возвращаемся в главное меню:", reply_markup=main_keyboard
        )
        return ConversationHandler.END

    # Определяем категорию для API
    category_key = category_map.get(user_choice)

    try:
        # Формируем параметры запроса
        params = {}
        if category_key:
            params["category"] = category_key

        # Делаем запрос к API
        response = requests.get(DJANGO_API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            message = f"*{data['category']}* ✨\n\n{data['text']}"
        else:
            message = "🌼 Ты прекрасен таким, какой ты есть!\nПрими себя сегодня и позволь миру увидеть твой свет."

        await update.message.reply_text(
            message, parse_mode="Markdown", reply_markup=category_keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(
            "🌿 Иногда просто нужно сделать глубокий вдох...\nИ помнить, что всё временно.",
            reply_markup=category_keyboard,
        )

    return CATEGORY  # Остаемся в состоянии выбора категории


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о боте"""
    about_text = """
*Обо мне* 🤗

Я - бот поддержки, созданный чтобы дарить немного тепла и доброты.

**Что я умею:**
• Присылать случайные добрые советы
• Фильтровать советы по категориям
• Поддерживать в трудную минуту

**Категории советов:**
💪 Мотивация - для поднятия духа
🤗 Утешение - когда грустно
✨ Вдохновение - для новых идей
🧠 Мудрость - жизненные уроки

*Администраторы добавляют новые советы через веб-интерфейс.*

Просто нажми "🎲 Случайный совет" или выбери категорию!
    """
    await update.message.reply_text(
        about_text, parse_mode="Markdown", reply_markup=main_keyboard
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text(
        "Возвращаемся в главное меню!", reply_markup=main_keyboard
    )
    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка произвольных текстовых сообщений"""
    text = update.message.text.lower()

    # Ответы на приветствия
    if any(word in text for word in ["привет", "hello", "hi", "хай", "здравствуй"]):
        await start(update, context)
    elif any(word in text for word in ["спасибо", "благодарю", "thanks", "thank you"]):
        await update.message.reply_text(
            "Спасибо тебе за добрые слова! ❤️\nТы делаешь этот мир лучше!",
            reply_markup=main_keyboard,
        )
    elif any(word in text for word in ["как дела", "как ты", "how are you"]):
        await update.message.reply_text(
            "У меня всё прекрасно, ведь я могу помогать таким замечательным людям как ты! 🌟",
            reply_markup=main_keyboard,
        )
    else:
        # Если сообщение не распознано
        await update.message.reply_text(
            "Я лучше понимаю команды из меню 😊\nИспользуй кнопки ниже:",
            reply_markup=main_keyboard,
        )


# ========== ОСНОВНАЯ ФУНКЦИЯ ==========


def main():
    """Запуск бота"""
    print("🚀 Запуск бота поддержки...")
    print(f"Токен: {'найден' if TOKEN else 'НЕ НАЙДЕН!'}")
    print(f"API URL: {DJANGO_API_URL}")
    print("=" * 50)

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # 1. ConversationHandler для выбора категории
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📁 По категории$"), choose_category)
        ],
        states={
            CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_advice_by_category)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # 2. Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    # 3. Обработчики кнопок главного меню
    application.add_handler(
        MessageHandler(filters.Regex("^🎲 Случайный совет$"), get_random_advice)
    )
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ О боте$"), about))

    # 4. Обработчик всех остальных текстовых сообщений
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Запускаем бота
    print("✅ Бот успешно запущен!")
    print("📱 Открой Telegram и напиши /start своему боту")
    print("=" * 50)

    # Убрали параметр allowed_updates
    application.run_polling()


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    main()
