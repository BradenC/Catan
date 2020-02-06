import inspect
import json
from datetime import datetime
from enum import IntEnum

from catan import config
from catan.files import dirname


class LogLevel(IntEnum):
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5
    ALL = 6


class Logger:
    level = config['logging']['level']
    categories = config['logging']['categories']

    def __init__(self):
        self.filename = f"{dirname}/log"

    def write(self, text='', end='\n'):
        with open(self.filename, 'a+') as f:
            f.write(text)
            f.write(end)

    def tags_are_relevant(self, tags):
        for tag in tags:
            if tag in self.categories and self.categories[tag]:
                return True

        return False

    def log(self, message='', data={}, tags=[], level=None):
        if isinstance(tags, str):
            tags = [tags]

        if self.level == LogLevel.ALL or not tags or self.tags_are_relevant(tags):
            self.write()

            if level:
                self.write(level.name, end='')

            self.write(' | ' + inspect.stack()[2].function, end='')

            if tags:
                self.write(' | [ ' + ', '.join(tags) + ' ]', end='')

            self.write(' | ' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])

            if message:
                self.write(message)

            if data:
                self.write(json.dumps(data))

    def trace(self, message='', data={}, tags=[]):
        if self.level >= LogLevel.TRACE:
            self.log(message, data, tags, LogLevel.TRACE)

    def debug(self, message='', data={}, tags=[]):
        if self.level >= LogLevel.DEBUG:
            self.log(message, data, tags, LogLevel.DEBUG)

    def info(self, message='', data={}, tags=[]):
        if self.level >= LogLevel.INFO:
            self.log(message, data, tags, LogLevel.INFO)

    def warn(self, message='', data={}, tags=[]):
        if self.level >= LogLevel.WARN:
            self.log(message, data, tags, LogLevel.WARN)

    def error(self, message='', data={}, tags=[]):
        if self.level >= LogLevel.ERROR:
            self.log(message, data, tags, LogLevel.ERROR)


logger = Logger()