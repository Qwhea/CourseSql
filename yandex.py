import requests

from config import YANDEX_DICTIONARY_URL, YANDEX_API_KEY

def get_translation_yandex(word):
    """Получение перевода слова с помощью Яндекс.Словаря"""

    try:
        if any('а' <= c.lower() <= 'я' for c in word):
            lang = 'ru-en'
        else:
            lang = 'en-ru'

        response = requests.get(YANDEX_DICTIONARY_URL, params={
            'key': YANDEX_API_KEY,
            'lang': lang,
            'text': word.strip()
        }, timeout=5)

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}, {response.text}")
            return None

        data = response.json()
        if 'def' not in data or len(data['def']) == 0:
            return None

        tr = data['def'][0]['tr']
        if len(tr) == 0:
            return None

        translation = tr[0]['text']
        return translation

    except Exception as e:
        print(f"Ошибка при запросе к Yandex.Dictionary: {e}")
        return None