import pandas as pd 
import yfinance as yf 
import streamlit as st 
from PIL import Image
import datetime
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
import sqlite3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "stockdatasql.db")

conn = sqlite3.connect(db_path)
c= conn.cursor()

st.write("""
#Stock Market Web App
**Visually** show data!
""")

image = Image.open("image.jpg")

st.image(image,use_column_width=True)

st.sidebar.header('User Input')

#function to get user input

def get_in():
	start = st.sidebar.text_input("Start Date","2019-1-1")
	end = st.sidebar.text_input("End Date","2020-1-1")
	symbol = st.sidebar.text_input("Stock Symbol","WIPRO.NS")
	return(start,end,symbol)

def select_indicators():
    indicator_list=['MACD','RSI','Bol Bands']
    i=st.sidebar.multiselect("Indicators",indicator_list)
    return(i)

# funcion to get name
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

start,end,symbol=get_in()
df=get_company_data(symbol,start,end)
selected_indicators=select_indicators()
rsi_flag=0
macd_flag=0
bol_flag=0

if 'RSI' in selected_indicators:
    rsi_flag = 1
if 'MACD' in selected_indicators:
    macd_flag = 1
if 'Bol Bands' in selected_indicators:
    bol_flag = 1

macd_weight='9'
macd_long ='26' 
macd_short ='12'
ma_period1 = '30'
ma_period2 ='60'

df['MACDshortEMA']=df['Adj Close'].ewm(span=int(macd_short),adjust=False).mean()
df['MACDlongEMA']=df['Adj Close'].ewm(span=int(macd_long),adjust=False).mean()
df['MACD']=df['MACDshortEMA']-df['MACDlongEMA']
df['Signal']=df['MACD'].ewm(span=int(macd_weight),adjust=False).mean()
df['MACDH']=(df['MACD']-df['Signal'])

df['ma1'] = df['Adj Close'].rolling(window=int(ma_period1)).mean()
df['ma2'] = df['Adj Close'].rolling(window=int(ma_period2)).mean()

rsi_period = 14
chg = df['Adj Close'].diff(1)
up=chg.mask(chg<0,0)
down=chg.mask(chg>0,0)
average_gain=up.ewm(com=rsi_period-1,min_periods=rsi_period).mean()
average_loss=down.ewm(com=rsi_period-1,min_periods=rsi_period).mean()
rs = abs(average_gain/average_loss)
rsi = 100-(100/(1+rs))
df['rsi']=rsi

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

df = df.iloc[60:]
num_subplot = 2 + rsi_flag + macd_flag

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

    #fig.add_trace(go.Scatter(x = df.index, y = df['ma1'],name="30 Day SMA",line_color='blue'),row=1,col=1)

    #fig.add_trace(go.Scatter(x = df.index, y = df['ma2'],name="60 Day SMA",line_color='purple'),row=1,col=1)

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
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="RSI", row=4, col=1)
    fig.update_xaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='white', mirror=True)
    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig

chart = chart_strategy(df,num_subplot)
title = "Candlestick chart for " + symbol
chart.update_layout(title=title)
chart.update_layout(width=1100,height=900) 
chart.layout.template = 'plotly_dark'

st.write(chart)







