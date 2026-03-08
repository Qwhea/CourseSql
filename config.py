from sqlalchemy import URL

#Yandex Dictionary API получить можно здесь: https://yandex.ru/dev/dictionary/keys/get/?service=dict
YANDEX_API_KEY = 'ВАШ API KEY'
YANDEX_DICTIONARY_URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'

#Токен телеграм бота из BotFather
BOT_TOKEN = 'ВАШ ТОКЕН'

#Данные для входа в базу данных
DB_USER = "postgres"
DB_PASSWORD = "ПАРОЛЬ ПОЛЬЗОВАТЕЛЯ"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db"

DATABASE_URL = URL.create(
    drivername="postgresql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

#Стикеры получения достижений
CONGRATULATIONS_STIKERS = [
    'CAACAgIAAxkBAAEbzNJpqvTs0CRFdzJGrjwPlXpRYDbVpQACGwADwDZPE329ioPLRE1qOgQ',
    'CAACAgIAAxkBAAEbzNRpqvT5B1HScjYDMC_bvyb-ZwOVRAACdwUAAj-VzApljNMsSkHZTjoE',
    'CAACAgIAAxkBAAEbzNVpqvT74w0C2T3xsx1k_oA_XeSjMQACTQADWbv8JSiBoG3dG4L3OgQ',
    'CAACAgIAAxkBAAEbzNZpqvT8zDe4QpXtH7ewRWuWUJO7ZwAC6RsAAoV_EEnRch0GfnFH5zoE',
    'CAACAgIAAxkBAAEbzNppqvUAARpSrBcnu1_C32vUQ8J2RY8AAkAAA1KJkSM1XLo_etZCiToE',
    'CAACAgIAAxkBAAEbzNxpqvUEWZS766-e3AmqdTutrV86GAACNwADlp-MDjXGAq7f-3ZJOgQ',
    'CAACAgIAAxkBAAEbzN1pqvUFHnK6e62-08Ja0sdQoZ9qDgACKQADJHFiGiKockiM5SMwOgQ',
    'CAACAgIAAxkBAAEbzN5pqvUHvwjUmtZ8qLjfdbKeLOYQigACHQADwDZPE17YptxBPd5IOgQ'
]