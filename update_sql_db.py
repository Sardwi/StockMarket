import bs4 as bs
import os
import pandas as pd 
import pandas_datareader.data as web
import pickle
import requests
import datetime as dt
import yfinance as yf
import sqlite3
from os.path import realpath

#DATABASE_NAME = realpath('stockdatasql.db')
#print(DATABASE_NAME)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "stockdatasql.db")

conn = sqlite3.connect(db_path)
c= conn.cursor()

with open("nifty50tickers.pickle","rb") as f:
	tickers = pickle.load(f)

# c.execute('SELECT * FROM "WIPRO.NS"')

# rows = c.fetchall()

# for row in rows:
# 	print(row)

for ticker in tickers:
	# sql_select_Query = c.execute('select Date from {tn} order by Date DESC limit 1'.format(tn=ticker))
	# print(sql_select_Query)
	c.execute('SELECT Date FROM "{tn}" ORDER BY Date DESC LIMIT 1'.\
        format(tn=ticker))
	rows = c.fetchone()
	print(ticker)
	#print(rows)
	s = str(rows);
	r=s.split("'")
	#print(r[1])

	df = web.get_data_yahoo(ticker,r[1],dt.datetime.now())
	#print(df)
	df = df.iloc[1:]
	#print(df)
	df.to_sql(ticker,conn,if_exists='append')
	
	
conn.commit()
conn.close()