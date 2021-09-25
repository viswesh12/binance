from configt import Connect
from ordert import Order
import numpy as np
from scipy import stats
import time
import datetime as dt
class main():
    def __init__(self):
        self.client=Connect().make_connection()
        print("logged in")
        self.start_trade()
    def get_all(self):
        coins = self.client.futures_exchange_info()
        all_coin = []
        for pair in coins['symbols']:
            all_coin += [pair['symbol']]
        return all_coin

    def start_trade(self):
        self.trading=Order()
        print("starting new trade...")
        coin= self.get_all()
        coin+=[]
        for symbol in list(coin):
            
              try:
                  fund=self.client.futures_funding_rate(symbol=symbol)
                  klines=self.client.futures_historical_klines(symbol,self.client.KLINE_INTERVAL_8HOUR,"1 day ago UTC+5.30")
              except:
                  print('Timeout')
                  time.sleep(120)
                  print('Trying to reconnect')
              fund=self.client.futures_funding_rate(symbol=symbol)
              klines=self.client.futures_historical_klines(symbol,self.client.KLINE_INTERVAL_8HOUR,"1 day ago UTC+5.30")
              fundrate=[]
              for i in fund:
                  fundrate.append(float(i['fundingRate']))
              price=[]
              for i in klines:
                  price.append(float(i[4]))
              zscore=stats.zscore(np.asarray(fundrate))[-1]
              self.zscore=zscore
              self.symbol=symbol
              if zscore > 2:
                   self.order_to_track=self.trading.sell(symbol,price[len(price)-1])
                   print(self.order_to_track)
                   self.track_trade()

              elif zscore < -2:
                   self.order_to_track=self.trading.buy(symbol,price[len(price)-1])
                   print(self.order_to_track)
                   self.track_trade()
              else:
                  time.sleep(2)
                  print('Zscore:',symbol,zscore)
                  print('No entry,waiting...')

    def track_trade(self):
        if self.zscore<0 and self.order_to_track['side']=='SELL':
            self.end_trade()
            time.sleep(1.5)
            try:
                self.start_trade()
            except:
                print("Can't make new trade.Wait...")
                time.sleep(120)
                self.start_trade()
        elif self.zscore>0 and self.order_to_track['side']=='BUY':
            self.end_trade()
            time.sleep(1.5)
            try:
                self.start_trade()
            except:
                print("Can't make new trade.Wait..")
                time.sleep(120)
                self.start_trade()
        """"   
        def percent_change(original,new):
            original=float(original)
            new=float(new)
            return (new-original)/original*100
        while True:
            time.sleep(1.5)
            try:
                self.last_price=self.client.futures_get_order(symbol=self.symbol)[-1]['price']
            except:
                print("Timeout.Wait...")
                time.sleep(120)
                print('Trying to connect..')
                self.last_price=self.client.futures_get_order(symbol=self.symbol)[-1]['price']

            change=percent_change(self.order_to_track['fills'][0]['price'],self.last_price)
             
            if(self.order_to_track['side']=='SELL'):
                change=change*-1
            if change >= 10  or change<= 5:
                print(change)
                self.end_trade()
                print("Current trade with profit:",change,'%')
                time.sleep(1.5)
                try:
                   self.start_trade()
                except:
                    print("Can't make new trade.WAIT..")
                    time.sleep(120)
                    self.start_trade()
            else:
                print("Current trade with profit:",format(change,'2f'),'%')"""



    def end_trade(self):
            self.trading.close_order(self.symbol,self.order_to_track["executedQty"],self.order_to_track['side'])
            print('position closed')
            print(self.order_to_track)

main()


