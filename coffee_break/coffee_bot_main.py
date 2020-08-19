#!/usr/bin/env python3
import random
import logging
import requests
from pony.orm import db_session

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


class VkBotCoffee:
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

    def run_bot(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    def on_event(self, event):
        """Отправляет сообщение назад, если оно текстовое"""
        pass
