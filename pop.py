#!/usr/bin/env python3

import argparse
from lib import *

side = "Sell"
#side = "Buy"

start_price = 48000
stop_price = 60000

price_gap = 1000
#price_gap = 500
#price_gap = 100

qty_divisor = 1000 / price_gap

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("POPULATE ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))
show_ticker()
show_pos()

price = start_price
while price < stop_price:
    qty = price / qty_divisor
    if side == "Sell":
        sell(price, qty)
    else: 
        buy(price, qty)
    time.sleep(1)
    price += price_gap




