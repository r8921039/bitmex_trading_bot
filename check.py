#!/usr/bin/env python3

import argparse
from lib import *

now = pytz.utc.localize(datetime.datetime.utcnow())

check_range = 10000

os.system('clear')
print("\033[93m{:>15s}{:>30s} (UTC)\033[00m".format("CONVERT ORDERS", now.strftime("%d/%m/%Y %H:%M:%S")))

orders = get_all_sell_orders()

print("")
show_pos()
print("")

orders = get_all_buy_orders()




