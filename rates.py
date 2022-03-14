import json

import requests

CUR = ['USD', 'EUR', 'GBP', 'RUB', 'CHF', 'CAD', 'AMD', 'JPY', 'BTC']


def get_rates():
    url = 'https://openexchangerates.org/api/latest.json?app_id=43d720b184b24b0d8157da339f12f17c'
    outfilename = '/var/www/gba.ee/data.json' # 'data.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        #print(data)
        data1 = {k: data['rates'][k] for k in CUR}
        data1['time'] = data['timestamp']

        with open(outfilename, 'w') as outfile:
            json.dump(data1, outfile)



if __name__ == '__main__':
    get_rates()
