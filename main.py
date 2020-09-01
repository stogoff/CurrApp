from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty

from kivy.config import Config, ConfigParser
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
from kivy.logger import Logger
import requests
import json
import urllib.request
import certifi
import os
import ast
import time

# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()

Config.set('kivy', 'keyboard_mode', 'systemanddock')

#from kivy.core.window import Window
#Window.size = (480, 853)

__version__ = '0.3.2'

def get_rates():
    url = 'https://openexchangerates.org//api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    response = requests.get(url)

    Logger.info('response status code: {}'.format(response.status_code))
    data = response.json()
    ##t = time.strftime('%d/%m %H:%M:%S', time.localtime(data['timestamp']))
    usdrub = float(data['rates']['RUB'])
    eurrub = float(data['rates']['RUB']) / float(data['rates']['EUR'])
    return data['rates']


class Container(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None

    def calculate(self):
        self.app = MDApp.get_running_app()
        self.app.user_data = ast.literal_eval(
            self.app.config.get('General', 'user_data'))
        if 'update' in self.app.user_data.keys() and (time.time() - self.app.user_data['update'] < 120):
            rates = self.app.user_data['rates']
        else:
            try:
                rates = get_rates()
                self.app.user_data['update'] = int(time.time())
                self.app.user_data['rates'] = rates
                self.app.config.set('General', 'user_data', self.app.user_data)
                self.app.config.write()
            except:
                rates = {}
                Logger.exception('Something happened!')
        try:
            amount1 = float(self.amount1.text)
        except:
            amount1 = 0
        k = rates[self.curr2.text]/rates[self.curr1.text]
        if self.curr2.text in ['BTC']:
            fmt = "{:.8f}"
        else:
            fmt = "{:.2f}"
        self.amount2.text = fmt.format(amount1*k)

    def swap_currencies(self):
        self.curr1.text, self.curr2.text = self.curr2.text, self.curr1.text

    def input(self, value):
        if value == '.':
            if '.' not in self.amount1.text:
                self.amount1.text += '.'
        elif value == 'C':
            self.amount1.text = '0'
        else:
            if self.amount1.text == '0':
                self.amount1.text = ''
            self.amount1.text += str(value)
        self.calculate()


class CurrApp(MDApp):
    theme_man = ThemeManager()
    title = "Currency calc"

    def __init__(self, **kvargs):
        super(CurrApp, self).__init__(**kvargs)
        self.config = ConfigParser()

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))
        self.user_data = ast.literal_eval(self.config.get(
            'General', 'user_data'))

    def get_application_config(self):
        return super(CurrApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        self.theme_man.theme_style = 'Light'

        return Container()


if __name__ == '__main__':
    CurrApp().run()
