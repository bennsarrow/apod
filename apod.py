#!/home/srbrown/anaconda3/bin/python3

import requests
import json
import textwrap
import os
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from configparser import ConfigParser

# set the home path
home = str(Path.home())

# setup logging
logging.basicConfig(filename=home + '/.apod/apod.log',
                    filemode='w',
                    format='%(asctime)s %(message)s',
                    level=logging.INFO)

# Read from config file
parser = ConfigParser()
configFilePath = home + '/.apod/apod.settings'
parser.read(configFilePath)
scrn_width = int(parser.get('apod_config', 'Screen_Size').split(',')[0])
scrn_length = int(parser.get('apod_config', 'Screen_Size').split(',')[1])
num_chars = int(parser.get('apod_config', 'Num_Characters'))
api_key = parser.get('apod_config', 'API_Key')
title_font_size = int(parser.get('apod_config', 'T_Font_Size'))
body_font_size = int(parser.get('apod_config', 'B_Font_Size'))

url = 'https://api.nasa.gov/planetary/apod?api_key=' + api_key

if len(sys.argv) > 1:
    date = str(sys.argv[1])
    data = json.loads(requests.get(url + '&date=' + date).text)
    logging.info('Command: ' + url + '&date=' + date)
    if len(data) > 2:
        logging.info('Command: ' + url + '&date=' + date)
    else:
        logging.warning('Command failure: ' + url + '&date=' + date)
        sys.exit()
else:
    data = json.loads(requests.get(url).text)
    if len(data) > 2:
        logging.info('Command: ' + url)
    else:
        logging.warning('Command failure: %s', url)
        sys.exit()

if data['media_type'] == 'image':
    image_url = requests.get(data['hdurl'], stream=True)
    if image_url.status_code == 404:
        logging.warning('404 Image not found: %s', data['hdurl'])
        sys.exit()
    elif image_url.status_code != 200:
        logging.warning(image_url.status_code +
                        ' Image retrieval error: %s', data['hdurl'])
        sys.exit()
    else:
        logging.info(image_url.status_code +
                     ' Image retrieval successful: %s', data['hdurl'])
        image = Image.open(image_url.raw).resize((scrn_width, scrn_length),
                                                 resample=0)

    draw = ImageDraw.Draw(image)
    exp_font = ImageFont.truetype("arial.ttf", body_font_size, encoding="unic")
    title_font = ImageFont.truetype("arial.ttf",
                                    title_font_size, encoding="unic")
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
    logging.info('Desktop Background set to %s', data['title'])
else:
    logging.warning('Image not available')
