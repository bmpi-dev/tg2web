from db import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import pystache
import os
import sys
import json

msgs_dict = {'items': []}

out_html_dir = './html/'

renderer = pystache.Renderer()
        
for msg in Message.select(Message).order_by(Message.post_date.desc()):
    msgs_dict['items'].append(model_to_dict(msg))
    channel_html_dir = out_html_dir + msg.channel + '/'
    os.makedirs(channel_html_dir, exist_ok=True)
    with open(channel_html_dir + str(msg.msg_id) + '.html', 'w') as f:
        item_html = renderer.render_path('item.mustache', msg)
        f.write(item_html)

index_html = renderer.render_path('index.mustache', msgs_dict)

with open(out_html_dir + 'index.html', 'w') as f:
    f.write(index_html)
