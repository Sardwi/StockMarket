import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import datetime as datetime
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio


yf.pdr_override() 
stock =input('Enter stock: ')
startyear =input('Enter startyear: ')
startmonth =input('Enter startmonth: ')
startday= input('Enter startday: ')
macd_weight= input('MACD SIGNAL LENGHT: ')
macd_long = input('MACD Long LENGHT: ')
macd_short = input('MACD short LENGHT: ')
start = dt.datetime(int(startyear),int(startmonth),int(startday))
now = dt.datetime.now()
df = pdr.get_data_yahoo(stock,start,now)

df['MACDshortEMA']=df['Adj Close'].ewm(span=int(macd_short),adjust=False).mean()
df['MACDlongEMA']=df['Adj Close'].ewm(span=int(macd_long),adjust=False).mean()
df['MACD']=df['MACDshortEMA']-df['MACDlongEMA']
df['Signal']=df['MACD'].ewm(span=int(macd_weight),adjust=False).mean()
df = df.iloc[int(macd_short):]
#print(df.head())

plt.figure(figsize=(12.5,4.5))
plt.plot(df.index,df['MACD'],label='MACD',color='red')
plt.plot(df.index,df['Signal'],label='Signal',color='blue')
plt.xticks(rotation = 45)
plt.show()

def triggers(df):
	buy_trigs = []
	sell_trigs = []

	flag = -1

	for i in range(len(df)):
		if df['MACD'][i]>df['Signal'][i]:
			if flag != 1:
				buy_trigs.append(df['Adj Close'][i])
				sell_trigs.append(np.nan)
				flag = 1
			else:
				sell_trigs.append(np.nan)
				buy_trigs.append(np.nan)
		elif df['MACD'][i]<df['Signal'][i]:
			if flag!=0:
				sell_trigs.append(df['Adj Close'][i])
				buy_trigs.append(np.nan)
				flag =0
			else:
				sell_trigs.append(np.nan)
				buy_trigs.append(np.nan)
		else:
			sell_trigs.append(np.nan)
			buy_trigs.append(np.nan)

	return(sell_trigs,buy_trigs)

bs = triggers(df)
df['buy_trigs'] = bs[1]
df['sell_trigs'] = bs[0]
print(df.head())

def chart_strategy(df):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x = df.index,
                                open = df['Open'],
                                close = df['Close'],
                                low = df['Low'],
                                high = df['High'],name="Candles",increasing_line_color= 'green', decreasing_line_color= 'red'))

    #fig.add_trace(go.Scatter(x = df.index, y = df['ma1'],name="30 Day SMA",line_color='#ffe476'))

    #fig.add_trace(go.Scatter(x = df.index, y = df['ma2'],name="60 Day SMA",line_color='#0000ff'))

    # fig.add_trace(go.Scatter(x = df.index, y = df['buy_trigs'],name="BUY"))

    # fig.add_trace(go.Scatter(x = df.index, y = df['sell_trigs'],name="SELL"))

    fig.add_trace(
    	go.Scatter(
        	mode='markers',
        	x=df.index,
        	y=df['buy_trigs'],
        	marker=dict(
            	color='white',
            	size=15,
            	symbol=5
        	),
        	showlegend=True,
        	name="BUY"
    	)
	)

    fig.add_trace(
    	go.Scatter(
        	mode='markers',
        	x=df.index,
        	y=df['sell_trigs'],
        	marker=dict(
            	color='gray',
            	size=15,
            	symbol=6
        	),
        	showlegend=True,
        	name="SELL"
    	)
	)




    return fig

chart=chart_strategy(df)
chart.update_layout(
	title="CandleStick Chart for "+str(stock),
	yaxis_title="Price",
	xaxis_title="Date")
chart.layout.template = 'plotly_dark' 
chart.show()