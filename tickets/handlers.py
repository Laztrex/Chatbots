#!/usr/bin/env python3
"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройден, False если данные введены неправильно.
"""
from datetime import datetime, timedelta, timezone
import re

from dateutil.parser import parse
from geopy.geocoders import Nominatim
from vk_api.keyboard import VkKeyboardColor

from generate_ticket import generate_ticket
from settings import DRINKS

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'(\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)+\b')
re_phone = re.compile(r'\+?\d[\( -]?\d{3}[\) -]?\d{3}[ -]?\d{2}[ -]?\d{2}')


def keyboard_welcome(step, context):
    """
    Создание клавиатуры с выбором действий
    :param step: шаг сценария (not used)
    :param context: контекст текущего события
    :return: json клавиатуры
    """
    context.add_callback_button(label='Зарегистрироваться', color=VkKeyboardColor.SECONDARY,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})

    context.add_line()

    context.add_callback_button(label='Самолёт', color=VkKeyboardColor.POSITIVE,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})
    context.add_line()

    context.add_callback_button(label='Кофе', color=VkKeyboardColor.NEGATIVE,
                                payload={"type": "show_snackbar", "text": "Ну поехали"})

    return context.get_keyboard()


def view_keyboard(step, context):
    """
    Создание клавиатуры с выбором действий (выбор напитка). Для сценария "coffee" (кофейный автомат).
    :param step: шаг сценария
    :param context: контекст текущего события
    :return: json клавиатуры
    """
    if not context.keyboard['buttons'][0]:
        for num, drink in enumerate(step['drinks'].items()):
            if num == 3:
                context.add_line()
            context.add_button(f'{drink[0]}', color=VkKeyboardColor.POSITIVE)
    return context.get_keyboard()


def check_bonus_card(text, context):
    return True


def handle_name(text, context):
    """
    Валидации имени пользователя
    :param text: сообщение от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    """
    Валидация email
    :param text: сообщение от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def handle_connection(text, context):
    """
    Валидация email/номера телефона. Для сценария "airplane (билет на самолёт)"
    :param text: сообщение от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['connect'] = matches[0]
        return True
    matches = re.findall(re_phone, text)
    if len(matches) > 0:
        context['connect'] = matches[0]
        return True
    return False


def generate_ticket_handle(text, context):
    """
    Создание изображения билета на конференцию. Для сценария "conference (билет на конференцию)
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: IOBytes изображения
    """
    return generate_ticket(context)


def generate_menu_coffee(text, context):
    """
    Создание изображения меню кофе. Для сценария "coffee (кофейный автомат)
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: IOBytes изображения
    """
    return generate_ticket(context, flag='coffee_menu')


def generate_img_coffee(text, context):
    """
    Вывод изображения напитка :). Для сценария "coffee (кофейный автомат)
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: IOBytes изображения
    """
    return generate_ticket(context, flag='drink')


def handle_coffee(text, context):
    """
    Проверка выбранного напитка
    :param text: сообщение от польхователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    choices_drink = text.upper()
    if choices_drink in DRINKS:
        context['coffee'] = (choices_drink, int(DRINKS.get(choices_drink)))
        return True
    return False


def pay_coffee(text, context):
    """
    (В тестовом варианте реализация vkPay не выполнялась, по понятным причинам. Но можно сделать)
    Покупка напитка.
    Выполняется, если пользователь не зарегистрирован на конференцию (сценарий "conference") - условие бесплатного кофе
    :param text: денежка от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    money = int(text) - context['coffee'][1]
    if money >= 0:
        return True
    return False


def handle_departure_point(text, context):
    """
    Создание клавиатуры с геолокацией
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: json клавиатуры
    """
    context.add_location_button()
    return context.get_keyboard()


def handle_destination_point(text, context):
    """
    Создание клавиатуры с геолокацией
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: json клавиатуры
    """
    context.add_location_button()
    return context.get_keyboard()


def handle_date(text, context):
    """
    :param text: сообщение от пользователя (дата)
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    try:
        parsed_data = parse(text, dayfirst=True).date()
    except Exception:
        # TODO: написать доп.метод обработки (анализа)
        # res = analyze_date(text)
        # if res:
        #     parsed_data = res
        # else:
        # raise Exception("Incorrect format date")  # TODO: log
        return False

    context["date_reg"] = datetime.now().date().strftime('%d.%m.%Y')
    curr = datetime.combine(parsed_data, datetime.utcnow().time(), tzinfo=timezone.utc).astimezone()
    context["date_landing"] = curr.strftime('%d.%m.%Y %H:%M:%S')
    context["date_direction"] = (curr + timedelta(hours=7, minutes=30)).strftime('%d.%m.%Y %H:%M:%S')
    return True


def generate_ticket_air(text, context):
    """
    Создание изображения билета на самолёт. Для сценария "airplane (билет на самолёт)
    :param text: сообщение от пользователя (not used)
    :param context: контекст текущего события
    :return: IOBytes изображения
    """
    return generate_ticket(context, flag='airplane')


# def super_handler(text, context):
#     for idx, (handler, unit) in enumerate(
#             zip([handle_name, handle_departure_point, handle_destination_point, handle_date, handle_email],
#                 context)):
#         handler(unit[text[idx]])

def location_find(target):
    """
    Поиск выбранного места отправления/назначения с помощью данных OpenStreetMap.
    Для сценария "airplane (билет на самолёт)".
    :param target: место отправления/назначения
    :return: str в формате "<country>, <city>"
    """
    geolocation = Nominatim(user_agent="chat-bot vk")
    location = geolocation.geocode(target, addressdetails=True, language='ru')
    if location:
        address = location.raw['address']
        return f'{address.get("country")}, ' \
               f'{address.get("city", location.raw["display_name"].replace(" ", "").split(",")[0])}'


def handle_landing(text, context):
    """
    Проверка выбранного места отправления. Для сценария "airplane (билет на самолёт)"
    :param text: сообщение от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    check_landing = location_find(text)
    if check_landing:
        context["landing"] = check_landing
        return True
    return False


def handle_direction(text, context):
    """
    Проверка выбранного места назначения. Для сценария "airplane (билет на самолёт)"
    :param text: сообщение от пользователя
    :param context: контекст текущего события
    :return: True - валидация пройдена; False - в противном случае
    """
    check_landing = location_find(text)
    if check_landing:
        context["direction"] = check_landing if len(check_landing) <= 25 \
            else check_landing[:25] + '...'
        return True
    return False
