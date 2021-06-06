import os

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE = os.environ.get('DATABASE')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

TOKEN = os.environ.get('BOT_TOKEN')
APPLINK = os.environ.get('LINK')

ALL_ALIAS = os.environ.get('ALL_ALIAS')
ALIAS_START = '@'

HELLO_TEXT = '''
Hi! I want to help you to tag your friends in group chats.\n\n
/all or @all - I'll tag all known members of the chat (I know members that have written something  in chat after the moment I've come
to the chat or people that were added by /add command.\n\n
/add - add people manually\n\n
/group - add alias for a group. For example, you'll be able to call all boys in the chat by @boys, and all girls by @girls\n\n
/info - learn about current known members and aliases\n\n
For сomplaints and suggestions - write to @MikeHeller\n\n
Public code repository - https://github.com/corwinnn/allbot
'''
