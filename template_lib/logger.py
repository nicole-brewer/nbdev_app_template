# AUTOGENERATED! DO NOT EDIT! File to edit: template_nbs/logger.ipynb (unless otherwise specified).

__all__ = ['ConfigModel', 'CONFIG', 'SettingsModel', 'DispatchingFormatter', 'FORMATTER', 'ROOT_LOGGER', 'FILE_HANDLER',
           'WidgetHandler', 'WIDGET_HANDLER', 'getLogger', 'logger']

# Cell
class ConfigModel(configparser.ConfigParser):

    def __init__(self):

        ''' a custom converter we use to get a log level value from it's string representation '''
        converters={'loglevel': lambda string: getattr(logging, string)}
        super().__init__(converters=converters)

        ''' root directory of repository '''
        bin = pathlib.Path().absolute().parent

        ''' user paths '''
        self.user_dir = Path('~/.nbdev_app_template').expanduser()
        self.user_dir.mkdir(exist_ok=True)
        self.user_config = self.user_dir / 'config.ini'

        ''' default config '''
        defaults = {'LOG': {'level': 'INFO',
                            'mode': 'w',
                            'captureWarnings': True,
                            'filename': self.user_dir / 'superpower.log'},
                    'ERRORS': {'catch_all': True}
                   }
        self.read_dict(defaults)

        ''' read and validate user config, which overrides default '''
        if self.user_config.is_file:
            try:
                self.read(self.user_config)
            except Exception as e:
                pass

        ''' remove old configs'''
        self.write_user_config()

    def write_user_config(self):
        with open(self.user_config, 'w') as file:
            self.write(file)

    def _repr_pretty_(self, p, cycle):
            for section in self.sections():
                for key, value in self[section].items():
                    p.text(key + ': ')
                    p.pretty(value)
                    p.breakable()

# Cell
CONFIG = ConfigModel()

# Cell
class SettingsModel(HasTraits):

    logLevel = Unicode()
    catchAll = Bool()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.logLevel = CONFIG['LOG']['level']
        self.catchAll = CONFIG['ERRORS'].getboolean('catch_all')

    @observe('logLevel')
    def observeLogLevel(self, change):
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            logger.setLevel(change['new'])
        CONFIG['LOG']['level'] = change['new']
        CONFIG.write_user_config()

    @observe('catchAll')
    def observeCatchAll(self, change):
        CONFIG['ERRORS']['catch_all'] = str(change['new'])
        CONFIG.write_user_config()

# Cell
import ipywidgets as ipyw
import traitlets
import warnings
import os, pathlib, urllib
from IPython.display import HTML, Javascript, display
from pathlib import Path
import logging

# Cell
class DispatchingFormatter:
    """Dispatch formatter for logger and it's sub logger."""
    def __init__(self):
        self.formatters = {
            'root': logging.Formatter('%(message)s'),
            'r.console': logging.Formatter('[R.%(levelname)s] %(message)s'),
            'py.warnings': logging.Formatter('[PY.WARNINGS] %(message)s'),
            '__main__': logging.Formatter('[PY.%(levelname)s] %(message)s'),
            'default': logging.Formatter('[PY.%(levelname)s](%(name)s:%(lineno)d)  %(message)s')
        }

    def format(self, record):
        formatter = self.formatters.get(record.name, self.formatters['default'])
        return formatter.format(record)

# Cell
FORMATTER = DispatchingFormatter()

# Cell
ROOT_LOGGER = logging.getLogger('')
ROOT_LOGGER.setLevel(CONFIG['LOG']['level'])

# Cell
FILE_HANDLER = logging.FileHandler(CONFIG['LOG']['filename'],
                               CONFIG['LOG']['mode'])
FILE_HANDLER.setFormatter(FORMATTER)
logging.getLogger('').addHandler(FILE_HANDLER)

# Cell
class WidgetHandler(ipyw.Textarea, logging.Handler):

    def __init__(self, config):
        super().__init__(layout={'width': '100%', 'height': '250px'}, disabled=True)
        self.config = config

    def emit(self, record):
        self.value += str(self.format(record)) + '\n'

# Cell
WIDGET_HANDLER = WidgetHandler(CONFIG)
WIDGET_HANDLER.setFormatter(FORMATTER)
logging.getLogger('').addHandler(WIDGET_HANDLER)

# Cell
def getLogger(name=''):
    return logging.getLogger(name)

# Cell
logger = getLogger()
logger.info('Welcome to Superpower!')

# Cell
logging.captureWarnings(CONFIG['LOG']['captureWarnings'])