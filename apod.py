#!/home/sean/anaconda3/bin/python

import requests
import json
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from configparser import ConfigParser

home = str(Path.home())

# Read from config file
parser = ConfigParser()
# configFilePath = home + '.apod/apod.settings'
configFilePath = 'apod.settings'
parser.read(configFilePath)
scrn_width = int(parser.get('apod_config', 'Screen_Size').split(',')[0])
scrn_length = int(parser.get('apod_config', 'Screen_Size').split(',')[1])
num_chars = int(parser.get('apod_config', 'Num_Characters'))
api_key = parser.get('apod_config', 'API_Key')

url = 'https://api.nasa.gov/planetary/apod'
data = json.loads(requests.get(url + '?api_key=' + api_key).text)
image = Image.open(requests.get(data['hdurl'], stream=True).raw).resize(
    (scrn_width, scrn_length), resample=0)
draw = ImageDraw.Draw(image)
exp_font = ImageFont.truetype("arial.ttf", 14, encoding="unic")
title_font = ImageFont.truetype("arial.ttf", 24, encoding="unic")
lines = textwrap.wrap(data['explanation'], width=num_chars)
y_text = (scrn_length / 6) * 5

draw.text((20, y_text - 30), data['title'], fill='white', font=title_font)

for line in lines:
    width, height = exp_font.getsize(line)
    draw.text((20, y_text), line, font=exp_font, fill='white')
    y_text += height

image.save(home + "/.apod/apod.png", 'PNG')
os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri file://" +
          home + "/.apod/apod.png")
