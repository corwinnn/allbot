import logging
import os
import telebot

from flask import Flask, request

from db import SQLighter

TOKEN = os.environ.get('BOT_TOKEN')
APPLINK = os.environ.get('LINK')

ALL_ALIAS = os.environ.get('ALL_ALIAS')
ALIAS_START = '@'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

db = SQLighter()


def add_user(func):
    """
    Decorator for adding a user to the database if we see him for the first time
    """

    def wrapper(*args, **kwargs):
        message = args[0]
        uid = message.from_user.id
        cid = message.chat.id
        name = message.from_user.username
        if not db.subscriber_exists(uid):
            db.add_subscriber(uid, name)
        if cid < 0:  # group chats have cid < 0, personal chats have cid > 0
            db.add_member(cid, '@' + name, ALL_ALIAS)
            return func(*args, **kwargs)
        else:
            bot.send_message(cid, 'I was born for group chats, please use me only in groups.')
            send_help(cid)

    return wrapper


@bot.message_handler(commands=['start', 'help'])
@add_user
def command_help(message):
    """
    Command for help message
    """
    cid = message.chat.id
    send_help(cid)


def send_help(cid):
    """
    Send help message
    :param cid: telegram chat id
    """
    text = '''
        Hi! I want to help you to call your friends in group chats.\n
        /all or @all - I'll tag all known members of the chat (I know members that have written something after adding me
        to the chat or people that were added by /add command.\n
        /add - add people manually\n
        /group - add alias for a group. For example, you'll be able to call all boys in the chat by @boys, and all girls by @girls\n
        /info - learn about current known members and aliases\n
        For сomplaints and suggestions - write to @MikeHeller\n
        Public code repository - https://github.com/corwinnn/allbot
        '''
    bot.send_message(cid, text)


@bot.message_handler(commands=['add'])
@add_user
def command_add(message):
    """
    Command for adding users to user list after /all command
    """
    msg = bot.reply_to(message, "Name members you want to be mentioned after /all command. Your answer should be like "
                                "@member1 @member2...")
    bot.register_next_step_handler(msg, process_members)


@add_user
def process_members(message):
    """
    Command for adding users to user list after /all command
    """
    cid = message.chat.id
    names = message.text.split()
    if any([name[0] != '@' for name in names]):
        bot.send_message(cid, "Please, list like this: @member1 @member2 ...")
        return

    for name in names:
        db.add_member(cid, name, ALL_ALIAS)


@bot.message_handler(commands=['all'])
@add_user
def command_all(message):
    """
    Tag all known chat members
    """
    cid = message.chat.id
    members = db.get_alias_list(cid, ALL_ALIAS)
    if members:
        bot.send_message(cid, ', '.join(members))


@bot.message_handler(commands=['info'])
@add_user
def command_info(message):
    """
    Send a list of known chat members and aliases
    """
    cid = message.chat.id
    info_message = 'Nice chat! I have such knowledge:\n\n'

    member_group = db.member_group_list(cid)
    info_message += 'All: ' + ', '.join([member for member, group in member_group if group == ALL_ALIAS]) + '\n\n'

    groups = [group for _, group in member_group if group != ALL_ALIAS]
    for group_name in groups:
        info_message += f'{group_name}: ' + \
                        ', '.join([member for member, group in member_group if group == group_name]) + '\n'
    bot.send_message(cid, info_message)


@bot.message_handler(commands=['group'])
@add_user
def command_group(message):
    """
    Create an alias for a group of members
    """
    msg = bot.reply_to(message, "Name group and members. Your answer should be like group_name @member1 @member2 ...")
    bot.register_next_step_handler(msg, process_group_name)


@add_user
def process_group_name(message):
    """
    Create an alias for a group of members
    """
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


@bot.message_handler(content_types=['text'])
@add_user
def get_text_messages(message):
    """
    Checking messages for aliases
    """
    cid = message.chat.id
    words = message.text.split()
    aliases = [w[len(ALIAS_START):] for w in words if w.startswith(ALIAS_START)]
    if aliases:
        for alias in aliases:
            if alias == 'all':
                alias = ALL_ALIAS  # processing @all
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
