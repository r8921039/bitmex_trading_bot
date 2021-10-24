#!/usr/bin/env python3

import argparse
from lib import *

polling_interval = 3
stats_interval = 60 * 3

now = pytz.utc.localize(datetime.datetime.utcnow())
#now = datetime.datetime(2021, 5, 25, 8, 0, 0, tzinfo=datetime.timezone.utc) # WARNING! for debug! can cause catastrophe 

create_last_buy_sell()
last_buy_time, last_sell_time = read_last_buy_sell(now, now) # overwrite with persisted data

stats_laps_in_sec = 0

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("BITMEX BOT", now.strftime("%d/%m/%Y %H:%M:%S")))
#show_ticker()
show_pos()

while True:
    try: 
        for i in range(1, polling_interval):
            stats_laps_in_sec = stats_laps_in_sec + 1
            time.sleep(1)
            print(".", end =" ", flush=True)
        print(" ", end =" ", flush=True)
    
        if stats_laps_in_sec > stats_interval: 
            print("")
            #show_ticker()
            show_pos()
            stats_laps_in_sec = 0
    
        trades = get_trades("Buy", last_buy_time)
        if trades != TypeError:
            for trade in trades:
                new_price_100 = trade['price'] + 100
                new_price_1000 = trade['price'] + 1000
                new_qty_100 = trade['orderQty']
                new_qty_1000 = trade['orderQty'] + 1000
                # case 100/200: qty doesn't change
                if (trade['price'] // 1000) * 100 == trade['orderQty'] or (new_price_100 // 1000) * 100 == trade['orderQty'] \
                    or (trade['price'] // 1000) * 200 == trade['orderQty'] or (new_price_100 // 1000) * 200 == trade['orderQty']:
                    sell(new_price_100, new_qty_100)
                    # price down: single beep
                    print("\a")
                # case 1000: qty changes. logic in check.py has to match
                elif trade['price'] == trade['orderQty'] and trade['orderQty'] % 1000 == 0:
                    sell(new_price_1000, new_qty_1000)
                    # price down: single beep
                    print("\a")
                else:
                    print("\033[93mSkip a trade as the price is not an order larger than the qty. executed trade side/price/qty:")
                    print("{:>15s}{:>15.2f}{:>15.0f}\033[00m".format(trade['side'], trade['price'], trade['orderQty']))

                if trade['timestamp'] > last_buy_time: 
                    last_buy_time = trade['timestamp'] + datetime.timedelta(microseconds = 1000) # bitmex resolution 1ms
                    write_last_buy_sell(last_buy_time, last_sell_time)
                time.sleep(1)
    
        trades = get_trades("Sell", last_sell_time)
        if trades != TypeError:
            for trade in trades:
                new_price_100 = trade['price'] - 100
                new_price_1000 = trade['price'] - 1000
                new_qty_100 = trade['orderQty']
                new_qty_1000 = trade['orderQty'] - 1000
                # case 100/200: qty doesn't change
                if (trade['price'] // 1000) * 100 == trade['orderQty'] or (new_price_100 // 1000) * 100 == trade['orderQty'] \
					or (trade['price'] // 1000) * 200 == trade['orderQty'] or (new_price_100 // 1000) * 200 == trade['orderQty']:
                    buy(new_price_100, new_qty_100)
                    # price up: double beep
                    print("\a\a")
                # case 1000: qty changes. logic in check.py has to match
                elif trade['price'] == trade['orderQty'] and trade['orderQty'] % 1000 == 0:
                    buy(new_price_1000, new_qty_1000)
                    # price up: double beep
                    print("\a\a")
                else:
                    print("\033[93mSkip a trade as the price is not an order larger than the qty. executed trade side/price/qty:")
                    print("{:>15s}{:>15.2f}{:>15.0f}\033[00m".format(trade['side'], trade['price'], trade['orderQty']))

                if trade['timestamp'] > last_sell_time: 
                    last_sell_time = trade['timestamp'] + datetime.timedelta(microseconds = 1000) # bitmex resolution 1ms
                    write_last_buy_sell(last_buy_time, last_sell_time)
                time.sleep(1)
    except:
        print("\033[91mBOT: Uncaught Exception!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

