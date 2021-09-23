from configt import Connect
from binance import Client
import math
import time
from decimal import Decimal as D, ROUND_DOWN, ROUND_UP
import decimal
class Order:
    def __init__(self):
        self.client=Connect.make_connection(Client)
        max_amount = self.client.futures_account_balance()
        self.max_amount = format(float(max_amount[1]['balance']) * 60/ 100, ".6f")
        self.qty = float(self.max_amount)


    def convert_volume(self,coin, quantity, last_price):
        """Converts the volume given in QUANTITY from USDT to the each coin's volume"""
        info = self.client.get_symbol_info(symbol=coin)
        price_filter = float(info['filters'][0]['tickSize'])
        ticker = self.client.get_symbol_ticker(symbol=coin)
        price = float(ticker['price'])
        price = D.from_float(price).quantize(D(str(price_filter)))
        minimum = float(info['filters'][2]['minQty'])  # 'minQty'
        quant = D.from_float(quantity).quantize(D(str(minimum)))
        al = info['filters'][2]['stepSize']
        decimal = 0
        is_dec = False
        for c in al:
            if is_dec is True:
                decimal += 1
            if c == '1':
                break
            if c == '.':
                is_dec = True
        qround = round(quant / price, decimal)

        return qround



    def sell(self,symbol,last_price):
        volume=self.convert_volume(symbol,self.qty,last_price)
        order=self.client.create_test_order(
            symbol=symbol,
            side=self.client.SIDE_SELL,
            type=self.client.ORDER_TYPE_MARKET,
            quantity=volume
             )
        return order
    def buy(self,symbol,last_price):
        volume = self.convert_volume(symbol,self.qty, last_price)
        order=self.client.create_test_order(
            symbol=symbol,
            side=self.client.SIDE_BUY,
            type=self.client.ORDER_TYPE_MARKET,
            quantity=volume
             )
        return order

    def close_order(self,symbol,qty,side):
        if side=='BUY':
            order=self.client.create_test_order(
                symbol=symbol,
                side=self.client.SIDE_SELL,
                type=self.client.ORDER_TYPE_MARKET,
                quantity=qty
            )
        elif side=='SELL':
            order=self.client.create_test_order(
                symbol=symbol,
                side=self.client.SIDE_BUY,
                type=self.client.ORDER_TYPE_MARKET,
                quantity=qty
            )
        return order