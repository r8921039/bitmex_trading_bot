#!/usr/bin/env python3

import argparse
from lib import *

now = pytz.utc.localize(datetime.datetime.utcnow())

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("CHECK ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))

show_ticker()

#t = get_ticker()
#print(t)
#print("")

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
                #print("100 ok:" + str(order['price']))
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m100 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_100))
                print("FIXING BUY 100...\033[00m")
                if order['price'] == prev_p_100:
                    result = cancel_order(order)
                    time.sleep(5)
                    if type(result) == dict:
                        print("\033[91mCancel FAILED!\033[00m")
                    else:
                        print("\033[93mCancel OKAY!\033[00m")
                elif order['price'] > prev_p_100 + 100 and order['price'] % 100 == 0:
                    for price in range(int(prev_p_100) + 100, int(order['price']) - 1, 100):
                        buy(price, price // 1000 * 100)
                        time.sleep(5)
                else:
                    print("\033[91mUnexpected price/qty!!!\033[00m")
                    print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                print("\033[93mFIXING BUY 100... DONE!\033[00m")
            prev_p_100 = order['price']
    elif order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 100 + 200 == order['orderQty']:
        if prev_p_200 == 0:
            first_p_200 = order['price']
            prev_p_200 = first_p_200
        else:
            if order['price'] == prev_p_200 + 100:
                #print("200 ok:" + str(order['price']))
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m200 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_200))
                print("FIXING BUY 200...\033[00m")
                if order['price'] == prev_p_200:
                    result = cancel_order(order)
                    time.sleep(5)
                    if type(result) == dict:
                        print("\033[91mCancel FAILED!\033[00m")
                    else:
                        print("\033[93mCancel OKAY!\033[00m")
                elif order['price'] > prev_p_200 + 100 and order['price'] % 100 == 0:
                    for price in range(int(prev_p_200) + 100, int(order['price']) - 1, 100):
                        buy(price, price // 1000 * 200)
                        time.sleep(5)
                else:
                    print("\033[91mUnexpected price/qty!!!\033[00m")
                    print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                print("\033[93mFIXING BUY 200... DONE!\033[00m")
            prev_p_200 = order['price']
    elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0: 
        if prev_p_1000 == 0:
            first_p_1000 = order['price']
            prev_p_1000 = first_p_1000
        else:
            if order['price'] == prev_p_1000 + 1000:
                #print("1000 ok:" + str(order['price']))
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m1000 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], prev_p_1000))
            prev_p_1000 = order['price']
    else:
        print("")
        print("\033[93mWARN! ODD PRICE/QTY DETECTED!\033[00m")
        print("{:>15.0f}{:>15.0f}".format(order['price'], order['orderQty']))

print()
print("1000 FIRST")
print("{:>15.0f}".format(first_p_1000))
print("1000 LAST")
print("{:>15.0f}".format(prev_p_1000))
print()
print("100 FIRST")
print("{:>15.0f}".format(first_p_100))
print("100 LAST")
print("{:>15.0f}".format(prev_p_100))
print()
print("200 FIRST")
print("{:>15.0f}".format(first_p_200))
print("200 LAST")
print("{:>15.0f}".format(prev_p_200))

#quit()

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
                #print("100 ok:" + str(order['price'])) 
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m100 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_100))
                print("FIXING SELL 100...\033[00m")
                if order['price'] == prev_p_100:
                    result = cancel_order(order)
                    time.sleep(5)
                    if type(result) == dict:
                        print("\033[91mCancel FAILED!\033[00m")
                    else:
                        print("\033[93mCancel OKAY!\033[00m")
                elif order['price'] > prev_p_100 + 100 and order['price'] % 100 == 0:
                    for price in range(int(prev_p_100) + 100, int(order['price']) - 1, 100):
                        sell(price, price // 1000 * 100)
                        time.sleep(5)
                else:
                    print("\033[91mUnexpected price/qty!!!\033[00m")
                    print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                print("\033[93mFIXING SELL 100... DONE!\033[00m")
            prev_p_100 = order['price']
    elif order['price'] // 1000 * 200 == order['orderQty'] or (order['price'] // 1000) * 100 - 200 == order['orderQty']:
        if prev_p_200 == 0:
            first_p_200 = order['price']
            prev_p_200 = first_p_200
        else:
            if order['price'] == prev_p_200 + 100:
                #print("200 ok:" + str(order['price']))
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m200 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}".format(order['price'], prev_p_200))
                print("FIXING SELL 200...\033[00m")
                if order['price'] == prev_p_200:
                    result = cancel_order(order)
                    time.sleep(5)
                    if type(result) == dict:
                        print("\033[91mCancel FAILED!\033[00m")
                    else:
                        print("\033[93mCancel OKAY!\033[00m")
                elif order['price'] > prev_p_200 + 100 and order['price'] % 100 == 0:
                    for price in range(int(prev_p_200) + 100, int(order['price']) - 1, 100):
                        sell(price, price // 1000 * 200)
                        time.sleep(5)
                else:
                    print("\033[91mUnexpected price/qty!!!\033[00m")
                    print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], order['orderQty']))
                print("\033[93mFIXING SELL 200... DONE!\033[00m")
            prev_p_200 = order['price']
    elif order['price'] == order['orderQty'] and order['orderQty'] % 1000 == 0: 
        if prev_p_1000 == 0:
            first_p_1000 = order['price']
            prev_p_1000 = first_p_1000
        else:
            if order['price'] == prev_p_1000 + 1000:
                #print("1000 ok:" + str(order['price']))
                print(" ", end =" ", flush=True)
            else:
                print("")
                print("\033[93m1000 WARN! CURRENT vs PREVIOUS!")
                print("{:>15.0f}{:>15.0f}\033[00m".format(order['price'], prev_p_1000))
            prev_p_1000 = order['price']
    else:
        print("")
        print("\033[93mWARN! ODD PRICE/QTY DETECTED!\033[00m")
        print("{:>15.0f}{:>15.0f}".format(order['price'], order['orderQty']))

print()
print("200 FIRST")
print("{:>15.0f}".format(first_p_200))
print("200 LAST")
print("{:>15.0f}".format(prev_p_200))
print()
print("100 FIRST")
print("{:>15.0f}".format(first_p_100))
print("100 LAST")
print("{:>15.0f}".format(prev_p_100))
print()
print("1000 FIRST")
print("{:>15.0f}".format(first_p_1000))
print("1000 LAST")
print("{:>15.0f}".format(prev_p_1000))


