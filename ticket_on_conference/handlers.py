#!/usr/bin/env python3
"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройден, False если данные введены неправильно.
"""
import datetime
import json
import re
from io import BytesIO
# import pandas as pd
from dateutil.parser import parse
from PIL import Image, ImageDraw, ImageFont
from vk_api.keyboard import VkKeyboardColor
from geopy.geocoders import Nominatim
from generate_ticket import generate_ticket
from generate_ticket_air import generate_ticket as ticket_air
from generate_menu_coffee import generate_menu

from settings import DRINKS

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'(\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)+\b')


def keyboard_welcome(text, context):
    context.add_callback_button(label='Зарегистрироваться', color=VkKeyboardColor.SECONDARY,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})

    context.add_line()

    context.add_callback_button(label='Самолёт', color=VkKeyboardColor.POSITIVE,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})
    context.add_line()

    context.add_callback_button(label='Кофе', color=VkKeyboardColor.NEGATIVE,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})

    return context.get_keyboard()


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
        for num, drink in enumerate(text['drinks'].items()):
            if num == 3:
                context.add_line()
            context.add_button(f'{drink[0]}', color=VkKeyboardColor.POSITIVE)
    return context.get_keyboard()


def handle_welcome(text, context):
    return True


def handle_coffee(text, context):
    choices_drink = text.upper()
    if choices_drink in DRINKS:
        context['coffee'] = (choices_drink, int(DRINKS.get(choices_drink)))
        return True
    return False


def check_choice_coffee(text, context):
    return True


def check_bonus_card(text, context):
    return True


def pay_coffee(text, context):
    money = int(text) - context['coffee'][1]
    if money >= 0:
        return True
    return False


def handle_departure_point(text, context):
    context.add_location_button()
    return context.get_keyboard()


def handle_destination_point(text, context):
    context.add_location_button()
    return context.get_keyboard()


def handle_date(text, context):
    """
    :param text:
    :param context:
    :return: False - failure_text; True - обработано ок
    """
    try:
        parsed_data = parse(text, dayfirst=True).strftime("%d.%m.%Y")
    except Exception:
        # TODO: написать доп.метод обработки (анализа)
        res = analyze_date(text)
        if res:
            parsed_data = res
        else:
            raise Exception("Incorrect format date")
    context["date"] = parsed_data
    return True


def check_data(text, context):
    # TODO: вывод формы, при нажатии на которую нужно сделать возможность редактирования поля

    return True


def generate_img_coffee(text, context):
    base = Image.open(f'files/drinks/{context["coffee"][0]}.jpg').convert("RGBA")

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file


def generate_ticket_air(text, context):
    return ticket_air(context)


# def super_handler(text, context):
#     for idx, (handler, unit) in enumerate(
#             zip([handle_name, handle_departure_point, handle_destination_point, handle_date, handle_email],
#                 context)):
#         handler(unit[text[idx]])

def location_find(target):
    geolocation = Nominatim(user_agent="chat-bot vk")
    location = geolocation.geocode(target)
    if location:
        return location.address


def handle_landing(text, context):
    check_landing = location_find(text)
    if check_landing:
        context["landing"] = check_landing
        return True
    return False


def handle_direction(text, context):
    check_landing = location_find(text)
    if check_landing:
        context["direction"] = check_landing
        return True
    return False


def analyze_date(strange_date):
    """
    Сегодня, завтра, послезавтра,
    # TODO: парсить расписание полётов для уточнения времени?
    :param strange_date:
    :return:
    """
    # curr_year = datetime.datetime.now().date().year
    # # pattern = r'(?:0?[1-9]|[12][0-9]|3[01]).(?:0?[1-9]|1[0-2]).(?:19[0-9][0-9]|20[01][0-9])'
    # try:
    #     parsed_dates = pd.to_datetime(strange_date).date()
    # except Exception:
    #     return False
    # print(parsed_dates)
    # print(type(parsed_dates))
    # return parsed_dates
    pass


def analyze_point(city):
    pass


def analyze_ever(think):
    pass


def draw_ticket(text, context):
    """Будет класс рисовальщика, туда заносится инфа
    Затем при отрисовки картинки вся инфа стянется"""

    return True
