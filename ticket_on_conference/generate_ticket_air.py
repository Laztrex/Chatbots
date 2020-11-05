from PIL import Image, ImageDraw, ImageFont, ImageColor
import datetime


class TicketMaker:
    def __init__(self, name, connect=None, landing='Москва', direction='Минск',
                 date_reg='26.10.20', date_landing=None, date_direction=None,
                 model_plane=None, place_passenger=None, row_place=None):
        self.name_passenger = [(45, 120), name]
        self.landing = [(45, 190), landing]
        self.direction = [(45, 255), direction]
        self.date = [(280, 255), date_reg]
        self.time_landing = [(420, 265), datetime.datetime.strftime(
            datetime.datetime.strptime(date_landing, "%d.%m.%Y %H:%M:%S"), "%H:%M")]
        self.time_direction = [(420, 335), datetime.datetime.strftime(
            datetime.datetime.strptime(date_direction, "%d.%m.%Y %H:%M:%S"), "%H:%M")]
        self.drawing = [self.name_passenger, self.landing, self.direction,
                        self.date, self.time_landing, self.time_direction]
        self.font_path = 'files/Roboto-Regular.ttf'
        self.template = 'files/ticket_template.png'

    def make(self, out_path=None):
        ticket_image = Image.open(self.template).convert("RGBA")
        draw = ImageDraw.Draw(ticket_image)
        font = ImageFont.truetype(self.font_path, size=15)

        for text in self.drawing:
            self._print_on_ticket(pic=draw, field=text, font=font)

        return ticket_image

    def set_landing(self, target):
        self.landing[1] = target

    def set_direction(self, target):
        self.direction[1] = target

    def set_date(self, date):
        self.date[1] = date

    def _print_on_ticket(self, pic, field, font):
        pic.text(field[0], field[1], font=font, fill=ImageColor.colormap['black'], )


