from io import BytesIO

from PIL import Image

TEMPLATE_PATH = 'files/menu_coffee.jpg'
FONT_PATH = 'files/Roboto-Regular.ttf'
FONT_SIZE = 20
BLACK = (0, 0, 0, 255)
NAME_OFFSET = (320, 210)
EMAIL_OFFSET = (320, 247)
AVATAR_SIZE = 100
AVATAR_OFFSET = (100, 200)


def generate_menu():
    base = Image.open(TEMPLATE_PATH).convert("RGBA")

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
