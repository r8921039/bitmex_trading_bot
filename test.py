#!/usr/bin/env python3

import argparse
from lib import *

side = "Sell"
#side = "Buy"

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("TEST", now.strftime("%d/%m/%Y %H:%M:%S")))
#show_ticker()

orders = client.Order.Order_getOrders(symbol=symbol, reverse=False, count=200, columns='side,price,orderQty,timestamp,orderID,ordStatus', filter=json.dumps({'open' : True, 'side' : side})).result()[0]
orders = sorted(orders, key = lambda i: i['price'], reverse=True)

#out = json.dumps({'open' : 'true', 'side' : side})
#out = json.dumps({'open' : True, 'side' : side})
#print(out)

for order in orders:
    print("{:<15.0f}{:<15s}{:>30s}{:>15s}".format(order['price'], order['side'], order['orderID'], order['ordStatus']))

