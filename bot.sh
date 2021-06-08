#!/bin/bash

res=`ps aux | grep bot.py | grep -v grep`
echo $res

if [ -z "$res" ]
then
    echo "bot.py starting"
    /home/dyin/bitmex_trading_bot/bot.py > /home/dyin/bitmex_trading_bot/out.log
    echo "bot.py stopped"
else
    echo "bot.py alreay running. abort!"
fi 


