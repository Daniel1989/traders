from abc import ABC, abstractmethod
import requests

NULL_VALUE = -999


class Exchange(ABC):
    def __init__(self):
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        session.headers.update(headers)
        self.session = session

    @abstractmethod
    def handle4DailyRecord(self):
        pass

    def formatNumberValue(self, value):
        if value is None:
            return value
        if type(value) == type(1.0) or type(value) == type(1):
            return value
        val = value.replace(',', '')
        if val == ' ' or val == '':
            return NULL_VALUE
        return val

