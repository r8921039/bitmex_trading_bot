#!/bin/bash

a="/bin/bash -lc /home/dyin/bitmex_trading_bot/bot.sh"
b="/bin/bash /home/dyin/bitmex_trading_bot/bot.sh"
c="python3 /home/dyin/bitmex_trading_bot/bot.py"

start() {
	res=`ps aux | grep "$a\|$b\|$c"` | grep -v grep
	if [ -z "$res" ]
	then
    	echo "bot.py starting..."
	    /home/dyin/bitmex_trading_bot/bot.py
    	echo "bot.py stopped"
	else
    	echo "bot.py alreay running. skipping..."
		exit 1
	fi 
}

stop() {
	res=`ps aux | grep "$a\|$b\|$c" | grep -v grep | awk '{print $2}'`
	if [ ! -z "$res" ]
	then
		echo "stopping bot..." 
		sudo kill $res
	fi

	sleep 1

	res=`ps aux | grep "$a\|$b\|$c" | grep -v grep | awk '{print $2}'`
	if [ ! -z "$res" ]
	then
		echo "force stopping bot..." 
		sudo kill -9 $res
	fi

	sleep 1

    res=`ps aux | grep "$a\|$b\|$c" | grep -v grep`
    if [ -z "$res" ]
    then
		echo "bot stopped"
	else 
		echo "failed to stop bot"
        exit 1
    fi 
}

status() {
    res=`ps aux | grep "$c" | grep -v grep`
    if [ -z "$res" ]
    then
        echo "bot not running"
    else
        echo "bot is running"
    fi
}

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	restart)
		stop
		start
		;;
	status)
		status
		;;
	*)
		echo $"Usage: $0 {start|stop|restart|status}"
        exit 1
		;;
esac
