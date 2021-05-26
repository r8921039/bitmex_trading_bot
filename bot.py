#!/usr/bin/env python3

import argparse
from lib import *

polling_interval = 10
stats_interval = 60 * 10

now = pytz.utc.localize(datetime.datetime.utcnow())
#now = datetime.datetime(2021, 5, 25, 8, 0, 0, tzinfo=datetime.timezone.utc) # WARNING! for debug! can cause catastrophe 

last_buy_time = now 
last_sell_time = now 
stats_laps_in_sec = 0

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("BITMEX BOT", now.strftime("%d/%m/%Y %H:%M:%S")))
show_ticker()
show_pos()

while True:
    for i in range(1, polling_interval):
        stats_laps_in_sec = stats_laps_in_sec + 1
        time.sleep(1)
        print(".", end =" ", flush=True)
    print(" ", end =" ", flush=True)

    if stats_laps_in_sec > stats_interval: 
        print("")
        show_ticker()
        show_pos()
        stats_laps_in_sec = 0

    trades = get_trades("Buy", last_buy_time)
    if trades != TypeError:
        for trade in trades:
            price = trade['price'] + 1000
            if trade['orderQty'] >= 1000:
                qty = trade['orderQty'] + 1000
            else:
                qty = trade['orderQty']
            sell(price, qty)
            if trade['timestamp'] > last_buy_time : 
                #last_buy_time = trade['timestamp'] + datetime.timedelta(microseconds = 1)
                last_buy_time = trade['timestamp'] + datetime.timedelta(seconds = 1)

    trades = get_trades("Sell", last_sell_time)
    if trades != TypeError:
        for trade in trades:
            price = trade['price'] - 1000
            if trade['orderQty'] >= 1000:
                qty = trade['orderQty'] - 1000
            else:
                qty = trade['orderQty']
            buy(price, qty)
            if trade['timestamp'] > last_sell_time : 
                #last_sell_time = trade['timestamp'] + datetime.timedelta(microseconds = 1)
                last_sell_time = trade['timestamp'] + datetime.timedelta(seconds = 1)





