#!/usr/bin/env python3
import logging
import random
import requests

import vk_api
from pony.orm import db_session
from vk_api.keyboard import VkKeyboard
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import handlers
from models import UserState, Registration, BonusCardCoffee, RegistrationAirline
from simple_spelling_correct import SpellingCorrect

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token!')


log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.DEBUG)
    log.addHandler(stream_handler)
    # TODO: в Formatter менять дату. Вид: ДД.ММ.ГГГГ ЧЧ:ММ
    file_handler = logging.FileHandler('bot.log', encoding='cp1251')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class VkBot:
    """
    Echo bot для vk.com
    Use python 3.7.5
    """

    def __init__(self, group_id, secret_key):
        """
        :param group_id: id группы vk.com
        :param secret_key: секретный токен из группы
        """
        self.group_id = group_id
        self.token = secret_key
        self.vk = vk_api.VkApi(token=secret_key)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

        self.pay = VkKeyboard(one_time=True)

        self.status_message_from_user = False
        self.keyboard_active = None
        self.flag_drink = ''

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    @db_session
    def on_event(self, event):
        """
        Обработка текстового сообщения.
        :param event: событие VkBotLongPoll
        :return: None, если событие неизвестно
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            if event.type == VkBotEventType.MESSAGE_EVENT:
                print(event)
            else:
                log.info('мы пока не можем обрабатывать этот тип %s', event.type)
                return

        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))

        if event.object.get('geo'):  # TODO
            text = event.object.get('geo')['place']['title']

        if state is not None and state.scenario_name != 'welcome':
            self.continue_scenario(text, state, user_id)
        else:
            # search intent
            if self.check_token(text, user_id) is False:
                spelling_text = SpellingCorrect(settings.TEXT_TEST)
                ans = spelling_text.correct_text(text.lower())
                if ans:
                    self.check_token(ans, user_id)
                else:
                    self.send_text(settings.DEFAULT_ANSWER, user_id)

    def check_token(self, text, user_id):
        """
        Проверка ключевого слова для старта сценария
        :param text: ответ пользователя
        :param user_id: id пользователя
        :return: False, если старт не задан
        """
        for intent in settings.INTENTS:
            log.debug(f'User gets {intent}')
            if any(token in text.lower() for token in intent['tokens']):
                if intent['answer']:
                    self.send_text(intent['answer'], user_id)
                else:
                    self.start_scenario(user_id, intent['scenario'], text)
                break
        else:
            return False

    def send_text(self, text_to_send, user_id, keyboard_active=None):
        """
        Отправка сообщения
        :param text_to_send: Текст сообщения
        :param user_id: id пользователя
        :param keyboard_active: активация клавиатуры
        :return: None
        """
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
            keyboard=keyboard_active
        )

    def send_image(self, image, user_id):
        """
        Отправка изображения
        :param image: io изображения
        :param user_id: id пользователя
        :return: None
        """
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'

        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
        )

    def send_step(self, step, user_id, text, context):
        """
        Обработка контекста в зависимости от действия по сценарию
        :param step: шаг сценария
        :param user_id: id пользователя
        :param text: текст сообщения
        :param context: контекст текущего события
        :type context: dict
        :return: None
        """
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)
        if 'keyboard' in step:
            handler = getattr(handlers, step['keyboard'])
            keyboard = handler(step, self.pay)
            self.send_text(step["keyboard_message"], user_id, keyboard_active=keyboard)
            self.pay = VkKeyboard(one_time=True)

    def start_scenario(self, user_id, scenario_name, text):
        """
        Старт сценария
        :param user_id: id пользователя
        :param scenario_name: имя текущего сценария
        :param text: сообщение от пользователя
        :return: None
        """
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        if scenario_name != 'welcome':
            UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def db_info(self, state, step, user_id, text):
        """
        Манипуляция с базой данных
        :param state: Текущее контекст (хранит последнее действие от пользователя)
        :param step: текущий шаг
        :param user_id: id пользователя
        :param text: текст от пользователя
        :return: False, если в сценарии 'registration' найдено совпадения по зарегистрированному email;
                continue - в сценарии 'coffee' найден пользователь;
                True - нет подходящего сценария
        """
        if state.scenario_name == 'registration':
            for i in Registration.select():
                if text == i.email:
                    text_to_send = step['failure_text2'].format(**state.context)
                    self.send_text(text_to_send, user_id)
                    return False

        elif state.scenario_name == 'coffee':
            res = BonusCardCoffee.select(lambda x: x.count < 10 and x.email_card == text)
            if res:
                for user in res:
                    user.count += 1
                    self.send_text('Да, сегодня ещё есть бесплатный кофе', user_id)
                    return 'continue'
            else:
                self.send_text(step['failure_text'], user_id)
        else:
            return True

    def continue_scenario(self, text, state, user_id):
        """
        Продолжение обработки сценария
        :param text: сообщение от пользователя
        :param state: Текущее контекст (хранит последнее действие от пользователя)
        :param user_id: id пользователя
        :return: None
        """
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        if state.step_name == 'step2':
            ans = self.db_info(state, step, user_id, text)
            if ans == 'continue':
                step = steps[step['next_step']]
            elif ans is False:
                return

        handler = getattr(handlers, step['handler'])

        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)

            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                self.finish_scenario(state)
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send, user_id)

    def finish_scenario(self, state):
        """
        Завершение текущего сценария
        :param state: состояние текущей процедуры
        :type state: models.UserState
        :return: None
        """
        if state.scenario_name == 'coffee':
            log.info('Выдан кофе')
            self.pay.get_empty_keyboard()
            state.delete()
        elif state.scenario_name == 'registration':
            log.info('Зарегистрирован: {name} {email}'.format(**state.context))
            Registration(name=state.context['name'], email=state.context['email'])
            BonusCardCoffee(email_card=state.context['email'], count=0)
            state.delete()
        elif state.scenario_name == 'airplane':
            log.info('Зарегистрирован на полёт: {name} {connect}. Рейс: {landing}-{direction}, {date_reg}'
                     .format(**state.context))
            RegistrationAirline(name=state.context['name'], connect=state.context['connect'],
                                landing=state.context['landing'], direction=state.context['direction'],
                                date_reg=state.context['date_reg'], date_landing=state.context['date_landing'],
                                date_direction=state.context["date_direction"])
            state.delete()
        else:
            state.delete()


if __name__ == "__main__":
    configure_logging()
    my_bot = VkBot(settings.GROUP_ID, settings.TOKEN)
    my_bot.run()
