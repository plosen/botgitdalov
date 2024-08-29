import telebot
from config import token
import time

bot = telebot.TeleBot(token)


# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hi, I am Kirill, your admin bot.")


# Бан пользователя при ответе на его сообщение
@bot.message_handler(commands=['ban_mruser'])
def ban_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status in ['administrator', 'creator']:
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


# Предупреждение пользователя (ограниченное число предупреждений)
warnings = {}


@bot.message_handler(commands=['warn'])
def warn_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
        chat_id = message.chat.id

        warnings[user_id] = warnings.get(user_id, 0) + 1

        if warnings[user_id] >= 3:  # Если 3 предупреждения — бан
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{username} забанен за нарушения.")
            del warnings[user_id]  # Сброс предупреждений после бана
        else:
            bot.reply_to(message, f"Пользователь @{username} получил предупреждение {warnings[user_id]}/3.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


# Временный бан пользователя
@bot.message_handler(commands=['tempban'])
def temp_ban_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        try:
            # Временный бан на 1 час
            bot.ban_chat_member(chat_id, user_id, until_date=int(time.time()) + 3600)
            bot.reply_to(message, f"Пользователь временно забанен на 1 час.")
        except Exception as e:
            bot.reply_to(message, f"Не удалось временно забанить пользователя: {e}")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


# Очистка сообщений
@bot.message_handler(commands=['clear'])
def clear_messages(message):
    try:
        count = int(message.text.split()[1])  # Количество сообщений для удаления
        for _ in range(count):
            bot.delete_message(message.chat.id, message.message_id - _)
        bot.reply_to(message, f"Удалено {count} сообщений.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Используйте /clear <количество сообщений>.")


# Мут и размут пользователей
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
        bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был замучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
        bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был размучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


# Получение информации о пользователе
@bot.message_handler(commands=['userinfo'])
def user_info(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_info = f"ID: {user.id}\nUsername: @{user.username}\nИмя: {user.first_name}\nФамилия: {user.last_name}"
        bot.reply_to(message, user_info)
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя.")


# Приветствие нового пользователя
@bot.message_handler(content_types=['new_chat_members'])
def greet_new_user(message):
    bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}!')
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)


# Хэндлер для сообщений с запрещенными ссылками
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if "https://" in message.text:
        user_info = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "text": message.text
        }

        with open("banned_users.txt", "a") as file:
            file.write(f"{user_info}\n")

        bot.kick_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
        bot.reply_to(message, "Вы были забанены за отправку запрещенных ссылок.")
    else:
        bot.reply_to(message, message.text)


# Бесконечный опрос
bot.infinity_polling(none_stop=True)
