import config
import json
import logging
import telebot
import os

from flask import Flask, request


bot = telebot.TeleBot(config.token)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

with open('chats.json') as f:
    chat_user = json.load(f)


@bot.message_handler(commands=['add'])
def command_help(message):
    cid = message.chat.id
    uname = message.from_user.username
    if str(cid) not in chat_user:
        chat_user[str(cid)] = []
    if '@' + uname not in chat_user[str(cid)]:
        chat_user[str(cid)].append('@' + uname)
    bot.send_message(cid, 'Added ' + uname)


@bot.message_handler(commands=['all'])
def command_help(message):
    cid = message.chat.id
    bot.send_message(cid, ' '.join(list(chat_user[str(cid)])))
    with open('chats.json', 'w') as f:
        json.dump(chat_user, f)


@server.route('/' + config.token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://sleepy-dawn-47510.herokuapp.com/' + config.token)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))