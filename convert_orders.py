#!/usr/bin/env python3

import argparse
from lib import *

#side = "Sell"
side = "Buy"
action = "Breakdown"
#action = "Combine"
if side == "Sell":
    start_price = 42000 # inclusive
    stop_price  = 45000 # exclusive
elif side == "Buy":
    start_price = 26000 # includsive
    stop_price  = 29000 # exclusive
else:
    print("\033[91mError! side must be Buy/Sell\033[00m")
    sys.exit()

if action == "Breakdown":
    old_price_gap = 1000
    new_price_gap = 100
elif action  == "Combine": 
    old_price_gap = 100
    new_price_gap = 1000
else:
    print("\033[91mError! action must be Breakdown/Combine\033[00m")
    sys.exit()

qty_divisor = old_price_gap / new_price_gap

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("CONVERT ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))
show_ticker()
show_pos()

price = start_price
while price < stop_price:
    # Breakdown
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
                        time.sleep(2)
                        new_price += new_price_gap
        price += old_price_gap
        time.sleep(1)

    # Conbine
    elif old_price_gap == 100 and new_price_gap == 1000: 
        print("")
        print("")
        old_price = price
        for i in range(0, 10):
            orders = get_orders(side, old_price)
            time.sleep(1)
            cancel_orders(orders)
            time.sleep(2)
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





