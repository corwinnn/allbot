import json
import logging
import os
import telebot

from flask import Flask, request

from db import SQLighter

TOKEN = os.environ.get('BOT_TOKEN')
APPLINK = os.environ.get('LINK')

ALL_ALIAS = os.environ.get('ALL_ALIAS')

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
db = SQLighter()


def add_user(func):
    def wrapper(*args, **kwargs):
        message = args[0]
        uid = message.from_user.id
        cid = message.chat.id
        name = message.from_user.username
        if not db.subscriber_exists(uid):
            db.add_subscriber(uid, name)
        if cid < 0:
            db.add_member(cid, '@' + name, ALL_ALIAS)
            return func(*args, **kwargs)
        else:
            bot.send_message(cid, 'I was born for group chats, please use me only in groups.')

    return wrapper


@bot.message_handler(commands=['add'])
@add_user
def command_help(message):
    msg = bot.reply_to(message, "Name members you want to be mentioned after /all command. Your answer should be like "
                                "@member1 @member2...")
    bot.register_next_step_handler(msg, process_members)


@bot.message_handler(commands=['all'])
@add_user
def command_all(message):
    cid = message.chat.id
    members = db.get_alias_list(cid, ALL_ALIAS)
    if members:
        bot.send_message(cid, ', '.join(members))


@bot.message_handler(commands=['info'])
@add_user
def command_help(message):
    cid = message.chat.id
    greet = 'Nice chat! I have such knowledge:\n\n'

    member_group = db.member_group_list(cid)
    greet += 'All: ' + ', '.join([member for member, group in member_group if group == ALL_ALIAS]) + '\n\n'

    groups = [group for _, group in member_group if group != ALL_ALIAS]
    for group_name in groups:
        greet += f'{group_name}: ' + ', '.join([member for member, group in member_group if group == group_name]) + '\n'
    bot.send_message(cid, greet)


@bot.message_handler(commands=['group'])
@add_user
def command_help(message):
    msg = bot.reply_to(message, "Name group and members. Your answer should be like group_name @member1 @member2 ...")
    bot.register_next_step_handler(msg, process_group_name)


@add_user
def process_group_name(message):
    cid = message.chat.id
    text = message.text.split()
    if len(text) == 1:
        bot.send_message(cid, "No members")
        return
    alias = text[0]
    names = text[1:]
    if any([name[0] != '@' for name in names]):
        bot.send_message(cid, "Please, list like this: group_name @member1 @member2 ...")
        return

    db.create_alias(cid, alias, names)


@add_user
def process_members(message):
    cid = message.chat.id
    names = message.text.split()
    if any([name[0] != '@' for name in names]):
        bot.send_message(cid, "Please, list like this: @member1 @member2 ...")
        return

    for name in names:
        db.add_member(cid, name, ALL_ALIAS)


@bot.message_handler(content_types=['text'])
@add_user
def get_text_messages(message):
    cid = message.chat.id
    words = message.text.split()
    print(words)
    aliases = [w[2:] for w in words if w.startswith('@@')]
    print(aliases)
    if aliases:
        for alias in aliases:
            members = db.get_alias_list(cid, alias)
            if members:
                bot.send_message(cid, ', '.join(members))


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
