#!/usr/bin/env python3

import argparse
from lib import *

#side = "Sell"
side = "Buy"
#start_price = 42000
#stop_price = 48000
start_price = 32000
stop_price = 34000
old_price_gap = 1000
new_price_gap = 100

qty_divisor = old_price_gap / new_price_gap

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("CONVERT ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))
show_ticker()
show_pos()

price = start_price
while price < stop_price:
    if old_price_gap == 1000 and new_price_gap == 100:
        print("")
        print("")
        orders = get_orders(side, price)
        time.sleep(1)
        if len(orders) > 0:
            for order in orders:
                print("")
                result = cancel_order(order)
                time.sleep(1)
                print("")
                if type(result) == dict:
                    new_price = price 
                    for i in range(0, 10):
                        if side == "Sell":
                            sell(new_price, new_price / qty_divisor)
                        else:
                            buy(new_price, new_price / qty_divisor)
                        time.sleep(1)
                        new_price += new_price_gap
        price += old_price_gap
        time.sleep(1)

    elif old_price_gap == 100 and new_price_gap == 1000: 
        print("")
        print("")
        old_price = price
        for i in range(0, 10):
            orders = get_orders(side, old_price)
            time.sleep(1)
            cancel_orders(orders)
            time.sleep(1)
            old_price += old_price_gap
        print("")
        print("")
        if side == "Sell":
            sell(price, price)
        else:
            buy(price, price)
        time.sleep(1)
        price += new_price_gap
        time.sleep(1)





