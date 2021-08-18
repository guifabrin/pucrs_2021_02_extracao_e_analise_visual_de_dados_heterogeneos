import requests
import os.path
import json
from datetime import date, timedelta

keys = [
    'A79C0DC0-5144-40DD-AB7C-2C74FAA939CC', #guilherme.franco@eldorado.org.br
    'B17A79DC-EDB4-489A-8D76-9BBEE5D6468B', #guilherme.franco@hp.com
    'DC27DE3A-BB62-4BA7-8FE8-EAC435B15F78', #guilherme.fraco93@edu.pucrs.br
    'E41C583B-82E5-4CEB-9BBD-5021D955C7F7', #guilherme.fabrin@gmail.com
    'DD6BB5E0-BDE6-4060-AFEF-497D71E72E54', #guilherme.fabrin@outlook.com
]


def get(filename, url, headers={}):
    if os.path.isfile(filename):
        file = open(filename, )
        return json.load(file)
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    if "error" in response_json:
        raise Exception(response_json)
    with open(filename, 'w') as outfile:
        json.dump(response_json, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    return response_json


def get_historical_btc():
    start_date = date(2016, 1, 1)
    end_date = date(2022, 1, 1)
    delta = timedelta(days=1)
    while start_date <= end_date:
        str_date = start_date.strftime("%Y-%m-%dT00:00:00")
        str_date_filename = start_date.strftime("%Y%m%d")
        while True:
            if len(keys) == 0:
                break
            try:
                print(get('./cache/get_historical_btc_' + str_date_filename + '.json',
                          'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1MIN&time_start=' + str_date,
                          {'X-CoinAPI-Key': keys[0]}))
                break
            except:
                keys.remove(keys[0])
        start_date += delta


if __name__ == '__main__':
    print(get_historical_btc())
