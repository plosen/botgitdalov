import telebot # библиотека telebot
from config import token # импорт токена

bot = telebot.TeleBot(token) 

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hi, I am Kirill.")

@bot.message_handler(commands=['ban_mruser'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение 
        chat_id = message.chat.id # сохранение id чата
         # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status 
         # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    # Проверка на наличие "https://" в тексте сообщения
    if "https://" in message.text:
        # Сохранение данных о пользователе
        user_info = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "text": message.text
        }

        # Сохранение данных пользователя (например, в файл)
        with open("banned_users.txt", "a") as file:
            file.write(f"{user_info}\n")

        # Бан пользователя
        bot.kick_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)

        # Уведомление о бане
        bot.reply_to(message, "Вы были забанены за отправку запрещенных ссылок.")
    else:
        # Ответ на обычное сообщение
        bot.reply_to(message, message.text)

bot.infinity_polling(none_stop=True)
