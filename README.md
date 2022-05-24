### INTRO
This project mainly contains a market maker bot (bot.py) that when a buy order executed, it will automatically place a sell order, and vice versa.  Another piece of the market maker bot (check.py) is to fix and adjust the buy order wall and sell order wall.  

Close to the current ticker price, each buy/sell order is layered 100 USD apart with size 0.2 BTC. For exmaple, if the current ticker price is 30000, the buy orders would be 29900, 29800, 29700, etc, and sell orders would be 30100, 30200, 30300, etc, all 0.2 BTC (taking floor to the smallest unit of 100 USD). Beyond the 0.2 BTC buy and sell walls, 1 BTC buy and sell walls are layered further out in a similar fashion. 

### HOWTO
1. pip3 install bitmex
2. place layered buy orders all the way down and layered sell orders all the way up 
3. run bot.py
4. (optional) run check.py 

### LICENSE
MIT


