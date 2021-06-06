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
Hi! I want to help you tag your friends in group chats.\n\n
/all or @all - I will tag all the known chat participants (I know the participants who wrote something \
after I came to the chat, or the people who were added with the /add command)\n\n
/add - add people manually for tagging them with /all after\n\n
/group - add an alias for a group. For example, you'll be able to tag all boys in \
the chat by @boys, and all girls by @girls\n
For example, after /group command(in the next message) write "boys @Bob @Steve @Mark" and bot will tag them \
if any message will contain @boys\n\n
/info - learn about current known members and aliases\n\n
For complaints and suggestions - write to @MikeHeller\n\n
Public code repository - https://github.com/corwinnn/allbot
'''
