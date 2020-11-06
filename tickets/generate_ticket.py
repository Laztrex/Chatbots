import requests

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from generate_ticket_air import TicketMaker
from files.settings_img import TICKET_CONFERENCE_BASE, TICKET_CONFERENCE_PLACE, COFFEE_BASE


def generate_ticket(data, flag='conference'):
    """
    Сценарий отрисовки изображения
    :param data: данные для отрисовки
    :param flag: switch сценария
    :return: BytesIO изображения
    """
    if flag == 'coffee_menu':
        base = Image.open(COFFEE_BASE["menu_template"]).convert("RGBA")
    elif flag == 'drink':
        base = Image.open(COFFEE_BASE["coffee_img"].format(data["coffee"][0])).convert("RGBA")
    elif flag == 'airplane':
        ticket_gen = TicketMaker(**data)
        base = ticket_gen.make()
    else:
        base = Image.open(TICKET_CONFERENCE_BASE["template"]).convert("RGBA")
        font = ImageFont.truetype(TICKET_CONFERENCE_BASE["font"], TICKET_CONFERENCE_BASE["font_size"])

        draw = ImageDraw.Draw(base)
        draw.text(TICKET_CONFERENCE_PLACE["name_offset"], data["name"], font=font,
                  fill=TICKET_CONFERENCE_BASE["color"])
        draw.text(TICKET_CONFERENCE_PLACE["email_offset"], data["email"], font=font,
                  fill=TICKET_CONFERENCE_BASE["color"])

        response = requests.get(url=f'https://api.adorable.io/avatars/{TICKET_CONFERENCE_BASE["avatar_size"]}'
                                    f'/{data["email"]}')

        avatar_file_like = BytesIO(response.content)
        avatar = Image.open(avatar_file_like)
        base.paste(avatar, TICKET_CONFERENCE_PLACE["avatar_offset"])

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
