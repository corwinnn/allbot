import json
import logging
import os
import telebot

from flask import Flask, request

from db import SQLighter

TOKEN = os.environ.get('BOT_TOKEN')
APPLINK = os.environ.get('LINK')

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
db = SQLighter()


def add_user(func):
    def wrapper(*args, **kwargs):
        message = args[0]
        uid = message.from_user.id
        name = message.from_user.username
        if not db.subscriber_exists(uid):
            db.add_user(uid, name)
        return func(*args, **kwargs)


with open('chats.json') as f:
    chat_user = json.load(f)

with open('groups.json') as f:
    chat_group = json.load(f)


@bot.message_handler(commands=['add'])
@add_user
def command_help(message):
    cid = message.chat.id
    uname = message.from_user.username
    if str(cid) not in chat_user:
        chat_user[str(cid)] = []
    if '@' + uname not in chat_user[str(cid)]:
        chat_user[str(cid)].append('@' + uname)
    bot.send_message(cid, 'Added ' + uname)


@bot.message_handler(commands=['all'])
@add_user
def command_help(message):
    cid = message.chat.id
    if str(cid) in chat_user:
        bot.send_message(cid, ' '.join(list(chat_user[str(cid)])))
    with open('chats.json', 'w') as f:
        json.dump(chat_user, f)


@bot.message_handler(commands=['info'])
@add_user
def command_help(message):
    cid = message.chat.id
    greet = 'Nice chat! I know them: '
    if str(cid) in chat_user:
        people = ' '.join(list(chat_user[str(cid)])) + '\n' + 'Groups:\n'
    else:
        people = 'Nobody' + '\n' + 'Groups:\n'
    if str(cid) in chat_group:
        groups = '\n'.join([(g + ': ' + ' '.join(list(chat_group[str(cid)][g]))) for g in chat_group[str(cid)]])
    else:
        groups = 'Nothing'
    bot.send_message(cid, greet + people + groups)


@bot.message_handler(commands=['group'])
@add_user
def command_help(message):
    msg = bot.reply_to(message, "Name group and members. Your answer should be like group_name @member1 @member2...")
    bot.register_next_step_handler(msg, process_group_name)


@bot.message_handler(commands=['log'])
@add_user
def command_help(message):
    bot.send_message(message.chat.id, str(chat_group))
    bot.send_message(message.chat.id, str(chat_user))


def process_group_name(message):
    cid = message.chat.id
    text = message.text.split()
    if len(text) == 1:
        bot.send_message(cid, "No members")
        return
    if len(text) > 10:
        bot.send_message(cid, "Too many members")
        return

    if str(cid) not in chat_group:
        chat_group[str(cid)] = {}
    chat_group[str(cid)][text[0]] = []
    for user in text[1:]:
        if user in chat_user[str(cid)]:
            chat_group[str(cid)][text[0]].append(user)
        else:
            bot.send_message(cid, "I don't know this guy: " + user)


@bot.message_handler(content_types=['text'])
@add_user
def get_text_messages(message):
    cid = message.chat.id
    text = message.text
    if str(cid) in chat_group and text in chat_group[str(cid)]:
        bot.send_message(cid, ' '.join(list(chat_group[str(cid)][text])) or 'Empty group')
        with open('groups.json', 'w') as f:
            json.dump(chat_group, f)
    uname = message.from_user.username
    if str(cid) not in chat_user:
        chat_user[str(cid)] = []
    if '@' + uname not in chat_user[str(cid)]:
        chat_user[str(cid)].append('@' + uname)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APPLINK + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
