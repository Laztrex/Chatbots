#!/usr/bin/env python3
import random
import logging

import requests
from pony.orm import db_session
from vk_api.keyboard import VkKeyboard

import handlers
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token!')

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


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
        """Отправляет сообщение назад, если оно текстовое"""
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info('мы пока не можем обрабатывать этот тип %s', event.type)
            return

        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))

        if state is not None:
            self.continue_scenario(text, state, user_id)
        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id, keyboard_active=None):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
            keyboard=keyboard_active
        )

    def send_image(self, image, user_id):
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
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)
        if 'keyboard' in step:
            handler = getattr(handlers, step['keyboard'])
            keyboard = handler(step['drinks'], self.pay)
            self.send_text('Выбери напиток', user_id, keyboard_active=keyboard)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])

        # TODO: доработать
        if state.scenario_name == 'registration' and state.step_name == 'step2':
            for i in Registration.select():
                if text == i.email:
                    text_to_send = step['failure_text2'].format(**state.context)
                    self.send_text(text_to_send, user_id)
                    return

        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)

            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                if state.scenario_name == 'coffee':
                    log.info('Выдан кофе')
                    # TODO: добавить в бд для бонусов и подсчета выпитого кофе (в день не больше трех, например)
                    state.delete()
                else:
                    log.info('Зарегистрирован: {name} {email}'.format(**state.context))
                    Registration(name=state.context['name'], email=state.context['email'])
                    state.delete()
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send, user_id)


if __name__ == "__main__":
    configure_logging()
    my_bot = VkBot(settings.GROUP_ID, settings.TOKEN)
    my_bot.run()
