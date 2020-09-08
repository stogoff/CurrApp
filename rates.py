import json

import requests

CUR = ['USD', 'EUR', 'GBP', 'RUB', 'CHF', 'CAD', 'JPY', 'BTC']


def get_rates():
    url = 'https://openexchangerates.org/api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        data1 = {k: data['rates'][k] for k in CUR}
        with open('/var/www/gba.ee/data.json', 'w') as outfile:
            json.dump(data1, outfile)
    return data1


if __name__ == '__main__':
    get_rates()