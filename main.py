import ast
import os
import re
import sys
import time

import certifi
import requests
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.logger import Logger
from kivy.properties import BooleanProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_hex_from_color
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.toast import toast
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.button import BaseRectangularButton, BaseRaisedButton, BasePressedButton

# from kivy.core.window import Window
# Window.size = (480, 853)
__version__ = '0.3.19'



from kivymd.uix.navigationdrawer import NavigationLayout

os.environ['SSL_CERT_FILE'] = certifi.where()
CRYPTO = ['BTC',]

def get_rates():
    url = 'https://gba.ee/data.json'
    response = requests.get(url)
    Logger.info('response status code: {}'.format(response.status_code))
    data = response.json()
    return data


class RaisedButton(
    BaseRectangularButton,
    RectangularElevationBehavior,
    BaseRaisedButton,
    BasePressedButton,
):
    pass


class RaisedIconButton(RaisedButton):
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


class ContentNavigationDrawer(BoxLayout):
    pass


class Calculator(NavigationLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rates = {}
        self.app = MDApp.get_running_app()
        self.app.user_data = ast.literal_eval(self.app.config.get('General', 'user_data'))
        self.app.main_screen = self
        self.curr1.text, self.curr2.text = ast.literal_eval(self.app.config.get('General', 'currencies'))
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
        self.show_pairs()

    def show_pairs(self):
        s1 = self.curr1.text
        s2 = self.curr2.text
        k = self.rates[s2] / self.rates[s1]
        if s1 in CRYPTO:
            fmt1 = "{}/{}:\n{:.2f}"
            fmt2 = "{}/{}:\n[size=15sp]{:.8f}[/size]"
        elif s2 in CRYPTO:
            fmt1 = "{}/{}:\n[size=15sp]{:.8f}[/size]"
            fmt2 = "{}/{}:\n{:.2f}"
        else:
            fmt1 = fmt2 = "{}/{}:\n{:.4f}"
        self.rate1.text = fmt1.format(self.curr1.text, self.curr2.text, k)
        self.rate2.text = fmt2.format(self.curr2.text, self.curr1.text, 1 / k)

    def calculate(self):
        self.update_rates()
        am1_txt = self.amount1.text
        s1, s2 = self.curr1.text, self.curr2.text
        if am1_txt == '0':
            self.amount2.text = '0'
        else:
            if am1_txt[-1] in "*-/+":
                am1_txt = am1_txt[:-1]
            if re.match(r'.*[+\-*/]+.*', am1_txt):
                try:
                    amount1 = float(eval(am1_txt))
                except:
                    amount1 = 0
            else:
                try:
                    amount1 = float(am1_txt)
                except ValueError:
                    amount1 = 0
                    Logger.exception('error')
            k = self.rates[s2] / self.rates[s1]
            if s2 in CRYPTO:
                fmt = "{:.8f}"
            else:
                fmt = "{:.2f}"
            self.amount2.text = fmt.format(amount1 * k)
        self.app.config.set('General', 'currencies', [s1, s2])
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
            try:
                if self.curr1.text in CRYPTO:
                    fmt = '{:.8f}'
                else:
                    fmt = '{:.2f}'
                self.amount1.text = fmt.format(eval(self.amount1.text.strip('*-+/'))).rstrip('0').rstrip('.')
            except:
                self.amount1.text = '0'
        elif str(value) in "*-/+":
            if self.amount1.text == '0':
                pass
            else:
                if self.amount1.text[-1] not in "*-/+":
                    self.amount1.text += str(value)
        else:
            if self.amount1.text == '0':
                self.amount1.text = ''

            self.amount1.text += str(value)
        self.calculate()


class CurrApp(MDApp):
    theme_man = ThemeManager()
    title = "Currency calc"

    def __init__(self, **kwargs):
        self.config = ConfigParser()
        self.user_data = {}
        self.manager = None
        self.nav_drawer = None
        self.main_screen = None
        self.start_screen = None
        self.exit_interval = False
        self.list_previous_screens = ['main']
        self.title = "Currency Calculator"
        self.version = __version__
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

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.set_state()
            self.back_screen(event=keyboard)
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self, event=None):
        if event in (1001, 27):
            if self.manager.current == 'main':
                self.dialog_exit()
                return
            try:
                self.manager.current = self.list_previous_screens.pop()
            except:
                self.manager.current = 'main'
            self.start_screen.ids.toolbar.title = self.title
            self.start_screen.ids.toolbar.left_action_items = \
                [['menu', lambda x: self.nav_drawer.set_state()]]

    def show_license(self, *args):
        self.nav_drawer.set_state()

        self.start_screen.ids.text_license.text = ('%s') % open(
                    os.path.join(self.directory, 'LICENSE'), encoding='utf-8').read()

        self.manager.current = 'license'
        self.start_screen.ids.toolbar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.start_screen.ids.toolbar.title = 'MIT LICENSE'

    def show_about(self, *args):
        Logger.info('enter show_about')
        self.nav_drawer.set_state()
        Logger.info('enter state')
        self.start_screen.ids.about_label.text = (
                u'[size=50][b]Currency Calculator [/b][/size]\n\n' +
                u'[b]Version:[/b] {version}\n' +
                u'[b]License:[/b] MIT\n\n' +
                u'[size=40][b]Developer[/b][/size]\n\n' +
                u'[ref=SITE_PROJECT]' +
                u'[color={link_color}]Rost[/color][/ref]\n\n' +
                #u'[b]Source code:[/b] ' +
                #u'[ref=https://github.com/stogoff/CurrApp]' +
                #u'[color={link_color}]GitHub[/color][/ref]'+
                '').format(
            version=__version__,
            link_color=get_hex_from_color(self.theme_cls.primary_color)
        )
        Logger.info(' text')
        self.manager.current = 'about'
        Logger.info('set current')
        self.start_screen.ids.toolbar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        Logger.info('last command')


    def select_locale(self, *args): # TODO
        pass

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)

        Clock.schedule_interval(check_interval_press, 1)
        toast('Press Back to Exit')

    def build(self):
        self.theme_man.theme_style = 'Light'
        self.start_screen = Calculator()
        self.manager = self.start_screen.ids.s_manager
        self.nav_drawer = self.start_screen.ids.nav_drawer
        # temporary disabled
        #self.start_screen.ids.lic_label.disabled = True
        self.start_screen.ids.lang_label.disabled = True

        return self.start_screen


if __name__ == '__main__':
    CurrApp().run()
