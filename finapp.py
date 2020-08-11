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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "stockdatasql.db")

conn = sqlite3.connect(db_path)
c= conn.cursor()

with open("nifty50tickers.pickle","rb") as f:
			tickers = pickle.load(f)

st.write("**STOCK MARKET TOOL**")
st.sidebar.header("Navigation Bar and User Inputs")

def choose_app():
	choice = st.sidebar.selectbox("Chose App",('Charts','Screener'))

	return(choice)

def get_in():
	start = st.sidebar.text_input("Start Date","2019-1-1")
	end = st.sidebar.text_input("End Date","2020-1-1")
	symbol = st.sidebar.text_input("Stock Symbol","WIPRO.NS")
	symbol=symbol.upper()
	return(start,end,symbol)

def select_indicators():
    indicator_list=['MACD','RSI','Bol Bands']
    i=st.sidebar.multiselect("Indicators",indicator_list)
    return(i)

def get_inputs():
	macd_w = st.sidebar.slider("MACD Weight",value=9,min_value=1,max_value=25)
	macd_l = st.sidebar.slider("MACD Long",value=26,min_value=1,max_value=50)
	macd_s = st.sidebar.slider("MACD Short",value=12,min_value=1,max_value=50)
	ma1p = st.sidebar.slider("MA Short Period",value=30,min_value=1,max_value=100)
	ma2p = st.sidebar.slider("MA Long Period",value=60,min_value=1,max_value=200)
	rsip = st.sidebar.slider("RSI Period",value=14,min_value=1,max_value=50)
	bolp = st.sidebar.slider("Bolinger Period",value=20,min_value=1,max_value=50)
	return(macd_w,macd_l,macd_s,ma1p,ma2p,rsip,bolp)

def get_company_data(symbol,start,end):
	query = "SELECT * from '" + symbol + "'"
	df = pd.read_sql_query(query, conn)
	#df = pd.read_csv('stocks/{}.csv'.format(symbol))
	start = pd.to_datetime(start)
	end = pd.to_datetime(end)

	start_row = 0
	end_row = 0

	for i in range(len(df)):
		if start <=pd.to_datetime(df['Date'][i]):
			start_row = i
			break
	for j in range(len(df)):
		if end >= pd.to_datetime(df['Date'][len(df)-1-j]):
			end_row = len(df) - 1- j
			break

	df = df.set_index(pd.to_datetime(df['Date'].values))

	return df.iloc[start_row:end_row+1,:]

def chart_strategy(df,num_subplot):
    fig = go.Figure()
    if num_subplot==4:
        rh=[0.4, 0.2,0.2,0.2]
    elif num_subplot==3:
        rh=[0.6, 0.2,0.2]
    else:
        rh =[0.7,0.3]
    fig = make_subplots(rows=num_subplot, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.1,row_heights=rh)
#Candlesticks
    fig.add_trace(go.Candlestick(x = df['Date'],
                                open = df['Open'],
                                close = df['Close'],
                                low = df['Low'],
                                high = df['High'],name="Candles",increasing_line_color= 'green', decreasing_line_color= 'red'),row=1,col=1)
    # if i30smaflag==1:
    #     fig.add_trace(go.Scatter(x = df.index, y = df['ma1'],name="30 Day SMA",line_color='blue'),row=1,col=1)
    # if i30smaflag==1:
    #     fig.add_trace(go.Scatter(x = df.index, y = df['ma2'],name="60 Day SMA",line_color='purple'),row=1,col=1)

    if bol_flag==1:
        fig.add_trace(go.Scatter(x = df['Date'], y = df['bol_mid'],name="BOL MID",line_color='white'),row=1,col=1)
        fig.add_trace(go.Scatter(x = df['Date'], y = df['bol_up'],name="BOL UP",line_color='green',fill='tonexty',fillcolor='rgba(110, 110, 110, 0.1)'),row=1,col=1)
        fig.add_trace(go.Scatter(x = df['Date'], y = df['bol_down'],name="BOL Down",line_color='red',fill='tonexty',fillcolor='rgba(110, 110, 110, 0.1)'),row=1,col=1)


#Volume
    fig.add_trace(go.Bar(x = df['Date'], y = df['Volume'],name='Volume',marker_color=colour),row=2,col=1)
    # if flag==1:
    #     fig.add_trace(go.Scatter(x = df['Date'], y = df['EMAvol'],name="Average",line_color='orange'),row=2,col=1)
    # elif flag==2:
    # 	fig.add_trace(go.Scatter(x = df['Date'], y = df['SMAvol'],name="Average",line_color='orange'),row=2,col=1)

    if macd_flag==1:
        fig.add_trace(go.Scatter(x = df['Date'], y = df['MACD'],name="MACD Line",line_color='green'),row=3,col=1)
        fig.add_trace(go.Scatter(x = df['Date'], y = df['Signal'],name="MACD Signal",line_color='red'),row=3,col=1)
        fig.add_trace(go.Bar(x = df['Date'], y = df['MACDH'],name='MACD Histogram',marker_color=colour),row=3,col=1)

    if rsi_flag==1 and macd_flag!=1:
        fig.add_trace(go.Scatter(x = df['Date'], y = df['rsi'],name="RSI",line_color='white'),row=3,col=1)
    elif rsi_flag==1 and macd_flag==1:
        fig.add_trace(go.Scatter(x = df['Date'], y = df['rsi'],name="RSI",line_color='white'),row=4,col=1)
    fig.update_xaxes(
    rangebreaks=[
        dict(bounds=["sat", "sun"]), #hide weekends
    ]
)
    fig.update_yaxes(title_text="Price Data", row=1, col=1)
    fig.update_yaxes(title_text="Volumes", row=2, col=1)
    if macd_flag==1:
    	fig.update_yaxes(title_text="MACD", row=3, col=1)
    if rsi_flag==1 and macd_flag!=1:
    	fig.update_yaxes(title_text="RSI", row=3, col=1)
    if macd_flag==1 and rsi_flag==1:
    	fig.update_yaxes(title_text="MACD", row=3, col=1)
    	fig.update_yaxes(title_text="RSI", row=4, col=1)
    fig.update_xaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig



choice = choose_app()

if choice == 'Charts':
	start,end,symbol=get_in()
	df=get_company_data(symbol,start,end)
	selected_indicators=select_indicators()
	rsi_flag=0
	macd_flag=0
	bol_flag=0
	i30smaflag=0
	i60smaflag=0

	if 'RSI' in selected_indicators:
	    rsi_flag = 1
	if 'MACD' in selected_indicators:
	    macd_flag = 1
	if 'Bol Bands' in selected_indicators:
	    bol_flag = 1
	# if '30 Day SMA' in selected_indicators:
	#     i30smaflag = 1
	# if '60 Day SMA' in selected_indicators:
	#     i60smaflag = 1

	macd_weight='9'
	macd_long ='26' 
	macd_short ='12'
	ma_period1 = '30'
	ma_period2 ='60'


	if macd_flag==1:
	    df['MACDshortEMA']=df['Adj Close'].ewm(span=int(macd_short),adjust=False).mean()
	    df['MACDlongEMA']=df['Adj Close'].ewm(span=int(macd_long),adjust=False).mean()
	    df['MACD']=df['MACDshortEMA']-df['MACDlongEMA']
	    df['Signal']=df['MACD'].ewm(span=int(macd_weight),adjust=False).mean()
	    df['MACDH']=(df['MACD']-df['Signal'])

	if i30smaflag== 1:
	    df['ma1'] = df['Adj Close'].rolling(window=int(ma_period1)).mean()
	if i60smaflag==1:
	    df['ma2'] = df['Adj Close'].rolling(window=int(ma_period2)).mean()

	if rsi_flag==1:
	    rsi_period = 14
	    chg = df['Adj Close'].diff(1)
	    up=chg.mask(chg<0,0)
	    down=chg.mask(chg>0,0)
	    average_gain=up.ewm(com=rsi_period-1,min_periods=rsi_period).mean()
	    average_loss=down.ewm(com=rsi_period-1,min_periods=rsi_period).mean()
	    rs = abs(average_gain/average_loss)
	    rsi = 100-(100/(1+rs))
	    df['rsi']=rsi

	if bol_flag==1:
	    bol_per=20
	    df['bol_mid'] = df['Adj Close'].rolling(window=20).mean()
	    df['bol_up']=df['bol_mid'] + 2*(df['Adj Close'].rolling(window=20).std())
	    df['bol_down']=df['bol_mid'] - 2*(df['Adj Close'].rolling(window=20).std())

	df['0']=0

	colour = []
	for i in range(len(df)):
	    if df['Open'][i]>=df['Close'][i]:
	        colour.append('red')
	    else:
	        colour.append('green')
	num_subplot = 2 + rsi_flag + macd_flag
	if num_subplot!=2:
		df = df.iloc[60:]
	
	chart = chart_strategy(df,num_subplot)
	title = "Candlestick chart for " + symbol
	chart.update_layout(title=title)
	chart.update_layout(width=2000,height=2000) 
	chart.layout.template = 'plotly_dark'

	st.write(chart)

elif choice== 'Screener':
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
		macd = df['MACDH'].iloc[-1]
		rsi_val = df['rsi'].iloc[-1]
		bol = df['bol_mid'].iloc[-1]
		sma = df['ma1'].iloc[-1]

		c1=0
		c2=0
		c3=0
		c4=0
		c5=0

		if df['MACDH'].iloc[-1]>0:
			c1=1
		if df['ma1'].iloc[-1]>df['ma2'].iloc[-1]:
			c2=1
		if df['rsi'].iloc[-1]>50 and df['rsi'].iloc[-1]<70:
			c3=1
		if df['Adj Close'].iloc[-1]>df['bol_mid'].iloc[-1]:
			c4=1

		if c1+c2+c3+c4==4:
			screened_stocks = screened_stocks.append({'Stock':ticker, 'Adj Close': Adj_Close ,'Volume': volume,'MACD':macd,'RSI':rsi_val,'bol_mid':bol,'sma':sma},ignore_index=True)
	st.write("**Filtered Stocks:**")
	st.write(screened_stocks)

