import difflib
import re
from collections import Counter

alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'


class SpellingCorrect:
    """
    Класс для обработки текста с ошибкой
    """
    def __init__(self, my_text):
        self.my_dict = Counter(self.tokens(my_text))

    def tokens(self, text):
        """Возвращает список токенов (подряд идущих буквенных последовательностей) в тексте.
        Также приводим текст к нижнему регистру"""
        return re.findall(r'[а-яё]+', text.lower())

    def known(self, words):
        """Вернуть множество слов, которые есть в нашем словаре"""
        return {w for w in words if w in self.my_dict}

    def edits0(self, word):
        """Вернуть все строки, которые находятся на edit_distance == 0 от word"""
        return {word}

    def edits2(self, word):
        """Вернуть все строки, которые находятся на edit_distance == 1 от word"""
        return {e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)}

    def edits1(self, word):
        """Возвращает список всех строк на расстоянии edit_distance == 1 от word"""
        pairs = self.splits(word)
        deletes = [a + b[1:] for (a, b) in pairs if b]
        transposes = [a + b[1:] + b[0] + b[2:] for (a, b) in pairs if len(b) > 1]
        replaces = [a + c + b[1:] for (a, b) in pairs
                    for c in alphabet if b]
        inserts = [a + c + b for (a, b) in pairs
                   for c in alphabet]

        return set(deletes + transposes + replaces + inserts)

    def splits(self, word):
        """Возвращает список всех возможных разбиений слова на пару (a, b)"""
        return [(word[:i], word[i:]) for i in range(len(word) + 1)]

    def correct(self, word):
        """Поиск лучшего исправления ошибки для слова"""
        candidates = (self.known(self.edits0(word)) or
                      self.known(self.edits1(word)) or
                      self.known(self.edits2(word)) or
                      [word])
        return max(candidates, key=self.my_dict.get)

    def correct_text(self, text):
        """Старт обработки"""
        return self.similarity(re.sub('[а-яА-ЯёЁ]+', self.correct_match, text),
                               ['привет', 'самолёт', 'кофе', 'регистрация, конференция'])

    def correct_match(self, match):
        word = match.group()
        return self.case_of(word)(self.correct(word.lower()))

    def case_of(self, text):
        return (str.upper if text.isupper() else
                str.lower if text.islower() else
                str.title if text.istitle() else
                str)

    def similarity(self, candidate, keys):
        for find_key in keys:
            normalized1 = candidate.lower()
            if difflib.SequenceMatcher(None, normalized1, find_key).ratio() > 0.65:
                return find_key

