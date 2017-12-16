import sys
import os
import krakenex
from urllib3.exceptions import ProtocolError
from pprint import pprint
from pykrakenapi import KrakenAPI
import requests

def get_asset_pairs(k):
    while True:
        try:
            r = k.query_public('AssetPairs')
        except:
            continue
        else:
            ap = r['result']
            break
    return ap

def retry(f, *d):
    while True:
        try:
            r = f(*d)
        except ProtocolError:
            print("Protcol error. Retrying...")
            continue
        except ConnectionError:
            print("Connection error. Retrying...")
            continue
        except:
            print("Unknown error. Aborting")
            raise
            return
        else:
            return r

def df_col_to_double(df, *l):
    for v in l:
        df[v] = df[v].astype('double')
    return df

kraken_key, kraken_secret = open('kraken.key').read().split('\n')[0:2]
k = krakenex.API(key=kraken_key,secret=kraken_secret)
kapi = KrakenAPI(k)

abal = kapi.get_account_balance()
ab = abal[abal['vol'] != 0].index
ap = get_asset_pairs(k)
get_name = lambda n: list(filter(lambda x: ap[x]['base'] == n and ap[x]['quote']=='ZEUR', ap))
pairs = list(map(get_name, ab))
pairs = list(filter(lambda x: '.d' not in x, [ x for l in pairs for x in l ]))

get_ohlc = lambda x: list(map(lambda x: kapi.get_ohlc_data(x)[0], x))
r = retry(get_ohlc, pairs)
r = { k:v for k, v in zip(pairs, r)}

conv = {k:v for k,v in zip(pairs,list(map(lambda x: (r[x]['high'].mean()+r[x]['low'].mean())/2, r)))}
nn = {ap[k]['base']:k for k in conv}
for k,v in nn.items():
    abal.loc[k, 'usd'] = abal.loc[k, 'vol'] * conv[v]
print('Portfolio overview')
print(abal)
co = retry(kapi.get_closed_orders)[0]
oo = retry(kapi.get_open_orders)
op = retry(kapi.get_open_positions)

spread = retry(kapi.get_recent_spread_data,'XETHZEUR')[0]
trades = retry(kapi.get_recent_trades,'XETHZEUR')[0]
orders = retry(kapi.get_order_book, 'XETHZEUR', 500)
orders = {k:v for k, v in zip(['asks','bids'], map(lambda x: df_col_to_double(x,'price', 'volume'),orders))}
for k,v in orders.items():
    print('{} price: {} +- {}'.format(k, orders[k]['price'].mean(),orders[k]['price'].std()))
