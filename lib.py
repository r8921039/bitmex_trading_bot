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

def cancel_order(side, price):
    try: 
        orders = client.Order.Order_getOrders(symbol=symbol, reverse=True, filter=json.dumps({'open' : 'true', 'side' : side, 'price' : price})).result()
        #print(orders[0][0]['orderID'])
        #print(orders[0][0]['side'])
        #print(orders[0][0]['price'])
        #print(orders[0][0]['orderQty']) # don't use this one for seraching, as
        #print(orders[0][0]['ordStatus']) # New, Canceled
        for order in orders[0]:
            print(orders[0][0]['orderID'])
            print(orders[0][0]['side'])
            print(orders[0][0]['price'])
            print(orders[0][0]['orderQty']) # don't use this one for seraching, as
            print(orders[0][0]['ordStatus']) # New, Canceled
            result = client.Order.Order_cancel(orderID=order['orderID']).result()
            print(result)
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
            if side == "Sell":
                print("\033[35m", end="")
            else:
                print("\033[32m", end="")
            print("FILLED ORDER:")
            print("{:>15s}{:>15s}{:>15s}{:>30s}{:>15s}\033[00m".format("SIDE", "PRICE", "QTY", "TIME", "STATUS"))
            for trade in trades:
                print("\033[96m{:>15s}{:>15.2f}{:>15.0f}{:>30s}{:>15s}\033[00m".format(trade['side'], trade['price'], trade['orderQty'], trade['timestamp'].strftime("%d/%m/%Y %H:%M:%S"), trade['ordStatus']))
                results.append(trade)
        return results
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        return TypeError

#
#
#

