#!/usr/bin/env python3

import bitmex

import datetime
from decimal import Decimal
import json
import pytz
import time
import traceback
import os
import sys
import warnings

from swagger_spec_validator.common import SwaggerValidationWarning
#warnings.simplefilter("ignore", SwaggerValidationWarning)
warnings.simplefilter("ignore", Warning)

with open('.apikey') as json_file:
    api_config = json.load(json_file)
    client = bitmex.bitmex(test=False, api_key=api_config['api_key'], api_secret=api_config['api_secret'])

symbol = 'XBTUSD'
verbose = False # debug

#
# quote
# 

def get_ticker(): 
    ticker()
def show_ticker():
    ticker(True)
def ticker(log = False):
    try: 
        result = client.Quote.Quote_get(symbol=symbol, reverse=True, count=1).result()[0][0]
        ticker = Decimal((result['bidPrice'] + result['askPrice']) / 2)
        timestamp = result['timestamp'].strftime("%d/%m/%Y %H:%M:%S")
        if log :
            print("\033[36mTICKER:\033[00m")
            print("\033[96m{:>15.0f}{:>30s} (UTC)\033[00m".format(ticker, timestamp))
        return ticker 
    except: 
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError
        #sys.exit()

#
# position
#

def show_pos():
    try: 
        result = client.Position.Position_get(filter=json.dumps({'symbol': symbol})).result()[0][0]
        qty = result['currentQty'] 
        value = result['currentQty'] / Decimal(result['lastPrice'])
        cost_base = Decimal(result['breakEvenPrice'])
        curr_price = Decimal(result['lastPrice'])
        liq_price = Decimal(result['liquidationPrice'])
        liq_pct = Decimal(result['deleveragePercentile'])
        u_pnl = Decimal(result['unrealisedPnl']) / 100000000
        r_pnl = (Decimal(result['realisedPnl']) + Decimal(result['rebalancedPnl'])) / 100000000

        #if verbose :
        if True :
            print("\033[36mOPEN POSITIONS:\033[00m")
            print("\033[36m{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("QTY (USD)", "VALUE (BTC)", "COST BASE", "CURR PRICE", "LIQ PRICE", "LIQ %", "UNREALISED", "REALIZED"))
            print("\033[96m{:>15.0f}{:>15.2f}{:>15.0f}{:>15.0f}{:>15.0f}{:>15.2f}{:>15.2f}{:>15.2f}\033[00m".format(qty, value, cost_base, curr_price, liq_price, liq_pct, u_pnl, r_pnl))
        return None
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError
        #sys.exit()

#
# order
#

def buy(price, orderQty = None): 
    if orderQty == None:
        orderQty = int(price)
    orderQty = abs(orderQty)
    return place_order(price, orderQty)
def sell(price, orderQty = None):
    if orderQty == None:
        orderQty = int(price)
    orderQty = 0 - abs(orderQty)
    return place_order(price, orderQty)
def place_order(price, orderQty):
    try:
        if orderQty == None:
            orderQty = int(price)
        result = client.Order.Order_new(symbol=symbol, ordType="Limit", orderQty=orderQty, price=price).result()[0]
        if result['side'] == 'Sell': 
            print("\033[35m", end="")
        else:
            print("\033[32m", end="")
        print("NEW ORDER:")
        print("{:>15s}{:>15s}{:>15s}{:>30s}{:>45s}\033[00m".format("SIDE", "PRICE", "QTY", "TIME", "ORDER ID"))
        print("\033[96m{:>15s}{:>15.2f}{:>15.0f}{:>30s}{:>45s}\033[00m".format(result['side'], result['price'], result['orderQty'], result['timestamp'].strftime("%d/%m/%Y %H:%M:%S"), result['orderID']))
        return result
    except: 
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

def get_all_buy_orders():
    get_orders("Buy")
def get_all_sell_orders():
    get_orders("Sell")
def get_orders(side, price = None): # price = None: for all orders 
    try: 
        if price == None: 
            orders = client.Order.Order_getOrders(symbol=symbol, reverse=False, count=200, columns='side,price,orderQty,timestamp,orderID', filter=json.dumps({'open' : 'true', 'side' : side})).result()[0]
            if side == "Buy":
                orders = sorted(orders, key = lambda i: i['price'], reverse=True)
            else:
                orders = sorted(orders, key = lambda i: i['price'], reverse=True)
        else: 
            orders = client.Order.Order_getOrders(symbol=symbol, reverse=False, filter=json.dumps({'open' : 'true', 'side' : side, 'price' : price})).result()[0]

        if len(orders) > 0:
            if side == 'Sell':
                print("\033[35m", end="")
            else:
                print("\033[32m", end="")
            print("FOUND ORDERS:")
            print("{:>15s}{:>15s}{:>15s}{:>30s}{:>45s}\033[00m".format("SIDE", "PRICE", "QTY", "TIME", "ORDER ID"))
            for order in orders:
                print("\033[96m{:>15s}{:>15.2f}{:>15.0f}{:>30s}{:>45s}\033[00m".format(order['side'], order['price'], order['orderQty'], order['timestamp'].strftime("%d/%m/%Y %H:%M:%S"), order['orderID']))
        return orders
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

def cancel_order(order):
    try: 
        if order['side'] == 'Sell':
            print("\033[35m", end="")
        else:
            print("\033[32m", end="")
        print("CANCEL ORDER:")
        print("{:>15s}{:>15s}{:>15s}{:>30s}{:>45s}\033[00m".format("SIDE", "PRICE", "QTY", "TIME", "ORDER ID"))
        result = client.Order.Order_cancel(orderID=order['orderID']).result()[0][0]
        print("\033[96m{:>15s}{:>15.2f}{:>15.0f}{:>30s}{:>45s}\033[00m".format(result['side'], result['price'], result['orderQty'], result['timestamp'].strftime("%d/%m/%Y %H:%M:%S"), result['orderID']))
        return result
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

def cancel_orders(orders):
    try: 
        if len(orders) > 0:
            for order in orders:
                cancel_order(order)
        return None
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

def cancel_all_orders(): 
    try:
        result = client.Order.Order_cancelAll().result()
        print(result)
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

#
# trade history
#
def get_trades(side, start_time, end_time = None):
    try:
        results = []
        trades = client.Execution.Execution_getTradeHistory(symbol=symbol, reverse=False, count = 1, startTime = start_time, endTime = end_time, filter=json.dumps({'ordStatus' : 'Filled', 'side' : side})).result()[0] # without entries of PartiallyFilled 
        if len(trades) > 0: 
            print("")
            if side == "Sell":
                print("\033[35m", end="")
            else:
                print("\033[32m", end="")
            print("FILLED ORDER:")
            print("{:>15s}{:>15s}{:>15s}{:>30s}{:>45s}\033[00m".format("SIDE", "PRICE", "QTY", "TIMESTAMP", "EXEC ID"))
            for trade in trades:
                print("\033[96m{:>15s}{:>15.2f}{:>15.0f}{:>30s}{:>45s}\033[00m".format(trade['side'], trade['price'], trade['orderQty'], trade['timestamp'].strftime("%d/%m/%Y %H:%M:%S"), trade['execID'])) 
                results.append(trade)
        return results
    except:
        print("")
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError
        #sys.exit()

#
#
#

def create_last_buy_sell():
    try:
        with open('.last_buy_sell', 'r') as last_buy_sell_config:
            print("")
    except:
        with open('.last_buy_sell', 'w') as last_buy_sell_config:
            json_file = {'buy': '', 'sell': ''}
            json.dump(json_file, last_buy_sell_config)
    
    if os.path.getsize('.last_buy_sell') == 0:
        with open('.last_buy_sell', 'w') as last_buy_sell_config:
            json_file = {'buy': '', 'sell': ''}
            json.dump(json_file, last_buy_sell_config)

def read_last_buy_sell(last_buy_time, last_sell_time):
    with open('.last_buy_sell', 'r') as json_file:
        last_buy_sell_config = json.load(json_file)

    if last_buy_sell_config['buy'] != "":
        last_buy_time = datetime.datetime( \
        last_buy_sell_config['buy']['year'], \
        last_buy_sell_config['buy']['month'], \
        last_buy_sell_config['buy']['day'], \
        last_buy_sell_config['buy']['hour'], \
        last_buy_sell_config['buy']['minute'], \
        last_buy_sell_config['buy']['second'], \
        last_buy_sell_config['buy']['microsecond'], \
        tzinfo=datetime.timezone.utc)

    if last_buy_sell_config['sell'] != "":
        last_sell_time = datetime.datetime( \
        last_buy_sell_config['sell']['year'], \
        last_buy_sell_config['sell']['month'], \
        last_buy_sell_config['sell']['day'], \
        last_buy_sell_config['sell']['hour'], \
        last_buy_sell_config['sell']['minute'], \
        last_buy_sell_config['sell']['second'], \
        last_buy_sell_config['sell']['microsecond'], \
        tzinfo=datetime.timezone.utc)

    return last_buy_time, last_sell_time

def write_last_buy_sell(last_buy_time, last_sell_time):
    with open('.last_buy_sell', 'w') as last_buy_sell_config:
        json_file = {'buy': { \
            'year': last_buy_time.year, \
            'month': last_buy_time.month, \
            'day': last_buy_time.day, \
            'hour': last_buy_time.hour, \
            'minute': last_buy_time.minute, \
            'second': last_buy_time.second, \
            'microsecond': last_buy_time.microsecond \
            }, 'sell': { \
            'year': last_sell_time.year, \
            'month': last_sell_time.month, \
            'day': last_sell_time.day, \
            'hour': last_sell_time.hour, \
            'minute': last_sell_time.minute, \
            'second': last_sell_time.second, \
            'microsecond': last_sell_time.microsecond \
        }}
        json.dump(json_file, last_buy_sell_config)
