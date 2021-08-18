import requests
import os.path
import json
from datetime import date, timedelta

keys = [
    '80A07723-B1E7-4290-9D2A-36A5D28874FD',
    '5E114D36-0CDB-4DC3-BC49-FE4BD9D2282B',
    'EC7DE371-D160-4EF2-BE58-43D0777D7B02',
    'D461BC50-5384-40A0-B62F-9A2D2E6BF72B',
    '07B67CDD-40E9-46B5-8547-501101649BA0',
    'C2787461-7DD4-4FA1-BBAF-EA5745742E85',
    '6B014BDA-D754-4613-A5C4-161C335F8792',
    '3EBDDB08-E400-4A85-BC16-BAEB6A5E2B80',
    'C0F8DC63-A905-45DC-86BF-D8B851D31E77',
    'A79C0DC0-5144-40DD-AB7C-2C74FAA939CC',  # guilherme.franco@eldorado.org.br
    'B17A79DC-EDB4-489A-8D76-9BBEE5D6468B',  # guilherme.franco@hp.com
    'DC27DE3A-BB62-4BA7-8FE8-EAC435B15F78',  # guilherme.fraco93@edu.pucrs.br
    'E41C583B-82E5-4CEB-9BBD-5021D955C7F7',  # guilherme.fabrin@gmail.com
    'DD6BB5E0-BDE6-4060-AFEF-497D71E72E54',  # guilherme.fabrin@outlook.com
]


def get(filename, url, headers=None):
    if headers is None:
        headers = {}
    if os.path.isfile(filename):
        return print(filename, 'already fetched')
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    if "error" in response_json:
        raise Exception(response_json)
    with open(filename, 'w') as outfile:
        json.dump(response_json, outfile, sort_keys=True, indent=4, ensure_ascii=False)
        return print(filename, 'saved')


def get_historical(year_init, year_end, stock_key):
    start_date = date(year_init, 1, 1)
    end_date = date(year_end, 12, 31)
    delta = timedelta(days=1)
    directory = './cache/coinapi/' + stock_key + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    while start_date <= end_date:
        str_date = start_date.strftime("%Y-%m-%dT00:00:00")
        str_date_filename = start_date.strftime("%Y%m%d")
        while True:
            if len(keys) == 0:
                break
            try:
                get(directory + str_date_filename + '.json',
                    'https://rest.coinapi.io/v1/ohlcv/' + stock_key + '/history?period_id=1MIN&time_start=' + str_date,
                    {'X-CoinAPI-Key': keys[0]})
                break
            except Exception as error:
                print(keys[0], error)
                keys.remove(keys[0])
        start_date += delta


if __name__ == '__main__':
    get_historical(2016, 2022, 'BITSTAMP_SPOT_BTC_USD')
