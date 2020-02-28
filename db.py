from peewee import *

db = SqliteDatabase('channels.db')

class BaseModel(Model):
    class Meta:
        database = db

class Message(BaseModel):
    msg_id = IntegerField()
    channel = CharField()
    content = TextField()
    media_path = TextField()
    type = CharField()
    is_img = BooleanField(default=False)
    post_date = DateTimeField()

db.connect()
db.create_tables([Message])
