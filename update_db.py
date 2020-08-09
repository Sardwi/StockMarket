import bs4 as bs
import os
import pandas as pd 
import pandas_datareader.data as web
import pickle
import requests
import datetime as dt
import yfinance as yf

date_now = dt.datetime.now()

# with open("nifty50tickers.pickle","rb") as f:
# 	tickers = tickers.load(f)

with open("nifty50tickers.pickle","rb") as f:
			tickers = pickle.load(f)

for ticker in tickers:
	df = pd.read_csv('stocks/{}.csv'.format(ticker))
	last_date = df['Date'].iloc[-1]
	#print(last_date)
	if last_date < str(dt.datetime.now()):
		#print(df)
		#print("")
		df2 = web.get_data_yahoo(ticker,last_date,date_now)
		df2 = df2.iloc[1:]
		df2 = df2.reset_index()
		dfa = df.append(df2,ignore_index = True)
		os.remove('stocks/{}.csv'.format(ticker))
		dfa.to_csv('stocks/{}.csv'.format(ticker))
		print('Updated data for '+ticker+' from '+last_date+ ' to '+ str(dt.datetime.now()))
		
