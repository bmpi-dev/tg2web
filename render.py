from db import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import pystache
import os
import sys
import json

msgs_dict = {'items': []}

out_html_dir = './html/'

channels = ['web_cpc', 'bmpi365', 'improve365']

renderer = pystache.Renderer()
        
for msg in Message.select(Message).order_by(Message.post_date.desc()):
    msgs_dict['items'].append(model_to_dict(msg))
    if (not msg.is_render):
        channel_html_dir = out_html_dir + msg.channel + '/'
        os.makedirs(channel_html_dir, exist_ok=True)
        with open(channel_html_dir + str(msg.msg_id) + '.html', 'w') as f:
            item_html = renderer.render_path('item.mustache', msg)
            f.write(item_html)
        msg.is_render = True
        msg.save()

msgs_dict['items'] = msgs_dict['items'][:20]
msgs_dict['is_home'] = True
index_html = renderer.render_path('index.mustache', msgs_dict)

with open(out_html_dir + 'index.html', 'w') as f:
    f.write(index_html)

for channel in channels:
    msgs_dict = {'items': []}
    if channel == 'web_cpc':
        msgs_dict['is_cpc'] = True
    if channel == 'bmpi365':
        msgs_dict['is_bmpi'] = True
    if channel == 'improve365':
        msgs_dict['is_i365'] = True
    for msg in Message.select(Message)\
    .where(Message.channel == channel)\
    .order_by(Message.post_date.desc()):
        msgs_dict['items'].append(model_to_dict(msg))
    channel_index_html = renderer.render_path('index.mustache', msgs_dict)
    with open(out_html_dir + channel + '/index.html', 'w') as f:
        f.write(channel_index_html)
