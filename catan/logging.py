from enum import IntEnum
import inspect

from catan import config


class LogLevel(IntEnum):
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    ALL = 5


class Logger:
    level = config['log_level']

    categories = {
        'actions': True,
        'checks': False,
        'planning': True
    }

    @staticmethod
    def write(text='', end='\n'):
        print(text, end=end)

    def tags_are_relevant(self, tags):
        if not isinstance(tags, list):
            tags = [tags]

        for tag in tags:
            if tag in self.categories and self.categories[tag]:
                return True

        return False

    def log(self, message='', data={}, tags=[], level=None):
        if self.level == LogLevel.ALL or not tags or self.tags_are_relevant(tags):
            self.write()

            if level:
                self.write(level.name + ' | ', end='')

            self.write(inspect.stack()[2].function, end='')

            if tags:
                self.write(f' | {tags}')
            else:
                self.write()

            if message:
                self.write(message)

            if data:
                self.write(data)

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
