#!/usr/bin/env python3
"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройден, False если данные введены неправильно.
"""
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from vk_api.keyboard import VkKeyboardColor

from generate_ticket import generate_ticket
from generate_menu_coffee import generate_menu

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'(\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)+\b')


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def generate_ticket_handle(text, context):
    return generate_ticket(name=context['name'], email=context['email'])


def generate_menu_coffee(text, context):
    return generate_menu()


def view_keyboard(text, context):
    if not context.keyboard['buttons'][0]:
        for num, drink in enumerate(text.items()):
            if num == 4:
                context.add_line()
            context.add_button(f'{drink[0]}', color=VkKeyboardColor.DEFAULT)
    return context.get_keyboard()


# def handle_coffee(text, context):
#     return 'пока ничего'
#
#
# def check_bonus_card(text, context):
#     return 'пока ничего'
#
#
# def pay_coffee(text, context):
#     return 'пока ничего'


def generate_img_coffee(text, context):
    base = Image.open('files/drinks/latte.jpg').convert("RGBA")

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
