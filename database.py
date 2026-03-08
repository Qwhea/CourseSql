from datetime import date, datetime, timedelta

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models import (
    Achievements,
    Base,
    DateLogins,
    UserAchievements,
    Users,
    UserStatistics,
    UserWords,
    Words,
)

engine = create_engine(DATABASE_URL, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

def create_tables():
    """Создание таблиц"""
    Base.metadata.create_all(engine)
    init_data()

def init_data():
    """Заполнение таблицы тестовыми данными"""
    try:
        if session.query(Words).count() == 0:
            words_data = [
                ("hello", "привет"),
                ("world", "мир"),
                ("cat", "кот"),
                ("dog", "собака"),
                ("house", "дом"),
                ("car", "машина"),
                ("book", "книга"),
                ("friend", "друг"),
                ("sun", "солнце"),
                ("water", "вода")
            ]
            for word, translation in words_data:
                session.add(Words(word=word, translation=translation))
            session.commit()
            print("✅ Таблица 'words' заполнена тестовыми данными.")

        if session.query(Achievements).count() == 0:
            achievements_data = [
                ("Новичок", "Правильных ответов 10", "total_correct", 10),
                ("Ученик", "Правильных ответов 50", "total_correct", 50),
                ("Мастер", "Правильных ответов 100", "total_correct", 100),
                ("Главное не сдаваться!", "Первая ошибка", "total_wrong", 1),
                ("Отличник", "Занимайся 5 дней подряд", "max_streak", 10),
                ("Начинающий лингвист", "Выучено 5 слов", "total_words", 5),
                ("Полиглот в деле", "Выучено 10 слов", "total_words", 10)
            ]
            for name, desc, a_type, goal in achievements_data:
                session.add(Achievements(
                    name=name,
                    description=desc,
                    achievement_type=a_type,
                    goal=goal
                ))
            session.commit()
            print("✅ Таблица 'achievements' заполнена тестовыми данными.")
    except Exception as e:
        print(f"❌ Ошибка при заполнении данных: {e}")
        session.rollback()

def get_user(telegram_id):
    """Получение пользователя по телеграм id"""
    try:
        user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
        if user:
            return user
        return False
    except Exception as e:
        print(f'Ошибка при получении пользователя: {e}')

def create_user(telegram_id, username):
    """Создание пользователя"""
    try:
        user = get_user(telegram_id)
        if not user:
            new_user = Users(
                telegram_id=telegram_id,
                username=username,
                created_at=datetime.utcnow()
            )
            session.add(new_user)
            session.flush()

            stats = UserStatistics(
                userId=new_user.id
            )
            session.add(stats)
            session.commit()
            print(f"Пользователь {username or telegram_id} добавлен в БД.")
        else:
            print(f"Пользователь с telegram_id={telegram_id} уже существует.")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
        session.rollback()

def get_stats(telegram_id):
    """Получение статистики"""
    try:
        user = get_user(telegram_id)
        if user:
            user = (session.query(Users)
                    .filter(Users.telegram_id == telegram_id)
                    .first())
            stats = (session.query(UserStatistics)
                     .filter(UserStatistics.userId == user.id)
                     .first())
            return stats
    except Exception as e:
        print(f'Ошибка при получении статистики: {e}')

def get_translation_mode(telegram_id):
    """Получение режима перевода"""
    user = get_user(telegram_id)
    return user.translation_mode if user else None

def set_translation_mode(telegram_id, mode):
    """Установка режима перевода"""
    try:
        if mode not in ['en-ru', 'ru-en']:
            return
        user = get_user(telegram_id)
        if user:
            user.translation_mode = mode
            session.commit()
    except Exception as e:
        print(f'Ошибка установки режима перевода: {e}')
        session.rollback()

def add_word_to_learn(word, telegram_id):
    """Добавление новых слов для пользователя"""
    try:
        user = get_user(telegram_id)
        if user:
            word_obj = session.query(Words).filter(Words.word == word).first()

            if not word_obj:
                print(f"Слово '{word}' не найдено в таблице Words.")
                return

            existing = session.query(UserWords).filter(
                UserWords.wordId == word_obj.id,
                UserWords.userId == user.id
            ).first()

            if not existing:
                user_word = UserWords(
                    wordId=word_obj.id,
                    userId=user.id
                )
                session.add(user_word)
                session.commit()
                print(f'Слово добавлено пользователю: {user.id}')
            else:
                print('Слово уже добавлено пользователю.')
        else:
            print('Пользователь не найден')
    except Exception as e:
        print(f'Ошибка добавления нового слова: {e}')
        session.rollback()

def get_words(telegram_id):
    """Список всех слов пользователя"""
    try:
        user = get_user(telegram_id)
        if user:
            words = (session.query(Words)
                .join(UserWords, UserWords.wordId == Words.id)
                .filter(UserWords.userId == user.id)
                .all()
            )
            return words
    except Exception as e:
        print(f"Ошибка получения списка изучаемых слов:  {e}")

def get_variants(telegram_id, word):
    """Получить варианты кроме текущего слова"""
    try:
        user = get_user(telegram_id)
        if user:
            variants = (session.query(Words)
                .join(UserWords, UserWords.wordId == Words.id)
                .order_by(func.random())
                .filter(UserWords.userId == user.id)
                .filter(Words.word != word)
                .limit(3).all()
            )
            return variants
    except Exception as e:
        print(f'Ошибка получения вариантов :{e})')

def get_random_word(telegram_id):
    """Получить случайное слово"""
    try:
        user = get_user(telegram_id)
        if not user:
            return
        learned_words = (session.query(UserWords.wordId)
            .filter(UserWords.userId == user.id))
        return (session.query(Words)
            .filter(~Words.id.in_(learned_words))
            .order_by(func.random())
            .first())

    except Exception as e:
        print(f"Ошибка при получении случайного слова:{e}")

def check_achievements(telegram_id, type, value):
    """Проверка на новые достижения (Возращает полученное достижение)"""
    try:
        user = get_user(telegram_id)
        if not user:
           return
        achievement = session.query(Achievements).filter(
            Achievements.achievement_type == type,
            Achievements.goal <= value
        ).first()

        if not achievement:
            return None

        existing = session.query(UserAchievements).filter(
            UserAchievements.user_id == user.id,
            UserAchievements.achievement_id == achievement.id
        ).first()

        if not existing:
            new_record = UserAchievements(
                user_id=user.id,
                achievement_id=achievement.id,
                achieve_date = datetime.utcnow()
            )
            session.add(new_record)
            session.commit()
            print(f"Пользователь {telegram_id} получил достижение: {achievement.name}")
            return achievement
    except Exception as e:
        print(f"Ошибка при проверке достижения: {e}")
        session.rollback()
        return None

def get_user_achievements(telegram_id):
    """Получить все достижения пользователя"""
    try:
        user = get_user(telegram_id)

        if not user:
            return

        achievements = (session.query(Achievements)
                      .join(UserAchievements, Achievements.id == UserAchievements.achievement_id)
                      .filter(UserAchievements.user_id == user.id)
                      .all())
        return achievements
    except Exception as e:
        print(f'Ошибка получения достижений: {e}')
        return []

def update_statistics(telegram_id, statistic):
    """Обновить статистику пользователя"""
    user = get_user(telegram_id)
    try:
        if user:
            stats = session.query(UserStatistics).filter(UserStatistics.userId == user.id).first()
            if statistic == 'correct':
                stats.total_correct += 1
                session.commit()
            elif statistic == 'wrong':
                stats.total_wrong += 1
                session.commit()
            elif statistic == 'words':
                stats.total_words += 1
                session.commit()
            elif statistic == 'sub_words':
                stats.total_words -= 1
            else:
                print('Неверный параметр')

    except Exception as e:
        print(f'Ошибка обновления статистики у пользователя: {user.id}, ({statistic}): {e}')
        session.rollback()

def delete_word_from_learn(telegram_id, word):
    """Удаляем слово у пользователя"""
    try:
        user = get_user(telegram_id)
        if not user:
            print('Пользователь не найден')
            return

        word_id = session.query(Words).filter(Words.word == word).first().id
        if not word_id:
            print('Слово не найдено')
            return

        (session.query(UserWords)
            .filter(UserWords.wordId == word_id, UserWords.userId == user.id)
            .delete())
        
        session.commit()
        print(f"Слово '{word}' удалено у пользователя {telegram_id}.")

    except Exception as e:
        print(f'Ошибка удаления слова из изучаемого списка: {e}')
        session.rollback()

def update_streak(telegram_id):
    """Обновление количества входов подряд"""
    try:
        user = get_user(telegram_id)
        if not user:
            return
        logins = (session.query(func.date(DateLogins.date_login))
            .filter(DateLogins.userId == user.id)
            .order_by(func.date(DateLogins.date_login).desc())
            .all())

        if not logins:
            return

        login_dates = {login[0] for login in logins}

        current_streak = 0
        check_date = date.today()

        while check_date in login_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        stats = get_stats(telegram_id)
        stats.current_streak = current_streak

        if current_streak > stats.max_streak:
            stats.max_streak = current_streak

        session.commit()

    except Exception as e:
        print(f'Ошибка обновления серии: {e}')
        session.rollback()

def is_first_login_today(telegram_id):
    """Проверяет первый ли это вход в тренировку пользователем"""
    try:
        user = get_user(telegram_id)
        if user:
            today = date.today()
            today_login = (session.query(DateLogins)
                           .filter(DateLogins.userId == user.id,
                                   func.date(DateLogins.date_login) == today)
                           .count())
            return today_login == 0
    except Exception as e:
        print(f'Ошибка проверки входа: {e}')
        return False

def login(telegram_id):
    """Первый вход пользователя за день"""
    try:
        user = get_user(telegram_id)
        if not user:
            return

        if is_first_login_today(telegram_id):
            new_login = DateLogins(
                userId = user.id,
                date_login = datetime.utcnow()
            )
            session.add(new_login)
            session.commit()

            update_streak(telegram_id)

            print(f'Первый вход за сегодня для пользователя: {user.id}')
    except Exception as e:
        print(f'Ошибка входа пользователя: {e}')
        session.rollback()


def add_word_to_db_and_user(telegram_id, word, translation, direction):
    """Добавить новое слово и связать его со списком изученных"""
    try:
        user = get_user(telegram_id)
        if not user:
            print("Пользователь не найден.")
            return False

        word_en = word if direction == 'en_to_ru' else translation
        word_ru = translation if direction == 'en_to_ru' else word

        existing_word = (session.query(Words)
                         .filter(func.lower(Words.word) == func.lower(word_en))
                         .first())

        if not existing_word:
            new_word = Words(word=word_en, translation=word_ru)
            session.add(new_word)
            session.flush()
            word_id = new_word.id
        else:
            word_id = existing_word.id

        existing_user_word = session.query(UserWords).filter(
            UserWords.userId == user.id,
            UserWords.wordId == word_id
        ).first()

        if not existing_user_word:
            user_word = UserWords(userId=user.id, wordId=word_id)
            session.add(user_word)

        session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении слова: {e}")
        session.rollback()
        return False