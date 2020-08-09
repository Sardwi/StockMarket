import bs4 as bs
import os
import pandas as pd 
import pandas_datareader.data as web
import pickle
import requests
import datetime as dt
import yfinance as yf

yf.pdr_override() 
def save_nifty50_tickers():
	resp = requests.get('https://en.wikipedia.org/wiki/NIFTY_50')
	soup = bs.BeautifulSoup(resp.text,"lxml")
	#find and get table data 
	table = soup.find('table',{'class':'wikitable sortable'})
	tickers = []
	for row in table.findAll('tr')[1:]:
		ticker = row.findAll('td')[1].text
		tickers.append(ticker)

	with open("nifty50tickers.pickle","wb") as f:
		pickle.dump(tickers,f)

	print(tickers)

	return tickers

save_nifty50_tickers()