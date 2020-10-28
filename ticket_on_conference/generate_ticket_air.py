from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageColor


# TEMPLATE_PATH = 'files/ticket_base.jpg'
# FONT_PATH = 'files/Roboto-Regular.ttf'
# FONT_SIZE = 20
# BLACK = (0, 0, 0, 255)
# NAME_OFFSET = (320, 210)
# EMAIL_OFFSET = (320, 247)
# AVATAR_SIZE = 100
# AVATAR_OFFSET = (100, 200)


class TicketMaker:
    def __init__(self, name, email=None, landing='Москва', direction='Минск', date='26.10.20'):
        self.name_passenger = [(45, 120), name]
        self.landing = [(45, 190), landing]
        self.direction = [(45, 255), direction]
        self.date = [(280, 255), date]
        self.drawing = [self.name_passenger, self.landing, self.direction, self.date]
        # self.template = os.path.join("images", "ticket_template.jpg")
        # self.font_path = os.path.join("python_snippets\\fonts", "ofont.ru_Vollkorn.ttf")
        self.font_path = 'files/Roboto-Regular.ttf'
        self.template = 'files/ticket_template.png'

    def make(self, out_path=None):
        ticket_image = Image.open(self.template).convert("RGBA")
        draw = ImageDraw.Draw(ticket_image)
        font = ImageFont.truetype(self.font_path, size=15)

        for text in self.drawing:
            self._print_on_ticket(pic=draw, field=text, font=font)

        # out_path = out_path if out_path else 'our_ticket.png'
        # ticket_image.save(out_path)
        # print(f'Your ticket has been saved to {out_path}')
        return ticket_image

    def set_landing(self, target):
        self.landing[1] = target

    def set_direction(self, target):
        self.direction[1] = target

    def set_date(self, date):
        self.date[1] = date

    def _print_on_ticket(self, pic, field, font):
        pic.text(field[0], field[1], font=font, fill=ImageColor.colormap['black'])


def generate_ticket(data):  # TODO: убрать, будет общий generate_ticket
    ticket_gen = TicketMaker(**data)
    base = ticket_gen.make()
    temp_file = BytesIO()

    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file

