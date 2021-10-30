#!/bin/bash

a="/bin/bash -lc /home/dyin/bitmex_trading_bot/check.sh"
b="/bin/bash /home/dyin/bitmex_trading_bot/check.sh"
c="python3 /home/dyin/bitmex_trading_bot/check.py"

start() {
	res=`ps aux | grep "$a\|$b\|$c"` | grep -v grep
	if [ -z "$res" ]
	then
    	echo "check.py starting..."
	    /home/dyin/bitmex_trading_bot/check.py -f
    	echo "check.py stopped"
	else
    	echo "check.py alreay running. skipping..."
	fi 
}

stop() {
	res=`ps aux | grep "$a\|$b\|$c" | grep -v grep | awk '{print $2}'`
	if [ ! -z "$res" ]
	then
		echo "stopping check.py..." 
		sudo kill $res
	fi

	sleep 1

	res=`ps aux | grep "$a\|$b\|$c" | grep -v grep | awk '{print $2}'`
	if [ ! -z "$res" ]
	then
		echo "force stopping check.py..." 
		sudo kill -9 $res
	fi

	sleep 1

    res=`ps aux | grep "$a\|$b\|$c" | grep -v grep`
    if [ -z "$res" ]
    then
		echo "check.py stopped"
	else 
		echo "failed to stop check.py"
    fi 
}

status() {
    res=`ps aux | grep "$c" | grep -v grep`
    if [ -z "$res" ]
    then
        echo "check.py not running"
    else
        echo "check.py is running"
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
