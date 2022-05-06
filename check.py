#!/usr/bin/env python3

import argparse
from lib import *

polling_interval = 60 * 1
stats_interval = 60 * 30
verbose = False

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
                liq_price = liq_price + 1000 
            else:
                is_long = False
        print("")
        print("\033[93m{:<30s}{:>30s}\033[00m".format("[LIQ PRICE FOR RANGE BUY LOWER BOUND]", liq_price)),
        print("", flush=True)

        #
        # [RANGE] GET TARGET/CURRENT BUY
        # 

        target_buy_first_200 = int(ticker) // 100 * 100 - 8000
        if is_long and target_buy_first_200 < liq_price:
            print("\033[93mTarget First Buy 200 is less than Liq Price. Use Liq Price as First Buy 200") 
            target_buy_first_200 = liq_price
        target_buy_last_1000 = target_buy_first_200 // 1000 * 1000
        if target_buy_last_1000 >= target_buy_first_200:
            target_buy_last_1000 = target_buy_last_1000 - 1000
        target_buy_first_1000 = target_buy_last_1000 - 8000
        if is_long and target_buy_first_1000 < liq_price:
            print("\033[93mTarget First Buy 1000 is less than Liq Price. Use Liq Price as First Buy 1000") 
            target_buy_first_1000 = liq_pirce
        if target_buy_first_1000 < 1000:
            print("\033[93mFirst RANGE BUY less than 1000!")
            target_buy_first_1000 = 1000

        buy_first_200 = 0
        buy_first_1000 = 0
        buy_last_200 = 0
        buy_last_1000 = 0
        buy_orders = get_all_buy_orders(log = False, price_reverse = False)
        for order in buy_orders:
            if order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 200 + 200 == order['orderQty']:
                if buy_last_200 == 0:
                    buy_first_200 = int(order['price'])
                    buy_last_200 = buy_first_200
                else:
                    buy_last_200 = int(order['price'])
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0:
                if buy_last_1000 == 0:
                    buy_first_1000 = int(order['price'])
                    buy_last_1000 = buy_first_1000
                else:
                    buy_last_1000 = int(order['price'])

        if verbose or target_buy_first_1000 != buy_first_1000 or target_buy_last_1000 != buy_last_1000 or target_buy_first_200 != buy_first_200:
            print("")
            print("\033[93m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("TARGET  FIRST 1000 BUY", "LAST 1000 BUY", "FIRST 200 BUY", "LAST 200 BUY"))
            print("\033[93m{:>20.0f}{:>20.0f}{:>20.0f}{:>20s}\033[00m".format(target_buy_first_1000, target_buy_last_1000, target_buy_first_200, "NA"))
            print("\033[32m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("CURRENT FIRST 1000 BUY", "LAST 1000 BUY", "FIRST 200 BUY", "LAST 200 BUY"))
            print("\033[32m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(buy_first_1000, buy_last_1000, buy_first_200, buy_last_200))
            print("")

        #
        # [RANGE] GET TARGET/CURRENT SELL
        #

        target_sell_last_200 = int(ticker) // 100 * 100 + 8000
        if (not is_long) and liq_price < target_sell_last_200:
            print("\033[93mTarget Last Sell 200 is greater than Liq Price. Use Liq Price as Last Sell 200")
            target_sell_last_200 = liq_price 
        target_sell_first_1000 = target_sell_last_200 // 1000 * 1000 + 1000
        target_sell_last_1000 = target_sell_first_1000 + 8000
        if (not is_long) and liq_price < target_sell_last_1000:
            print("\033[93mTarget Last Sell 1000 is greater than Liq Price. Use Liq Price as Last Sell 1000")
            target_sell_last_1000 = liq_price
        sell_first_200 = 0
        sell_first_1000 = 0
        sell_last_200 = 0
        sell_last_1000 = 0
        sell_orders = get_all_sell_orders(log = False, price_reverse = False)
        for order in sell_orders:
            if order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 200 - 200 == order['orderQty']:
                if sell_last_200 == 0:
                    sell_first_200 = int(order['price'])
                    sell_last_200 = sell_first_200
                else:
                    sell_last_200 = int(order['price'])
            elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0:
                if sell_last_1000 == 0:
                    sell_first_1000 = int(order['price'])
                    sell_last_1000 = sell_first_1000
                else:
                    sell_last_1000 = int(order['price'])

        if verbose or target_sell_last_200 != sell_last_200 or target_sell_first_1000 != sell_first_1000 or target_sell_last_1000 != sell_last_1000:
            print("")
            print("\033[93m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("TARGET  FIRST 200 SELL", "LAST 200 SELL", "FIRST 1000 SELL", "LAST 1000 SELL"))
            print("\033[93m{:>20s}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format("NA", target_sell_last_200, target_sell_first_1000, target_sell_last_1000))
            print("\033[35m{:>20s}{:>20s}{:>20s}{:>20s}\033[00m".format("CURRENT FIRST 200 SELL", "LAST 200 SELL", "FIRST 1000 SELL", "LAST 1000 SELL"))
            print("\033[35m{:>20.0f}{:>20.0f}{:>20.0f}{:>20.0f}\033[00m".format(sell_first_200, sell_last_200, sell_first_1000, sell_last_1000))
            print("")

        #
        # [RANGE CANCEL] BUY/SELL
        #

        # PRICE GOING UP
        if buy_first_200 < target_buy_first_200:
            print("CANCEL BUY 200")
            for p in range(buy_first_200, target_buy_first_200, 100):
                if fix_mode:
                    orders = get_orders("Buy", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] // 1000 * 200 == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if buy_first_1000 < target_buy_first_1000:
            print("CANCEL BUY 1000")
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

        if sell_first_1000 < target_sell_first_1000:
            print("CANCEL SELL 1000")
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
        if target_sell_last_200 < sell_last_200:
            print("CANCEL SELL 200")
            for p in range(target_sell_last_200 + 100, sell_last_200 + 100, 100):
                if fix_mode:
                    orders = get_orders("Sell", p)
                    time.sleep(3)
                    for order in orders:
                        if order['price'] // 1000 * 200 == order['orderQty']:
                            cancel_order(order)
                            time.sleep(3)
                else:
                    print(p)

        if target_sell_last_1000 < sell_last_1000:
            print("CANCEL SELL 1000")
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

        if target_buy_last_1000 < buy_last_1000:
            print("CANCEL BUY 1000")
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
        if sell_last_200 < target_sell_last_200:
            print("ADD   SELL  200")
            for p in range(sell_last_200 + 100, target_sell_last_200 + 100, 100):
                if fix_mode:
                    sell(p, (p // 1000) * 200)
                    time.sleep(3)
                else:
                    print(p)

        if sell_last_1000 < target_sell_last_1000:
            print("ADD    SELL 1000")
            for p in range(sell_last_1000 + 1000, target_sell_last_1000 + 1000, 1000):
                if fix_mode:
                    sell(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)

        if buy_last_1000 < target_buy_last_1000:
            print("ADD    BUY  1000")
            for p in range(buy_last_1000 + 1000, target_buy_last_1000 + 1000, 1000):
                if fix_mode:
                    buy(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)

        # PRICE GOING DOWN
        if target_buy_first_200 < buy_first_200:
            print("ADD    BUY 200")
            for p in range(target_buy_first_200, buy_first_200, 100):
                if fix_mode:
                    buy(p, (p // 1000) * 200)
                    time.sleep(3)
                else:
                    print(p)

        if target_buy_first_1000 < buy_first_1000:
            print("ADD    BUY 1000")
            for p in range(target_buy_first_1000, buy_first_1000, 1000):
                if fix_mode:
                    buy(p, (p // 1000) * 1000)
                    time.sleep(3)
                else:
                    print(p)
        
        if target_sell_first_1000 < sell_first_1000:
            print("ADD    SELL 1000")
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
                print("\033[93m{:<15s}{:>30s} (UTC)\033[00m".format("[CHECK AND RANGE AND FIX]", now.strftime("%d/%m/%Y %H:%M:%S")))
            else:
                print("\033[93m{:<15s}{:>30s} (UTC)\033[00m".format("[CHECK AND RANGE ONLY (NO FIX)]", now.strftime("%d/%m/%Y %H:%M:%S")))
            print("", end =" ", flush=True)
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
