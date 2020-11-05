from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent
import settings
from copy import deepcopy

from bot import VkBot
from generate_ticket import generate_ticket


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session as session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new',
                 'object': {'date': 1574375803, 'from_id': 563762917, 'id': 705,
                            'out': 0, 'peer_id': 563762917, 'text': 'hello', 'conversation_message_id': 705,
                            'fwd_messages': [],
                            'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False},
                 'group_id': 187930812}

    INPUTS = [
        'ты кто',
        'Привет',
        'А Когда',
        'Где будет конференция?',

        'Зарегай меня',
        'Вениамин',
        'мой адрес email@mail',
        'email@email.ru',

        'самолёт',
        'Вася Пупкин',
        'московья',
        'Россия, Москва',
        'Франция, Париж',
        '20-го где-то через месяц',
        '22.12.2020',
        'pupkin@pip.ru',

        'кофейку',
        'LATTE',
        'la@la',
        '70',
        '80',
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.SCENARIOS['welcome']['steps']['step1']['text'],
        settings.SCENARIOS['welcome']['steps']['step1']['keyboard_message'],

        settings.INTENTS[1]['answer'],
        settings.INTENTS[2]['answer'],

        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@email.ru'),

        settings.SCENARIOS['airplane']['steps']['step1']['text'],
        settings.SCENARIOS['airplane']['steps']['step2']['text'],
        settings.SCENARIOS['airplane']['steps']['step2']['keyboard_message'],
        settings.SCENARIOS['airplane']['steps']['step2']['failure_text'],
        settings.SCENARIOS['airplane']['steps']['step3']['text'],
        settings.SCENARIOS['airplane']['steps']['step3']['keyboard_message'],
        settings.SCENARIOS['airplane']['steps']['step4']['text'],
        settings.SCENARIOS['airplane']['steps']['step4']['failure_text'],
        settings.SCENARIOS['airplane']['steps']['step5']['text'],
        settings.SCENARIOS['airplane']['steps']['step6']['text'].format(name='Вася Пупкин', connect='pupkin@pip.ru'),

        settings.SCENARIOS['coffee']['steps']['step1']['text'],
        settings.SCENARIOS['coffee']['steps']['step1']['keyboard_message'],
        settings.SCENARIOS['coffee']['steps']['step2']['text'],
        settings.SCENARIOS['coffee']['steps']['step2']['failure_text'],
        settings.SCENARIOS['coffee']['steps']['step3']['text'],
        settings.SCENARIOS['coffee']['steps']['step3']['failure_text'],
        settings.SCENARIOS['coffee']['steps']['step4']['text'],
    ]

    def test_run(self):
        count = 5
        obj = {}
        events = [obj] * count  # [{}, {}, ...]
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = VkBot("", "")
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call({})
                assert bot.on_event.call_count == count

    @isolate_db
    @patch('handlers.generate_ticket_handle', return_value=None)
    def test_run_ok(self, mock_request):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = VkBot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS) + 5

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        with open('files/greg.png', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()
        with patch('requests.get', return_value=avatar_mock):
            ticket_file = generate_ticket({'name': 'rge', 'email': 'greg'}, flag='conference')
        with open('files/ticket_example.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
        assert ticket_file.read() == expected_bytes

    def test_image_airline_gen(self):
        pass

    def test_image_coffee_gen(self):
        pass

    def test_spelling_words(self):
        pass


