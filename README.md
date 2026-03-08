# 📚 Бот для изучения английского языка
## ✨ Функции бота

- **Добавление новых слов** — через Yandex Dictionary API
- **Режимы перевода**:
    - Английский → Русский (`🇺🇸 → 🇷🇺`)
    - Русский → Английский (`🇷🇺 → 🇺🇸`)
- **Тренировка слов** с вариантами ответов
- **Статистика**:
    - Количество выученных слов
    - Правильные/неправильные ответы
    - Серия дней подряд
- **Достижения** за активность
- **Автоматический перевод** при добавлении слов
- ## 🚀 Запуск бота

### 1. Установите зависимости:
    bash pip install -r requirements.txt
### 2. Настройте переменные в config.py
Yandex Dictionary API получить можно здесь: https://yandex.ru/dev/dictionary/keys/get/?service=dict

    YANDEX_API_KEY = 'ВАШ API KEY'

Токен телеграм бота из [@BotFather](https://t.me/BotFather)

    BOT_TOKEN = 'ТОКЕН ВАШЕГО БОТА'

Данные базы PostgreSQL

    DB_USER = "postgres"
    DB_PASSWORD = "ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ"
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "db"

### 3. Создайте базу данных
    psql -U postgres

    sql CREATE DATABASE db

### 4. Запустите бота

     python main.py

