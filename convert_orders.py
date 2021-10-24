#!/usr/bin/env python3

import argparse
from lib import *

#side = "Sell"
side = "Buy"
action = "Breakdown"
#action = "Combine"

# currently only works for breakdowns.
qty_multiple = 1

if side == "Sell":
    start_price = 70000 # inclusive
    stop_price  = 75000 # exclusive
elif side == "Buy":
    start_price = 55000 # includsive
    stop_price  = 58000 # exclusive
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
        time.sleep(2)
        if len(orders) > 0:
            # cancel all matching orders
            for order in orders:
                # 2022-10-24 Cancel all combined orders of the same price found but breakdonw only once 
                breakdown_done_once = False
                print("")
                if order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0:
                    result = cancel_order(order)
                    time.sleep(2)
                    print("")
                    if type(result) == dict:
                        if breakdown_done_once == False:
                            breakdown_done_once = True
                            new_price = price
                            # since 2021-06-07, bitmex requires qty multiples of 100
                            new_qty = (price // 1000) * 100 * qty_multiple
                            for i in range(0, 10):
                                if side == "Sell":
                                    sell(new_price, new_qty)
                                else:
                                    buy(new_price, new_qty)
                                time.sleep(5)
                                new_price += new_price_gap
                        else: 
                            print("\033[93mSKIP! Avoid multiple breakdowns on same price!\033[00m")
                    else: 
                        print("\033[93mWARN! Cancel order FAILED!\033[00m")
                else:
                    print("\033[93mSKIP! PRICE/QTY not qualified!\033[00m")
        price += old_price_gap
        time.sleep(3)

    # Combine
    elif old_price_gap == 100 and new_price_gap == 1000: 
        print("")
        print("")
        old_price = price
        for i in range(0, 10):
            orders = get_orders(side, old_price)
            time.sleep(3)
            cancel_orders(orders)
            time.sleep(3)
            old_price += old_price_gap
        print("")
        print("")
        time.sleep(3)
        if side == "Sell":
            sell(price, price)
        else:
            buy(price, price)
        price += new_price_gap
        time.sleep(3)

print("\a\a\a")




