#!/usr/bin/env python3

import argparse
from lib import *

### WARNING! There is a bug in bootstrapping check.py. It can't start with empty orders as it will use 0 to start populate sell orders <- bug
### To work around the bug: 
### 1) Run ./check.py without -f (fix mode) and get target buy/sell x00/1000 first/last orders
### 2) Manually enter those boundary orders 
### 3) Run ./check.py -f (fix mode and turn on verbose). Better monitor the population of all orders and stop the program if bug shows up.   
### 4) Clear .last_buy_sell file before restarting bot.py if running into the bug otherwise it will re-execute wrongly executed orders

polling_interval = 60 * 1
stats_interval = 60 * 30
verbose = False
wall_x00 = 8000
wall_1000 = 8000

# order size 100 or 200
qty = 100

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fix", help="add missing and cancel duplicate orders", action="store_true")
args = parser.parse_args()
if args.fix:
    fix_mode = True
else:
    fix_mode = False

def fix_range():
    try:
        ticker = get_ticker()
        pos = get_pos()
        liq_price = 0
        is_long = True
        if pos != None:
            liq_price = int(pos['liquidationPrice']) // 1000 * 1000
            if pos['currentQty'] >= 0:
                liq_price = liq_price + 2000 
            else:
                is_long = False
        if is_long and liq_price > ticker:
            print("\033[91mERROR! Long pos has Liq Price (:.0f) > Ticker Price {:.0f}\033[00m".format(liq_price, ticker))
            raise ValueError("Liq Price > Ticker Price")
        elif (not is_long) and liq_price < ticker:
            print("\033[91mERROR! Short pos has Liq Price (:.0f) < Ticker Price {:.0f}\033[00m".format(liq_price, ticker))
            raise ValueError("Liq Price < Ticker Price")

        print("")
        print("\033[93m{:<30s}{:>30.0f}\033[00m\033[00m".format("[LIQ PRICE FOR RANGE]", liq_price))
        print("", flush=True)

        #
        # [RANGE] GET TARGET/CURRENT BUY
        # 

        target_buy_last_x00 = int(ticker) // 100 * 100 - 100
        target_buy_first_x00 = target_buy_last_x00 - wall_x00
        if pos and is_long and target_buy_first_x00 < liq_price:
            print("\033[91mTarget First Buy X00 ({:.0f}) < Liq Price ({:.0f}). Use Liq Price\033[00m".format(target_buy_first_x00, liq_price)) 
            target_buy_first_x00 = liq_price
        target_buy_last_1000 = target_buy_first_x00 // 1000 * 1000
        if target_buy_last_1000 >= target_buy_first_x00:
            target_buy_last_1000 = target_buy_last_1000 - 1000
        target_buy_first_1000 = target_buy_last_1000 - wall_1000
        if pos and is_long and target_buy_first_1000 < liq_price:
            print("\033[91mTarget First Buy 1000 ({:.0f}) < Liq Price ({:.0f}). Use Liq Price\033[00m".format(target_buy_first_1000, liq_price))
            target_buy_first_1000 = liq_price
        if target_buy_first_1000 < 1000:
            print("\033[91mFirst RANGE BUY less than 1000!\033[00m")
            target_buy_first_1000 = 1000

        buy_first_x00 = 0
        buy_first_1000 = 0
        buy_last_x00 = 0
        buy_last_1000 = 0
        buy_orders = get_all_buy_orders(log = False, price_reverse = False)
        for order in buy_orders:
            if order['price'] // 1000 * qty == order['orderQty'] or (order['price'] // 1000) * qty + qty == order['orderQty']:
                if buy_last_x00 == 0:
                    buy_first_x00 = int(order['price'])
                    buy_last_x00 = buy_first_x00
                else:
                    buy_last_x00 = int(order['price'])
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0:
                if buy_last_1000 == 0:
                    buy_first_1000 = int(order['price'])
                    buy_last_1000 = buy_first_1000
                else:
                    buy_last_1000 = int(order['price'])

        if verbose or target_buy_first_1000 != buy_first_1000 or target_buy_last_1000 != buy_last_1000 or target_buy_first_x00 != buy_first_x00:
            print("")
            print("\033[93m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("TARGET  FIRST 1000 BUY", "LAST 1000 BUY", "FIRST X00 BUY", "LAST X00 BUY"))
            print("\033[93m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(target_buy_first_1000, target_buy_last_1000, target_buy_first_x00, target_buy_last_x00))
            print("\033[32m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("CURRENT FIRST 1000 BUY", "LAST 1000 BUY", "FIRST X00 BUY", "LAST X00 BUY"))
            print("\033[32m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(buy_first_1000, buy_last_1000, buy_first_x00, buy_last_x00))
            print("")

        #
        # [RANGE] GET TARGET/CURRENT SELL
        #

        target_sell_first_x00 = int(ticker) // 100 * 100 + 100
        target_sell_last_x00 = target_sell_first_x00 + wall_x00
        if pos and (not is_long) and liq_price < target_sell_last_x00:
            print("\033[91mTarget Last Sell X00 ({:.0f}) > Liq Price ({:.0f}). Use Liq Price\033[00m".format(target_sell_last_x00, liq_price))
            target_sell_last_x00 = liq_price 
        target_sell_first_1000 = target_sell_last_x00 // 1000 * 1000 + 1000
        target_sell_last_1000 = target_sell_first_1000 + wall_1000
        if pos and (not is_long) and liq_price < target_sell_last_1000:
            print("\033[91mTarget Last Sell 1000 ({:.0f}) > Liq Price ({:.0f}). Use Liq Price\033[00m".format(target_sell_last_1000, liq_price))
            target_sell_last_1000 = liq_price
        sell_first_x00 = 0
        sell_first_1000 = 0
        sell_last_x00 = 0
        sell_last_1000 = 0
        sell_orders = get_all_sell_orders(log = False, price_reverse = False)
        for order in sell_orders:
            if order['price'] // 1000 * qty == order['orderQty'] or (order['price'] // 1000) * qty - qty == order['orderQty']:
                if sell_last_x00 == 0:
                    sell_first_x00 = int(order['price'])
                    sell_last_x00 = sell_first_x00
                else:
                    sell_last_x00 = int(order['price'])
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0:
                if sell_last_1000 == 0:
                    sell_first_1000 = int(order['price'])
                    sell_last_1000 = sell_first_1000
                else:
                    sell_last_1000 = int(order['price'])

        if verbose or target_sell_last_x00 != sell_last_x00 or target_sell_first_1000 != sell_first_1000 or target_sell_last_1000 != sell_last_1000:
            print("")
            print("\033[93m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("TARGET  FIRST X00 SELL", "LAST X00 SELL", "FIRST 1000 SELL", "LAST 1000 SELL"))
            print("\033[93m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(target_sell_first_x00, target_sell_last_x00, target_sell_first_1000, target_sell_last_1000))
            print("\033[35m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("CURRENT FIRST X00 SELL", "LAST X00 SELL", "FIRST 1000 SELL", "LAST 1000 SELL"))
            print("\033[35m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(sell_first_x00, sell_last_x00, sell_first_1000, sell_last_1000))
            print("")

        #
        # [RANGE CANCEL] BUY/SELL
        #

        # PRICE GOING UP
        if buy_first_x00 < target_buy_first_x00 and (not (buy_first_x00 == 0 and buy_last_x00 == 0)):
            if verbose:
                print("CANCEL BUY X00:{:.0f}..{:.0f}".format(buy_first_x00, target_buy_first_x00))
            for p in range(buy_first_x00, target_buy_first_x00, 100):
                if fix_mode:
                    orders = get_orders("Buy", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] // 1000 * qty == order['orderQty'] or order['price'] // 1000 * qty == (order['orderQty'] - qty):
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if buy_first_1000 < target_buy_first_1000 and (not (buy_first_1000 == 0 and buy_last_1000 == 0)):
            if verbose:
                print("CANCEL BUY 1000:{:.0f}..{:.0f}".format(buy_first_1000, target_buy_first_1000))
            for p in range(buy_first_1000, target_buy_first_1000, 1000):
                if fix_mode:
                    orders = get_orders("Buy", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if sell_first_1000 < target_sell_first_1000 and (not (sell_first_1000 == 0 and sell_last_1000 == 0)):
            if verbose:
                print("CANCEL SELL 1000:{:.0f}..{:.0f}".format(sell_first_1000, target_sell_first_1000))
            for p in range(sell_first_1000, target_sell_first_1000, 1000):
                if fix_mode:
                    orders = get_orders("Sell", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        # PRICE GOING DOWN
        if target_sell_last_x00 < sell_last_x00 and (not (target_sell_last_x00 == 0 and sell_last_x00 == 0)):
            if verbose:
                print("CANCEL SELL X00:{:.0f}..{:.0f}".format(target_sell_last_x00 + 100, sell_last_x00 + 100))
            for p in range(target_sell_last_x00 + 100, sell_last_x00 + 100, 100):
                if fix_mode:
                    orders = get_orders("Sell", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] // 1000 * qty == order['orderQty'] or order['price'] // 1000 * qty == (order['orderQty'] + qty):
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if target_sell_last_1000 < sell_last_1000 and (not (target_sell_last_1000 == 0 and sell_last_1000 == 0)):
            if verbose:
                print("CANCEL SELL 1000:{:.0f}..{:.0f}".format(target_sell_last_1000 + 1000, sell_last_1000 + 1000))
            for p in range(target_sell_last_1000 + 1000, sell_last_1000 + 1000, 1000):
                if fix_mode:
                    orders = get_orders("Sell", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if target_buy_last_1000 < buy_last_1000 and (not (target_buy_last_1000 == 0 and buy_last_1000 == 0)):
            if verbose:
                print("CANCEL BUY 1000:{:.0f}..{:.0f}".format(target_buy_last_1000 + 1000, buy_last_1000 + 1000))
            for p in range(target_buy_last_1000 + 1000, buy_last_1000 + 1000, 1000):
                if fix_mode:
                    orders = get_orders("Buy", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        #
        # [RANGE ADD] BUY/SELL
        #

        # PRICE GOING UP
        if sell_last_x00 < target_sell_last_x00:
            if verbose:
                print("ADD SELL X00:{:.0f}..{:.0f}".format(sell_last_x00 + 100, target_sell_last_x00 + 100))
            for p in range(sell_last_x00 + 100, target_sell_last_x00 + 100, 100):
                if fix_mode:
                    sell(p, (p // 1000) * qty)
                    time.sleep(3)
                else:
                    print(p)

        if sell_last_1000 < target_sell_last_1000:
            if verbose:
                print("ADD SELL 1000:{:.0f}..{:.0f}".format(sell_last_1000 + 1000, target_sell_last_1000 + 1000))
            for p in range(sell_last_1000 + 1000, target_sell_last_1000 + 1000, 1000):
                if fix_mode:
                    sell(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)

        if buy_last_1000 < target_buy_last_1000 and target_buy_first_1000 < target_buy_last_1000:
            if buy_last_1000 < target_buy_first_1000:
                buy_last_1000 = target_buy_first_1000 - 1000 
            if verbose:
                print("ADD BUY 1000:{:.0f}..{:.0f}".format(buy_last_1000 + 1000, target_buy_last_1000 + 1000))
            for p in range(buy_last_1000 + 1000, target_buy_last_1000 + 1000, 1000):
                if fix_mode:
                    buy(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)

        # PRICE GOING DOWN
        if target_buy_first_x00 < buy_first_x00:
            if verbose:
                print("ADD BUY X00:{:.0f}..{:.0f}".format(target_buy_first_x00, buy_first_x00))
            for p in range(target_buy_first_x00, buy_first_x00, 100):
                if fix_mode:
                    buy(p, (p // 1000) * qty)
                    time.sleep(3)
                else:
                    print(p)

        if target_buy_first_1000 < buy_first_1000:
            if verbose:
                print("ADD BUY 1000:{:.0f}..{:.0f}".format(target_buy_first_1000, buy_first_1000))
            for p in range(target_buy_first_1000, buy_first_1000, 1000):
                if fix_mode:
                    buy(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)
        
        if target_sell_first_1000 < sell_first_1000:
            if verbose:
                print("ADD SELL 1000:{:.0f}..{:.0f}".format(target_sell_first_1000, sell_first_1000))
            for p in range(target_sell_first_1000, sell_first_1000, 1000):
                if fix_mode:
                    sell(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)
    except:
        print("\033[91mRANGE: Uncaught Exception!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def fix_gap():
    try:
        first_p_100 = 0
        first_p_200 = 0
        first_p_1000 = 0
        
        prev_p_100 = 0
        prev_p_200 = 0
        prev_p_1000 = 0
        
        buy_orders = get_all_buy_orders(log = False, price_reverse = False)
        for order in buy_orders:
            # buy order at 34900 can have qty 3400 or 3500
            # buy order at 35000 must have qty 3500
            if order['price'] // 1000 * 100 == order['orderQty'] or (order['price'] // 1000) * 100 + 100 == order['orderQty']:
                if prev_p_100 == 0:
                    first_p_100 = order['price']
                    prev_p_100 = first_p_100
                else:
                    if order['price'] == prev_p_100 + 100:
                        pass
                    else:
                        print("")
                        print("\033[93mBUY 100 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_100))
                        if fix_mode == True:
                            print("FIXING BUY 100...\033[00m")
                            if order['price'] == prev_p_100:
                                # tripple beeps
                                #print("\a\a\a") 
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_100 + 100 and order['price'] % 100 == 0:
                                for price in range(int(prev_p_100) + 100, int(order['price']) - 1, 100):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    buy(price, price // 1000 * 100)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING BUY 100... DONE!\033[00m")
                        else:
                            print("SKIP FIXING BUY 100\033[00m")
                    prev_p_100 = order['price']
            elif order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 200 + 200 == order['orderQty']:
                if prev_p_200 == 0:
                    first_p_200 = order['price']
                    prev_p_200 = first_p_200
                else:
                    if order['price'] == prev_p_200 + 100:
                        pass
                    else:
                        print("")
                        print("\033[93mBUY 200 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_200))
                        if fix_mode == True:
                            print("FIXING BUY 200...\033[00m")
                            if order['price'] == prev_p_200:
                                # tripple beeps
                                #print("\a\a\a")
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_200 + 100 and order['price'] % 100 == 0:
                                for price in range(int(prev_p_200) + 100, int(order['price']) - 1, 100):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    buy(price, price // 1000 * 200)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING BUY 200... DONE!\033[00m")
                        else:
                            print("SKIP FIXING BUY 200\033[00m")
                    prev_p_200 = order['price']
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0: 
                if prev_p_1000 == 0:
                    first_p_1000 = order['price']
                    prev_p_1000 = first_p_1000
                else:
                    if order['price'] == prev_p_1000 + 1000:
                        pass
                    else:
                        print("")
                        print("\033[93mBUY 1000 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_1000))
                        if fix_mode == True:
                            print("FIXING BUY 1000...\033[00m")
                            if order['price'] == prev_p_1000:
                                # tripple beeps
                                #print("\a\a\a")
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_1000 + 1000 and order['price'] % 1000 == 0 and order['price'] < prev_p_1000 + 10000:
                                for price in range(int(prev_p_1000) + 1000, int(order['price']) - 1, 1000):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    buy(price, price)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING BUY 1000... DONE!\033[00m")
                        else:
                            print("\033[93mSKIP FIXING BUY 1000\033[00m")
                    prev_p_1000 = order['price']
            else:
                print("")
                print("\033[93mBUY XXX WARN! ODD PRICE/QTY DETECTED!\033[00m")
                print("{:>15.0f}{:>15.0f}".format(order['price'], order['orderQty']))
        
        if verbose == True:
        	if first_p_1000 > 0:
        		print()
        		print("BUY 1000 FIRST")
        		print("{:>15.0f}".format(first_p_1000))
        		print("BUY 1000 LAST")
        		print("{:>15.0f}".format(prev_p_1000))
        	if first_p_200 > 0:
        		print()
        		print("BUY 200 FIRST")
        		print("{:>15.0f}".format(first_p_200))
        		print("BUY 200 LAST")
        		print("{:>15.0f}".format(prev_p_200))
        	if first_p_100 > 0:
        		print()
        		print("BUY 100 FIRST")
        		print("{:>15.0f}".format(first_p_100))
        		print("BUY 100 LAST")
        		print("{:>15.0f}".format(prev_p_100))
        	
        	print()
        	show_ticker()
        
        sell_orders = get_all_sell_orders(log = False, price_reverse = False)
        
        first_p_100 = 0
        first_p_200 = 0
        first_p_1000 = 0
        
        prev_p_100 = 0
        prev_p_200 = 0
        prev_p_1000 = 0
        
        for order in sell_orders:
            # sell order at 34900 must have qty 3400
            # sell order at 35000 can have qty 3400 or 3500
            if order['price'] // 1000 * 100 == order['orderQty'] or (order['price'] // 1000) * 100 - 100 == order['orderQty']:
                if prev_p_100 == 0:
                    first_p_100 = order['price']
                    prev_p_100 = first_p_100
                else:
                    if order['price'] == prev_p_100 + 100:
                        pass
                    else:
                        print("")
                        print("\033[93mSELL 100 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_100))
                        if fix_mode == True:
                            print("FIXING SELL 100...\033[00m")
                            if order['price'] == prev_p_100:
                                # tripple beeps
                                #print("\a\a\a")
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_100 + 100 and order['price'] % 100 == 0:
                                for price in range(int(prev_p_100) + 100, int(order['price']) - 1, 100):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    sell(price, price // 1000 * 100)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING SELL 100... DONE!\033[00m")
                        else:
                            print("\033[93mSKIP FIXING SELL 100\033[00m")
                    prev_p_100 = order['price']
            elif order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 200 - 200 == order['orderQty']:
                if prev_p_200 == 0:
                    first_p_200 = order['price']
                    prev_p_200 = first_p_200
                else:
                    if order['price'] == prev_p_200 + 100:
                        pass
                    else:
                        print("")
                        print("\033[93mSELL 200 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_200))
                        if fix_mode == True:
                            print("FIXING SELL 200...\033[00m")
                            if order['price'] == prev_p_200:
                                # tripple beeps
                                #print("\a\a\a")
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_200 + 100 and order['price'] % 100 == 0:
                                for price in range(int(prev_p_200) + 100, int(order['price']) - 1, 100):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    sell(price, price // 1000 * 200)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING SELL 200... DONE!\033[00m")
                        else:
                            print("\033[93mSKIP FIXING SELL 200\033[00m")
                    prev_p_200 = order['price']
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0: 
                if prev_p_1000 == 0:
                    first_p_1000 = order['price']
                    prev_p_1000 = first_p_1000
                else:
                    if order['price'] == prev_p_1000 + 1000:
                        pass
                    else:
                        print("")
                        print("\033[93mSELL 1000 WARN! CURRENT vs PREVIOUS!")
                        print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_1000))
                        if fix_mode == True:
                            print("FIXING SELL 1000...\033[00m")
                            if order['price'] == prev_p_1000:
                                # tripple beeps
                                #print("\a\a\a")
                                result = cancel_order(order)
                                time.sleep(5)
                                if type(result) == dict:
                                    print("\033[91mCancel FAILED!\033[00m")
                                else:
                                    print("\033[93mCancel OKAY!\033[00m")
                            elif order['price'] > prev_p_1000 + 1000 and order['price'] % 1000 == 0 and order['price'] < prev_p_1000 + 10000:
                                for price in range(int(prev_p_1000) + 1000, int(order['price']) - 1, 1000):
                                    # tripple beeps
                                    #print("\a\a\a")
                                    sell(price, price)
                                    time.sleep(5)
                            else:
                                print("\033[91mUnexpected price/qty!!!\033[00m")
                                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                            print("\033[93mFIXING SELL 1000... DONE!\033[00m")
                        else:
                            print("\033[93mSKIP FIXING SELL 1000\033[00m")
                    prev_p_1000 = order['price']
            else:
                print("")
                print("\033[93mSELL XXX WARN! ODD PRICE/QTY DETECTED!\033[00m")
                print("{:>15.0f}{:>15.0f}".format(order['price'], order['orderQty']))
        
        if verbose == True:
        	if first_p_200 > 0:
        		print()
        		print("SELL 200 FIRST")
        		print("{:>15.0f}".format(first_p_200))
        		print("SELL 200 LAST")
        		print("{:>15.0f}".format(prev_p_200))
        	if first_p_100 > 0:
        		print()
        		print("SELL 100 FIRST")
        		print("{:>15.0f}".format(first_p_100))
        		print("SELL 100 LAST")
        		print("{:>15.0f}".format(prev_p_100))
        	if first_p_1000 > 0:
        		print()
        		print("SELL 1000 FIRST")
        		print("{:>15.0f}".format(first_p_1000))
        		print("1000 LAST")
        		print("{:>15.0f}".format(prev_p_1000))

    except:
        print("\033[91mCHECK AND FIX: Uncaught Exception!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


stats_and_range_laps_in_sec = 1000000000
while True:
    try:
        if stats_and_range_laps_in_sec > stats_interval:
            stats_and_range_laps_in_sec = 0
            now = pytz.utc.localize(datetime.datetime.utcnow())
            print("")
            if fix_mode == True:
                print("\033[93m{:<30s}{:>30s} (UTC)\033[00m".format("[CHECK AND RANGE AND FIX]", now.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                print("\033[93m{:<30s}{:>30s} (UTC)\033[00m".format("[CHECK AND RANGE ONLY (NO FIX)]", now.strftime("%d/%m/%Y %H:%M:%S")))
            print("", end ="", flush=True)
            fix_gap()
            fix_range()
        else:
            fix_gap()
    except:
        print("\033[91mCHECK AND FIX: Uncaught Exception!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

    for i in range(1, polling_interval):
        stats_and_range_laps_in_sec = stats_and_range_laps_in_sec + 1
        time.sleep(1)
        print(".", end =" ", flush=True)
    print(" ", end =" ", flush=True)
