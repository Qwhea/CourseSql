from database import create_tables
from telegram import bot

if __name__ == "__main__":
    create_tables()
    print("✅ Все таблицы успешно созданы.")

    bot.polling()