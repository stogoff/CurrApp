from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
#from kivy.core.window import Window
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
#Window.size = (480, 853)

def get_rates():
    url = 'https://openexchangerates.org//api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    #req = urllib.request.Request(url)
    #Logger.info('string20.')
    #with urllib.request.urlopen(req) as f:
    #    Logger.info(f.status)
    #    Logger.info(f.reason)
    #    text = f.read().decode('utf-8')
    #    data = json.loads(text)
    #    Logger.info(float(data['rates']['RUB']))
    response = requests.get(url)
    data = response.json()
    ##t = time.strftime('%d/%m %H:%M:%S', time.localtime(data['timestamp']))
    usdrub = float(data['rates']['RUB'])
    eurrub = float(data['rates']['RUB']) / float(data['rates']['EUR'])
    return usdrub, eurrub


class Container(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None

    def calculate(self, curr):
        self.app = MDApp.get_running_app()
        self.app.user_data = ast.literal_eval(
            self.app.config.get('General', 'user_data'))
        if 'update' in self.app.user_data.keys() and  (time.time() - self.app.user_data['update'] < 120):
            usdrub = self.app.user_data['usdrub']
            eurrub = self.app.user_data['eurrub']

        else:
            try:
                usdrub, eurrub = get_rates()

                self.app.user_data['update'] = int(time.time())
                self.app.user_data['usdrub'] = usdrub
                self.app.user_data['eurrub'] = eurrub

                self.app.config.set('General', 'user_data', self.app.user_data)
                self.app.config.write()
            except:
                usdrub, eurrub = 100,100
                Logger.exception('Something happened!')
        try:
            amount = int(self.text_input.text)
        except:
            amount = 0
        if curr == 'USD':
            self.usd.text = '{:.2f}'.format(amount)
            self.rub.text = '{:.2f}'.format(amount * usdrub)
            self.eur.text = '{:.2f}'.format(amount * usdrub / eurrub)
        if curr == 'RUB':
            self.rub.text = '{:.2f}'.format(amount)
            self.usd.text = '{:.2f}'.format(amount / usdrub)
            self.eur.text = '{:.2f}'.format(amount / eurrub)
        if curr == 'EUR':
            self.usd.text = '{:.2f}'.format(amount * eurrub / usdrub)
            self.rub.text = '{:.2f}'.format(amount * eurrub)
            self.eur.text = '{:.2f}'.format(amount)


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
