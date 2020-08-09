import bs4 as bs
import os
import pandas as pd 
import pandas_datareader.data as web
import pickle
import requests
import datetime as dt
import yfinance as yf
import sqlite3

conn = sqlite3.connect('stockdatasql.db')
c= conn.cursor()

with open("nifty50tickers.pickle","rb") as f:
	tickers = pickle.load(f)

start = dt.datetime(2018,1,1)
end= dt.datetime(2019,1,1)

for ticker in tickers:
	print(ticker)
	df=web.get_data_yahoo(ticker,start,end)
	df.reset_index()
	df.to_sql(ticker,conn,if_exists='append')


