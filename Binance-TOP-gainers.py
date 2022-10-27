# %%
# %%
from binance.exceptions import BinanceAPIException
import os
# from binance import AsyncClient
from binance.client import Client
import json
import requests
import pandas as pd



# %%

# Binance
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

# Telegram
telegramToken = os.environ.get('telegramToken') 
telegram_chat_id = os.environ.get('telegram_chat_id')

# %%


# %%
# %%
def sendTelegramMessage(emoji, msg):
    if not emoji:
        lmsg = msg
    else:
        lmsg = emoji+" "+msg
    url = f"https://api.telegram.org/bot{telegramToken}/sendMessage?chat_id={telegram_chat_id}&text={lmsg}"
    requests.get(url).json() # this sends the message

def sendTelegramAlert(emoji, date, coin, timeframe, strategy, ordertype, value, amount):
    lmsg = emoji + " " + str(date) + " - " + coin + " - " + strategy + " - " + timeframe + " - " + ordertype + " - " + "Value: " + str(value) + " - " + "Amount: " + str(amount)
    url = f"https://api.telegram.org/bot{telegramToken}/sendMessage?chat_id={telegram_chat_id}&text={lmsg}"
    requests.get(url).json() # this sends the message





# %%
# %%
# Binance Client
clientTest = Client(api_key, api_secret)

# %%


# %%
tickers = clientTest.get_ticker()
dfTickers = pd.DataFrame(tickers)



# %%
dfStables = dfTickers[dfTickers.symbol.str.endswith("BUSD")]
dfStables.volume = dfStables.volume.astype(float)
dfStables.quoteVolume = dfStables.quoteVolume.astype(float)
dfStables.priceChangePercent = dfStables.priceChangePercent.astype(float)
dfStables.askPrice = dfStables.askPrice.astype(float)
dfStables

# %%

#dfVol = dfStables
dfVol = dfStables[(dfStables.quoteVolume > 2000000) & 
                    (dfStables.askPrice > 0)]



# %%
#dfVol.priceChangePercent.sort_values(ascending = True, inplace = True) 
dfOrderPricePerc = dfVol.sort_values('priceChangePercent', axis = 0, ascending = False,
                 na_position ='last')

dfOrderPricePerc.head(10)

# %%
dfOrderVol = dfVol.sort_values('quoteVolume', axis = 0, ascending = False, na_position ='last')

dfOrderVol.head(10)


