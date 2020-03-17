import config
import json
import telebot
import os

bot = telebot.TeleBot(config.token)

with open('chats.json') as f:
    chat_user = json.load(f)


@bot.message_handler(commands=['add'])
def command_help(message):
    cid = message.chat.id
    uname = message.from_user.username
    if str(cid) not in chat_user:
        chat_user[str(cid)] = []
    chat_user[str(cid)].append('@' + uname)
    bot.send_message(cid, 'Added ' + uname)


@bot.message_handler(commands=['all'])
def command_help(message):
    cid = message.chat.id
    bot.send_message(cid, ' '.join(list(chat_user[str(cid)])))
    with open('chats.json', 'w') as f:
        json.dump(chat_user, f)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
