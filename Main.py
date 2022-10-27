# %%
from backtesting.test import SMA
import os
from binance.client import Client
import pandas as pd
import btalib
import numpy as np

# %%
# Binance API
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

# %%
client = Client(api_key, api_secret)

# %%
# from optparse import Values


def EMA(values, n):
    """
    Return exp moving average of `values`, at
    each step taking into account `n` previous values.
    """
    
    # return btalib.ema(Values, period=n)
    
    # return pd.Series(values).rolling(n).mean()
    return pd.Series(values).ewm(span=n, adjust=False).mean()


# %%
def SMA(values, n):
    """
    Return exp moving average of `values`, at
    each step taking into account `n` previous values.
    """
        
    return pd.Series(values).rolling(n).mean()
    

# %%
def bollinger_bands(df, length=20, m=2):
    # takes dataframe on input
    # n = smoothing length
    # m = number of standard deviations away from MA
    
    #typical price
    TP = (df['High'] + df['Low'] + df['Close']) / 3
    # but we will use Adj close instead for now, depends
    
    data = TP
    #data = df['Adj Close']
    
    # takes one column from dataframe
    B_MA = pd.Series((data.rolling(length, min_periods=length).mean()), name='B_MA')
    sigma = data.rolling(length, min_periods=length).std() 
    
    BU = pd.Series((B_MA + m * sigma), name='BU')
    BL = pd.Series((B_MA - m * sigma), name='BL')
    
    df = df.join(B_MA)
    df = df.join(BU)
    df = df.join(BL)
    
    return df

# %%
from backtesting import Strategy
from backtesting.lib import crossover


# we will use four moving averages in total: 
# two moving averages whose relationship determines a general trend (we only trade long when the shorter MA is above the longer one, and vice versa), 
# and two moving averages whose cross-over with daily close prices determine the signal to enter or exit the position.
class Sma4Cross(Strategy):
    n1 = 36
    print("n1=",str(n1)) 
    n2 = 88
    print("n2=",str(n2))
    # n_enter = 20
    # n_exit = 10
    
    def init(self):
        self.sma1 = self.I(EMA, self.data.Close, self.n1)
        self.sma2 = self.I(EMA, self.data.Close, self.n2)
        
        # self.sma1 = self.I(SMA, self.data.Close, self.n1)
        # self.sma2 = self.I(SMA, self.data.Close, self.n2)
        
    def next(self):
        
        if not self.position:
            
            # On upwards trend, if price closes above
            # "entry" MA, go long
            
            # Here, even though the operands are arrays, this
            # works by implicitly comparing the two last values
            if self.sma1 > self.sma2:
                # if crossover(self.data.Close, self.sma_enter):
                self.buy()
                    
            # On downwards trend, if price closes below
            # "entry" MA, go short
            
            # else:
            #     if crossover(self.sma_enter, self.data.Close):
            #         self.sell()
        
        # But if we already hold a position and the price
        # closes back below (above) "exit" MA, close the position
        
        else:
            # if (self.position.is_long and
            #     crossover(self.sma_exit, self.data.Close)
            #     or
            #     self.position.is_short and
            #     crossover(self.data.Close, self.sma_exit)):
                
            self.position.close()

# %%
import datetime as dt

def getdata(Symbol):
    print("getdata")
    frame = pd.DataFrame(client.get_historical_klines(Symbol,
                                                      client.KLINE_INTERVAL_1HOUR,
                                                    #   '3 years ago UTC')
                                                      '1 Feb, 2019 UTC',
                                                      # '26 Dec, 2021 UTC'
                                                      # '90 day ago UTC'
                                                      # '4000 hour ago UTC' # 4hour
                                                      ))
    
    frame = frame.iloc[:,:6] # use the first 5 columns
    frame.columns = ['Time','Open','High','Low','Close','Volume'] #rename columns
    frame[['Open','High','Low','Close','Volume']] = frame[['Open','High','Low','Close','Volume']].astype(float) #cast to float
    # frame.Time = pd.to_datetime(frame.Time, unit='ms') #make human readable timestamp
    frame.index = [dt.datetime.fromtimestamp(x/1000.0) for x in frame.Time]
    return frame

# %%

from backtesting import Backtest

# GOOG = Open	High	Low	Close	Volume
coin = "ETHUSDT"
print("coin= "+coin)
df = getdata(coin)
df = df.drop(['Time'], axis=1)
# df
# df = bollinger_bands(df)

print("backtest")
bt = Backtest(df, Sma4Cross, cash=100000, commission=0)
stats = bt.run()
print(stats)
# bt.plot() 


# quit()
# %%

# bt.plot() 

# %%
print("heatmap")
stats, heatmap = bt.optimize(
    n1=range(8, 50, 2),
    n2=range(2, 100, 2),
    # n_enter=range(15, 35, 5),
    # n_exit=range(10, 25, 5),
    # constraint=lambda p: p.n_exit < p.n_enter < p.n1 < p.n2,
    maximize='Equity Final [$]',
    # max_tries=200,
    # random_state=0,
    return_heatmap=True)

# %%
heatmap.dropna(inplace=True)
heatmap.sort_values()
print(heatmap)

# %%
hm = heatmap.groupby(['n1', 'n2']).mean().unstack()
hm

# %%


import seaborn as sns
import matplotlib.pylab as plt


sns.heatmap(hm[::-1], cmap='viridis',vmin=100000)
plt.show()
