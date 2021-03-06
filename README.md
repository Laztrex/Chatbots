# ChatBot Tickets  
Тестовый проект чат-бота для vk, носит исключительно учебный характер. В будущем планируется расширять функционал

---
## Начальная настройка:
-  Все необходимяе модули находятся в файле requirements.txt:
~~~
pip install -r requirements.txt
~~~
- Из особенностей: используются модули версий vk-api==11.9.0 и Pillow==7.2.0
- Необходимо копировать файл settings.py.default, переименовав в settings.py и добавив в поле уникальный ключ TOKEN (и идентификатор группы GROUP_ID)
~~~
cp settings.py.default settings.py
~~~
Как получить TOKEN:
...

## Префиксы (токены):
По умолчанию бот отзывается на следующие префиксы:

- привет - Запуск сценарий приветсвия. Выводит меню из трёх возможных сценариев (Регистрация на конференцию, Кофебрейк, регистрация на самолёт)
Сценарий регистрации на конференцию:
- регистрация (или выбрать соответствующий пункт в меню) - заполнение билета на конференцию данными, введёнными пользователем. По окончании присылается заполненный билет

- кофе (или выбрать соответствующий пункт в меню) - вывод меню кофе, при выборе проверяется регистрация пользователя на конференцию. Если не зарегистрирован - плати денежку (vk pay пока не включен, просто отправьте сообщение)
- самолёт (или выбрать соотвествующий пункт в меню) - заполнение билета на самолёт данными, введёнными пользователем. По окончании присылается заполненный билет

При желании можно модифицировать префиксы или дополнить своими в settings.py


## Примеры работы
- **сценарий регистрации на конференцию** 
![Image alt](https://github.com/Laztrex/Chatbots/raw/master/tickets/files/ticket_example.png)

- **сценарий регистрации на самолёт**
![Image alt](https://github.com/Laztrex/Chatbots/raw/master/tickets/files/airplane_ticket_example.png)



## В перспективе
Планируются следующие расширения 
- Ответы в режиме "свободного общения"
- Сценарий покупки билета: брать реальное расписание полётов, предоставлять выбор даты/времени относительно полученных данных
- Сценарий покупки билета: при указании даты научить бота понимать фразы "завтра", "на новый год", "ближайший" и т.д.
- Сценарий кофе: завести БД для напитков, определять в чате админа, который может менять информацию о доступности определённых напитоков
