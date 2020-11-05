import requests

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from generate_ticket_air import TicketMaker

TEMPLATE_PATH = 'files/ticket_base.jpg'
FONT_PATH = 'files/Roboto-Regular.ttf'
FONT_SIZE = 20
BLACK = (0, 0, 0, 255)
NAME_OFFSET = (320, 210)
EMAIL_OFFSET = (320, 247)
AVATAR_SIZE = 100
AVATAR_OFFSET = (100, 200)

TEMPLATE_PATH_COFFEE = 'files/menu_coffee.jpg'


def generate_ticket(data, flag='conference'):
    """
    Сценарий отрисовки изображения
    :param data: данные для отрисовки
    :param flag: switch сценария
    :return: BytesIO изображения
    """
    if flag == 'coffee_menu':
        base = Image.open(TEMPLATE_PATH_COFFEE).convert("RGBA")
    elif flag == 'drink':
        base = Image.open(f'files/drinks/{data["coffee"][0]}.jpg').convert("RGBA")
    elif flag == 'airplane':
        ticket_gen = TicketMaker(**data)
        base = ticket_gen.make()
    else:
        base = Image.open(TEMPLATE_PATH).convert("RGBA")
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        draw = ImageDraw.Draw(base)
        draw.text(NAME_OFFSET, data["name"], font=font, fill=BLACK)
        draw.text(EMAIL_OFFSET, data["email"], font=font, fill=BLACK)

        response = requests.get(url=f'https://api.adorable.io/avatars/{AVATAR_SIZE}/{data["email"]}')
        avatar_file_like = BytesIO(response.content)
        avatar = Image.open(avatar_file_like)
        base.paste(avatar, AVATAR_OFFSET)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
