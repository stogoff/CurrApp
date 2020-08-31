from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
#from kivy.core.window import Window
from kivy.config import Config
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
import http.client
import time
import json

Config.set('kivy', 'keyboard_mode', 'systemanddock')
#Window.size = (480, 853)

def get_rates():
    conn = http.client.HTTPSConnection("openexchangerates.org")
    conn.request("GET", "/api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c")
    r = conn.getresponse().read().decode()
    data = json.loads(r)
    # print (json.dumps(data,sort_keys=True, indent=4, separators=(',', ': ')))
    t = time.strftime('%d/%m %H:%M:%S', time.localtime(data['timestamp']))
    usdrub = float(data['rates']['RUB'])
    eurrub = float(data['rates']['RUB']) / float(data['rates']['EUR'])
    return usdrub, eurrub

class Container(GridLayout):
    def calculate(self, curr):
        try:
            usdrub, eurrub = get_rates()
        except:
            usdrub, eurrub = 100,100
        amount = int(self.text_input.text)
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

    def build(self):
        self.theme_man.theme_style = 'Light'
        return Container()


if __name__ == '__main__':
    CurrApp().run()
