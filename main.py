from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.config import ConfigParser
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
from kivy.logger import Logger
import requests
import certifi
import os
import ast
import time
import re

from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.button import BaseFlatIconButton, BaseRectangularButton, BaseRaisedButton, BasePressedButton

os.environ['SSL_CERT_FILE'] = certifi.where()
# from kivy.core.window import Window
# Window.size = (480, 853)
__version__ = '0.3.13'


def get_rates():
    url = 'https://openexchangerates.org/api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    response = requests.get(url)
    Logger.info('response status code: {}'.format(response.status_code))
    data = response.json()
    return data['rates']


class MYRaisedButton(
    BaseRectangularButton,
    RectangularElevationBehavior,
    BaseRaisedButton,
    BasePressedButton,
):
    pass


class MYRaisedIconButton(MYRaisedButton):
    icon = StringProperty("android")
    """
    Button icon.

    :attr:`icon` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'android'`.
    """

    text = StringProperty("")
    """Button text.

    :attr:`text` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    button_label = BooleanProperty(False)


class Main(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.curr1.text, self.curr2.text = ast.literal_eval(self.app.config.get(
            'General', 'currencies'))
        self.app.user_data = ast.literal_eval(self.app.config.get(
            'General', 'user_data'))
        self.rates = {}
        self.update_rates()

    def update_rates(self):
        if 'update' not in self.app.user_data.keys() or (time.time() - self.app.user_data['update'] > 1800):
            self.rates = get_rates()
            self.app.user_data['update'] = int(time.time())
            self.app.user_data['rates'] = self.rates
            self.app.config.set('General', 'user_data', self.app.user_data)
            self.app.config.write()
        else:
            self.rates = self.app.user_data['rates']
        self.timelabel.text = time.strftime("rates updated: %d.%m.%Y, %H:%M:%S",
                                            time.localtime(self.app.user_data['update']))
        k = self.rates[self.curr2.text] / self.rates[self.curr1.text]
        self.rate1.text = "{}/{}:\n{:.4f}".format(self.curr1.text, self.curr2.text, k)

        self.rate2.text = "{}/{}:\n{:.4f}".format(self.curr2.text, self.curr1.text, 1 / k)

    def calculate(self):
        self.update_rates()

        if re.match(r'.*[+\-*/].*', self.amount1.text):
            try:
                amount1 = float(eval(self.amount1.text))
            except:
                amount1 = 0
        else:
            try:
                amount1 = float(self.amount1.text)
            except ValueError:
                amount1 = 0
                Logger.exception('error')
        k = self.rates[self.curr2.text] / self.rates[self.curr1.text]
        if self.curr2.text in ['BTC']:
            fmt = "{:.8f}"
        else:
            fmt = "{:.2f}"
        self.amount2.text = fmt.format(amount1 * k)
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
        elif value == 'B':
            if len(self.amount1.text) > 1:
                self.amount1.text = self.amount1.text[:-1]
            else:
                self.amount1.text = '0'
        elif value == '=':
            self.amount1.text = str(eval(self.amount1.text.strip('*-+/')))
        else:
            if self.amount1.text == '0':
                self.amount1.text = ''
                if str(value) in "*-/+":
                    value = '0'
            self.amount1.text += str(value)
        self.calculate()



class CurrApp(MDApp):
    theme_man = ThemeManager()
    title = "Currency calc"

    def __init__(self, **kwargs):
        self.config = ConfigParser()
        self.user_data = {}
        self.title = "Currency Calculator"
        self.theme_cls.primary_palette = "Blue"
        super().__init__(**kwargs)

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')
        config.setdefault('General', 'currencies', '["USD","RUB"]')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))

    def get_application_config(self, **kwargs):
        return super(CurrApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        self.theme_man.theme_style = 'Light'
        return Main()


if __name__ == '__main__':
    CurrApp().run()
