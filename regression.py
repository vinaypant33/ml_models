import pandas as pd
import yfinance as yf
from time import sleep


Ticker = yf.Ticker('AAPL')
df   = Ticker.history(period = "1mo")



sleep(4)


print(df.head(10))