import bs4 as bs
import os
import pandas as pd 
import pandas_datareader.data as web
import pickle
import requests
import datetime as dt
import yfinance as yf
import sqlite3
import streamlit as st 
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "stockdatasql.db")

conn = sqlite3.connect(db_path)
c= conn.cursor()

st.write("""#**Stock Market Screener**""")

image = Image.open("image.jpg")

st.image(image,use_column_width=True)

st.sidebar.header('User Input')

with open("nifty50tickers.pickle","rb") as f:
			tickers = pickle.load(f)

def get_inputs():
	macd_w = st.sidebar.text_input("MACD Weight","9")
	macd_l = st.sidebar.text_input("MACD Long","26")
	macd_s = st.sidebar.text_input("MACD Short","12")
	ma1p = st.sidebar.text_input("MA Short Period","30")
	ma2p = st.sidebar.text_input("MA Long Period","60")
	rsip = st.sidebar.text_input("RSI Period","14")
	bolp = st.sidebar.text_input("Bolinger Period","20")
	return(macd_w,macd_l,macd_s,ma1p,ma2p,rsip,bolp)

macd_w,macd_l,macd_s,ma1p,ma2p,rsip,bolp=get_inputs()

screened_stocks =  pd.DataFrame(columns=['Stock', 'Adj Close','Volume','MACD','RSI','bol_mid','sma'])
for ticker in tickers:
	query = "SELECT * from '" + ticker + "'"
	df = pd.read_sql_query(query, conn)
	macd_weight=macd_w
	macd_long = macd_l
	macd_short =macd_s
	ma_period1 = ma1p
	ma_period2 =ma2p
	df['MACDshortEMA']=df['Adj Close'].ewm(span=int(macd_short),adjust=False).mean()
	df['MACDlongEMA']=df['Adj Close'].ewm(span=int(macd_long),adjust=False).mean()
	df['MACD']=df['MACDshortEMA']-df['MACDlongEMA']
	df['Signal']=df['MACD'].ewm(span=int(macd_weight),adjust=False).mean()
	df['MACDH']=(df['MACD']-df['Signal'])

	df['ma1'] = df['Adj Close'].rolling(window=int(ma_period1)).mean()
	df['ma2'] = df['Adj Close'].rolling(window=int(ma_period2)).mean()

	rsi_period = rsip
	chg = df['Adj Close'].diff(1)
	up=chg.mask(chg<0,0)
	down=chg.mask(chg>0,0)
	average_gain=up.ewm(com=int(rsi_period)-1,min_periods=int(rsi_period)).mean()
	average_loss=down.ewm(com=int(rsi_period)-1,min_periods=int(rsi_period)).mean()
	rs = abs(average_gain/average_loss)
	rsi = 100-(100/(1+rs))
	df['rsi']=rsi

	bol_per=bolp
	df['bol_mid'] = df['Adj Close'].rolling(window=int(bol_per)).mean()
	df['bol_up']=df['bol_mid'] + 2*(df['Adj Close'].rolling(window=int(bol_per)).std())
	df['bol_down']=df['bol_mid'] - 2*(df['Adj Close'].rolling(window=int(bol_per)).std())

	Adj_Close = df['Adj Close'].iloc[-1]
	volume = df['Volume'].iloc[-1]
	macd = df['MACD'].iloc[-1]
	rsi_val = df['rsi'].iloc[-1]
	bol = df['bol_mid'].iloc[-1]
	sma = df['ma1'].iloc[-1]

	c1=0
	c2=0
	c3=0
	c4=0
	c5=0

	if df['MACD'].iloc[-1]>0:
		c1=1
	if df['ma1'].iloc[-1]>df['ma2'].iloc[-1]:
		c2=1
	if df['rsi'].iloc[-1]>50 and df['rsi'].iloc[-1]<70:
		c3=1
	if df['Adj Close'].iloc[-1]>df['bol_mid'].iloc[-1]:
		c4=1

	if c1+c2+c3+c4>3:
		screened_stocks = screened_stocks.append({'Stock':ticker, 'Adj Close': Adj_Close ,'Volume': volume,'MACD':macd,'RSI':rsi_val,'bol_mid':bol,'sma':sma},ignore_index=True)

st.write(screened_stocks)