import random

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import BOT_TOKEN, CONGRATULATIONS_STIKERS
from database import (
    get_user, create_user, get_translation_mode, set_translation_mode,
    get_random_word, add_word_to_learn, get_words, get_variants,
    delete_word_from_learn, get_stats, get_user_achievements,
    update_statistics, login, is_first_login_today,
    check_achievements, add_word_to_db_and_user
)
from yandex import get_translation_yandex

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    """Стартовое сообщение с записью пользователя в базу данных"""
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    user = get_user(telegram_id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('Начать обучение', 'Тренировка')
    keyboard.add('Мои результаты', 'Добавить слово')
    if not user:
        create_user(telegram_id, first_name)
        mode = get_translation_mode(message.from_user.id)
        mode_flag = "🇷🇺 → 🇬🇧" if mode == 'ru-en' else "🇬🇧 → 🇷🇺"
        keyboard.add(f'🔤 Режим перевода: {mode_flag}')
        bot.send_message(message.chat.id,
                         f'Привет, {first_name}, я бот для обучения Английскому языку. Вы записаны в базу',
                         reply_markup=keyboard)
    else:
        mode = get_translation_mode(message.from_user.id)
        mode_flag = "🇷🇺 → 🇬🇧" if mode == 'ru-en' else "🇬🇧 → 🇷🇺"
        keyboard.add(f'🔤 Режим перевода: {mode_flag}')
        bot.send_message(message.chat.id,
                         f'Давно не виделись, {first_name}!',
                         reply_markup=keyboard)


@bot.message_handler(func=lambda m: m.text.startswith('🔤 Режим перевода:'))
def toggle_translation_mode(message):
    """Функция переключения режима переводов"""
    current_mode = get_translation_mode(message.from_user.id)
    new_mode = 'ru-en' if current_mode == 'en-ru' else 'en-ru'

    set_translation_mode(message.from_user.id, new_mode)
    mode_text = "🇷🇺 → 🇬🇧" if new_mode == 'ru-en' else "🇬🇧 → 🇷🇺"

    bot.send_message(
        message.chat.id,
        f"✅ Режим перевода изменён: {mode_text}"
    )
    start_message(message)

@bot.message_handler(func=lambda m: m.text == "Начать обучение")
def start_studying(message):
    bot.send_message(message.chat.id, "Давай начнём!")
    study_word(message)


def study_word(message):
    """Обучаемся на случайном слове и добавляем его к списку изученных"""
    word_data = get_random_word(message.from_user.id)

    if word_data:
        response = f"Слово: **{word_data.word}**\nПеревод: __{word_data.translation}__"
        bot.send_message(message.chat.id, response, parse_mode='markdownv2')
        add_word_to_learn(word_data.word, message.from_user.id)

        update_statistics(message.from_user.id, 'words')
        handle_achievements(message)
    else:
        bot.send_message(message.chat.id, "К сожалению, пока нет доступных слов.")
        return


    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Следующее слово", "Закончить обучение")
    bot.send_message(message.chat.id, "Что будем делать дальше?", reply_markup=keyboard)

    bot.register_next_step_handler(message, handle_after_word)


def handle_after_word(message):
    """Обработчик кнопок после обучения слову"""
    if message.text == "Следующее слово":
        study_word(message)
    elif message.text == "Закончить обучение":
        bot.send_message(message.chat.id, "Тренировка окончена. Молодец! 🎉")
        start_message(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выбери вариант ниже.")

@bot.message_handler(func= lambda m:m.text == "Тренировка")
def train_words(message):
    """Режим тренировки"""
    if is_first_login_today(message.from_user.id):
        bot.send_sticker(message.chat.id, random.choice(CONGRATULATIONS_STIKERS))
        bot.send_message(message.chat.id, "Первая тренировка за сегодня, так держать!")
    login(message.from_user.id)
    handle_achievements(message)

    words = get_words(message.chat.id)

    if not words:
        bot.send_message(message.chat.id, "У тебя пока нет слов для тренировки.")
        return

    current_word = random.choice(words)
    mode = get_translation_mode(message.from_user.id)

    if mode == 'ru-en':
        question_text = f"Переведи слово: *{current_word.translation}*"
        variants = get_variants(message.from_user.id, current_word.word)
        correct_answer = current_word.word
        buttons = [variant.word for variant in variants]
    else:
        question_text = f"Переведи слово: *{current_word.word}*"
        variants = get_variants(message.from_user.id, current_word.word)
        correct_answer = current_word.translation
        buttons = [variant.translation for variant in variants]

    buttons.append(correct_answer)
    random.shuffle(buttons)
    buttons.append('⏭️ Следующее слово')
    buttons.append('❌ Удалить слово')
    buttons.append('🔚 Закончить тренировку')

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard.add(*row)

    bot.send_message(
        message.chat.id,
        question_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(message,
                                   train_response,
                                   correct_answer=correct_answer,
                                   current_word=current_word)


def train_response(message, correct_answer, current_word):
    """Обработка ответа от пользователя"""
    user_text = message.text.strip()
    mode = get_translation_mode(message.from_user.id)
    if user_text == '⏭️ Следующее слово':
        train_words(message)
        return

    elif user_text == '🔚 Закончить тренировку':
        bot.send_message(message.chat.id,
                         "Тренировка окончена. Молодец! 🎉",
                         reply_markup=ReplyKeyboardRemove())
        start_message(message)
        return

    elif user_text == '❌ Удалить слово':
        delete_word_from_learn(message.from_user.id, current_word.word)
        update_statistics(message.from_user.id, 'sub_words')
        bot.send_message(message.chat.id,
                         f"Слово *{current_word.word}* удалено из списка изучения.",
                         parse_mode="Markdown")
        train_words(message)
        return

    if mode == 'ru-en':
        display_word = current_word.translation
    else:
        display_word = current_word.word


    if user_text.lower() == correct_answer:
        bot.send_message(message.chat.id, "✅ Правильно! Молодец!")
        update_statistics(message.from_user.id, 'correct')
        handle_achievements(message)
        train_words(message)
    else:
        update_statistics(message.from_user.id, 'wrong')
        bot.send_message(
            message.chat.id,
            f"❌ Неправильно. Попробуй ещё раз!\n"
            f"Переведи слово: *{display_word}*?",
            parse_mode="Markdown"
        )
        handle_achievements(message)
        bot.register_next_step_handler(message,
                                       train_response,
                                       correct_answer=correct_answer,
                                       current_word=current_word)


@bot.message_handler(func=lambda m: m.text == "Добавить слово")
def add_new_word(message):
    """Добавление нового слова через Yandex Dictionary API"""
    bot.send_message(message.chat.id, 'Введите слово на Русском или Английском языке')
    bot.register_next_step_handler(message, add_new_word_handler)


def add_new_word_handler(message):
    word = message.text.strip().lower()

    if not word.isalpha():
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное слово (только буквы).")
        return

    if any('а' <= char <= 'я' for char in word):
        direction = 'ru_to_en'
    else:
        direction = 'en_to_ru'

    translation = get_translation_yandex(word)
    if not translation:
        bot.send_message(message.chat.id,
                         "Не удалось перевести слово. "
                         "Проверьте подключение или попробуйте другое слово.")
        return

    if add_word_to_db_and_user(message.from_user.id, word, translation, direction):
        print(f"✅ Слово '{word}' добавлено с переводом: '{translation}'")
        bot.send_message(message.chat.id,
                         f"✅ Слово *{word}* добавлено с переводом: _{translation}_",
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при добавлении слова в базу данных.")


@bot.message_handler(func=lambda m: m.text == "Мои результаты")
def show_statistics(message):
    """Показать статистику пользователя"""

    telegram_id = message.from_user.id
    stats = get_stats(telegram_id)

    if stats:
        response = (
            f"📊 Ваша статистика:\n"
            f"Всего слов: {stats.total_words}\n"
            f"Правильных ответов: {stats.total_correct}\n"
            f"Неправильных ответов: {stats.total_wrong}\n"
            f"Текущая серия: {stats.current_streak} дней\n"
            f"Максимальная серия: {stats.max_streak} дней"
        )
        achievements = get_user_achievements(telegram_id)
        if achievements:
            response += "\n\n🎖 Полученные достижения:\n"
            for ach in achievements:
                response += f"• {ach.name} — {ach.description}\n"
        else:
            response += "\n\n🎖 Пока нет достижений. Продолжайте учиться!"
    else:
        response = "❌ Статистика не найдена."

    bot.send_message(message.chat.id, response)


def handle_achievements(message):
    """Проверка и оповощение о новых достижениих"""
    telegram_id = message.from_user.id
    stats = get_stats(telegram_id)
    if not stats:
        return

    achievement_types = [
        ('total_words', stats.total_words),
        ('total_correct', stats.total_correct),
        ('total_wrong', stats.total_wrong),
        ('max_streak', stats.max_streak)
    ]

    for a_type, value in achievement_types:
        achievement = check_achievements(telegram_id, a_type, value)
        if achievement:
            try:
                bot.send_sticker(message.chat.id, random.choice(CONGRATULATIONS_STIKERS))
                bot.send_message(
                    message.chat.id,
                    f'🎉 Поздравляем! Вы получили достижение:\n\n'
                    f'"{achievement.name}" — {achievement.description}'
                )
            except Exception as e:
                print(e)