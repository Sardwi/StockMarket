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

start = dt.datetime(int(startyear),int(startmonth),int(startday))
now = dt.datetime.now()

df = pdr.get_data_yahoo(stock,start,now)
#print(df)

ma_period1 = input('Enter MA period: ')
df['ma1'] = df['Adj Close'].rolling(window=int(ma_period1)).mean()
#print(df)

ma_period2 =input('Enter MA period2: ')
df['ma2'] = df['Adj Close'].rolling(window=int(ma_period2)).mean()

df['avg volume'] = df['Volume'].rolling(window=int(ma_period2)).mean()
#print(df.dtypes)
df = df.iloc[int(ma_period2):]

flag = -1

def triggers(df):
	buy_trigs = []
	sell_trigs = []

	flag = -1

	for i in range(len(df)):
		if df['ma1'][i]>df['ma2'][i]:
			if flag != 1:
				buy_trigs.append(df['Adj Close'][i])
				sell_trigs.append(np.nan)
				flag = 1
			else:
				sell_trigs.append(np.nan)
				buy_trigs.append(np.nan)
		elif df['ma1'][i]<df['ma2'][i]:
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

idx_b1 = df['buy_trigs'].first_valid_index()
idx_b2 = df['sell_trigs'].first_valid_index()
bc = df['buy_trigs'].count()
sc = df['sell_trigs'].count()

#df.to_csv('aapldata.csv')

pnl = 0
count = 0
totalinvestment = 0
if bc==sc:
	pnl = df['sell_trigs'].sum() - df['buy_trigs'].sum() 
	count = bc
	totalinvestment = df['buy_trigs'].sum()

elif bc>sc:
	pnl = df['sell_trigs'].sum() - df['buy_trigs'].sum() + df['buy_trigs'][df['buy_trigs'].last_valid_index()]
	count = sc
	totalinvestment = df['buy_trigs'].sum() - df['buy_trigs'][df['buy_trigs'].last_valid_index()]

elif bc<sc:
	pnl = df['sell_trigs'].sum() - df['buy_trigs'].sum() - df['sell_trigs'][df['sell_trigs'].last_valid_index()]
	count = bc
	totalinvestment = df['buy_trigs'].sum()

pnlpercent = (pnl/totalinvestment)*100
#print(totalinvestment)
print('Net Profit and Loss after '+str(count)+' trades is: ' +str(pnl))
print('Net Profit and Loss % after '+str(count)+' trades is: ' +str(pnlpercent)+'%')


def chart_strategy(df):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x = df.index,
                                open = df['Open'],
                                close = df['Close'],
                                low = df['Low'],
                                high = df['High'],name="Candles",increasing_line_color= 'green', decreasing_line_color= 'red'))

    fig.add_trace(go.Scatter(x = df.index, y = df['ma1'],name="30 Day SMA",line_color='#ffe476'))

    fig.add_trace(go.Scatter(x = df.index, y = df['ma2'],name="60 Day SMA",line_color='#0000ff'))

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
