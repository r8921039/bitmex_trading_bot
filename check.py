#!/usr/bin/env python3

import argparse
from lib import *

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("CONVERT ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))

print("")
#show_pos()

show_ticker()

t = get_ticker()
print(t)
print("")

sell_orders = get_all_sell_orders(log = False, price_reverse = False)

sell_first = sell_orders[0]['price']
sell_last = sell_orders[-1]['price']
sell_n_100 = 0
sell_n_1000 = 0
sell_n_na = 0

for order in sell_orders:
    # price 34900 can have order qty 3400 or 3500
    if order['price'] // 1000 * 100 == order['orderQty'] or (order['price'] // 1000 + 1) * 100 == order['orderQty']:
        sell_n_100 += 1
    elif order['price'] == order['orderQty']: 
        sell_n_1000 += 1
    else:
        print("order['price']" + str(order['price']) + "order['orderQty']" + str(order['orderQty']))
        sell_n_na += 1

print(sell_first)
print(sell_last)
print(sell_n_100)
print(sell_n_1000)
print(sell_n_na)

print("")

buy_orders = get_all_buy_orders(log = False, price_reverse = True)

buy_first = buy_orders[0]['price']
buy_last = buy_orders[-1]['price']
buy_n_100 = 0
buy_n_1000 = 0
buy_n_na = 0

for order in buy_orders:
    # price 34900 can have order qty 3400 or 3500
    if order['price'] // 1000 * 100 == order['orderQty'] or (order['price'] // 1000 + 1) * 100 == order['orderQty']:
        buy_n_100 += 1
    elif order['price'] == order['orderQty']: 
        buy_n_1000 += 1
    else:
        print("order['price']" + str(order['price']) + "order['orderQty']" + str(order['orderQty']))
        buy_n_na += 1

print(buy_first)
print(buy_last)
print(buy_n_100)
print(buy_n_1000)
print(buy_n_na)


