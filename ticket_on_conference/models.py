import datetime

from pony.orm import Database, Required, Json, Optional, PrimaryKey
from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария"""
    id = PrimaryKey(int, auto=True)
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Заявка на регистрацию"""
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    email = Required(str, unique=True)


class RegistrationAirline(db.Entity):
    """Заявка на билет на самолёт"""
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    connect = Required(str)
    landing = Required(str)
    direction = Required(str)
    date_reg = Required(str)  # TODO
    date_landing = Required(str)
    date_direction = Required(str)


class BonusCardCoffee(db.Entity):
    """Лимит на получение бесплатного кофе"""
    id = PrimaryKey(int, auto=True)
    email_card = Required(str, unique=True)
    count = Optional(int)

    # ingredients_qty


db.generate_mapping(create_tables=True)
