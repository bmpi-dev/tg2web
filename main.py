from peewee import *
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.utils import get_display_name
from telethon.network import ConnectionTcpAbridged
from getpass import getpass
import telethon.sync
import datetime
import os
import sys
import time
import glob

channels = ['web_cpc', 'bmpi365', 'improve365']

db = SqliteDatabase('channels.db')

class BaseModel(Model):
    class Meta:
        database = db

class Message(BaseModel):
    msg_id = CharField()
    channel = CharField()
    content = TextField()
    type = CharField()
    post_date = DateTimeField()

db.connect()
db.create_tables([Message])

def sprint(string, *args, **kwargs):
    """Safe Print (handle UnicodeEncodeErrors on some terminals)"""
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore')\
                       .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)

def download_media_by_msg(client, channel, msg):
    """Given a message ID, finds the media this message contained and
        downloads it.
    """
    try:
        print('Downloading media to media/...')
        os.makedirs('media', exist_ok=True)
        file_name = 'media/' + channel + '-' + str(msg.id)
        file_name_check = file_name + ".*"
        if len(glob.glob(file_name_check)) > 0:
            return
        output = client.download_media(
            msg.media,
            file=file_name
        )
        print('Media downloaded to {}!'.format(output))
    except:
        print("download message media failure, message id is " + msg.id)

def get_local_last_msg_id(channel_entity):
    try:
        msg = Message.select(Message)\
        .where(Message.channel == channel_entity.username)\
        .order_by(Message.msg_id.desc()).get()
        if msg is not None:
            return msg.msg_id
    except:
        pass

def is_message_exists(channel, msg_id):
    try:
        msg = Message.select(Message)\
        .where(Message.channel == channel and Message.msg_id == msg_id)\
        .get()
        if msg is not None:
            return True
    except:
        pass
    return False

def get_remote_last_msg_id(channel_entity):
    msg = get_history_message(channel_entity, 0, 1)[0]
    if msg is not None:
        return msg.id

def calc_offset_limit(channel_entity):
    local_msg_id = get_local_last_msg_id(channel_entity)
    remote_msg_id = get_remote_last_msg_id(channel_entity)
    if remote_msg_id <= local_msg_id:
        return None
    return remote_msg_id, remote_msg_id - local_msg_id
    

def get_env(name, default_value=None):
    if name in os.environ:
        return os.environ[name]
    return default_value

def get_history_message(channel_entity, offset_id, limit):
    msgs = client(GetHistoryRequest(
            peer=channel_entity,
            limit=limit,
            offset_date=None,
            offset_id=offset_id,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0)).messages
    return msgs

class ChannelTelegramClient(TelegramClient):

    def __init__(self, session_user_id, api_id, api_hash,
                 proxy=None):
        """
        Initializes the InteractiveTelegramClient.
        :param session_user_id: Name of the *.session file.
        :param api_id: Telegram's api_id acquired through my.telegram.org.
        :param api_hash: Telegram's api_hash.
        :param proxy: Optional proxy tuple/dictionary.
        """

        # The first step is to initialize the TelegramClient, as we are
        # subclassing it, we need to call super().__init__(). On a more
        # normal case you would want 'client = TelegramClient(...)'
        super().__init__(
            # These parameters should be passed always, session name and API
            session_user_id, api_id, api_hash,

            # You can optionally change the connection mode by passing a
            # type or an instance of it. This changes how the sent packets
            # look (low-level concept you normally shouldn't worry about).
            # Default is ConnectionTcpFull, smallest is ConnectionTcpAbridged.
            connection=ConnectionTcpAbridged,

            # If you're using a proxy, set it here.
            proxy=proxy
        )

        # Calling .connect() may raise a connection error False, so you need
        # to except those before continuing. Otherwise you may want to retry
        # as done here.
        print('Connecting to Telegram servers...')

        try:
            self.connect()
        except IOError:
            # We handle IOError and not ConnectionError because
            # PySocks' errors do not subclass ConnectionError
            # (so this will work with and without proxies).
            print('Initial connection failed. Retrying...')
            self.connect()

        # If the user hasn't called .sign_in() or .sign_up() yet, they won't
        # be authorized. The first thing you must do is authorize. Calling
        # .sign_in() should only be done once as the information is saved on
        # the *.session file so you don't need to enter the code every time.
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            user_phone = input('Enter your phone: ')
            self.sign_in(user_phone)

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = self.sign_in(code=code)

                # Two-step verification may be enabled, and .sign_in will
                # raise this error. If that's the case ask for the password.
                # Note that getpass() may not work on PyCharm due to a bug,
                # if that's the case simply change it for input().
                except SessionPasswordNeededError:
                    pw = getpass('Two step verification is enabled. '
                                 'Please enter your password: ')

                    self_user = self.sign_in(password=pw)

    def run(self):
        for channel in channels:
            channel_entity= client.get_entity(channel)
            messages = get_history_message(channel_entity, 100, 100)

            for msg in reversed(messages):
                # Note how we access .sender here. Since we made an
                # API call using the self client, it will always have
                # information about the sender. This is different to
                # events, where Telegram may not always send the user.
                name = get_display_name(msg.sender)

                # Format the message content
                if getattr(msg, 'media', None):
                    content = '<{}> {}'.format(
                        type(msg.media).__name__, msg.message)
                    download_media_by_msg(self, channel, msg)

                elif hasattr(msg, 'message'):
                    content = msg.message
                elif hasattr(msg, 'action'):
                    content = str(msg.action)
                else:
                    # Unknown message, simply print its class name
                    content = type(msg).__name__

                # And print it to the user
                sprint('[{}:{}] (ID={}) {}: {}'.format(
                    msg.date.hour, msg.date.minute, msg.id, name, content))
                if content is not None:
                    if (not is_message_exists(channel, msg.id)):
                        save_msg = Message(msg_id=msg.id, channel=channel, content=content, type=type(msg.media).__name__, post_date=msg.date)
                        save_msg.save()

if __name__ == '__main__':
    SESSION = os.environ.get('TG_SESSION', 'bmpi')
    API_ID = get_env('TG_API_ID')
    API_HASH = get_env('TG_API_HASH')
    client = ChannelTelegramClient(SESSION, API_ID, API_HASH)
    client.run()
    print(get_local_last_msg_id(client.get_entity('web_cpc')))
