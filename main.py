from kivy.uix.gridlayout import GridLayout
from kivy.config import  ConfigParser
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
from kivy.logger import Logger
import requests
import certifi
import os
import ast
import time

os.environ['SSL_CERT_FILE'] = certifi.where()
#from kivy.core.window import Window
#Window.size = (480, 853)
__version__ = '0.3.7'

def get_rates():
    url = 'https://openexchangerates.org/api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    response = requests.get(url)
    Logger.info('response status code: {}'.format(response.status_code))
    data = response.json()
    return data['rates']


class Container(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.curr1.text, self.curr2.text = ast.literal_eval(self.app.config.get(
            'General', 'currencies'))
        self.rates = {}
        self.update_rates()

    def update_rates(self):
        try:
            self.rates = get_rates()
            self.app.user_data['update'] = int(time.time())
            self.app.user_data['rates'] = self.rates
            self.app.config.set('General', 'user_data', self.app.user_data)
            self.app.config.write()

            self.timelabel.text = time.strftime("%d.%m.%Y, %H:%M:%S",
                                                time.localtime(self.app.user_data['update']))

        except:
            rates = {}
            Logger.exception('Something happened!')

    def calculate(self):
        #self.app =
        self.app.user_data = ast.literal_eval(
            self.app.config.get('General', 'user_data'))
        if 'update' in self.app.user_data.keys() and (time.time() - self.app.user_data['update'] < 1800):
            self.rates = self.app.user_data['rates']
        else:
            self.update_rates()
        try:
            amount1 = float(self.amount1.text)
        except:
            amount1 = 0
        k = self.rates[self.curr2.text]/self.rates[self.curr1.text]
        if self.curr2.text in ['BTC']:
            fmt = "{:.8f}"
        else:
            fmt = "{:.2f}"
        self.amount2.text = fmt.format(amount1*k)
        self.app.config.set('General', 'currencies', [self.curr1.text, self.curr2.text])
        self.app.config.write()

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
        self.user_data = {}
        print(self.config)

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')
        config.setdefault('General', 'currencies', '["USD","RUB"]')

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
