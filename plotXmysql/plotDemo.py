import pymysql
import pymysql.cursors
import pandas as pd
import plotly.plotly as py
import datetime as dt
import numpy as np
from plotly.graph_objs import *
import random
import time

colorArr = ['rgba(255, 128, 0, .9)', 'rgba(0, 0, 255, .9)', 'rgba(0, 255, 0, .9)']
watchFlight = 'NH011NH933'
def getSqlTableNameDate (date):
    year = date[:4]
    month = date[5:7]
    day = date[8:10]
    return (year + month + day)
def toDF (dfRow, color, date):
    df = pd.DataFrame( [[i[ij] for ij in i] for i in dfRow] )
    df.rename(columns={0: 'price', 1: 'flight', 2: 'duration', 3: 'id', 4: 'tCount', 5: 'qDate'}, inplace=True)
    # print(date)
    # print(df)
    df['duration'] = pd.to_datetime(df['duration'])
    df['duration'] = df['duration'].dt.time
    df['qDate'] = pd.to_datetime(df['qDate'])
    # a = df['qDate'].dt.date
    for index, row in df.iterrows():
        df.loc[index, 'flight'] = (df.loc[index, 'flight'] + '||' + date)
        df.loc[index, 'id'] = color
        # if row['tCount'] == 0:
        #     df.loc[index, 'id'] = colorArr[2]
        # else:
        #     df.loc[index, 'id'] = color
    return df
def getColor():
    flag = False
    color = 'rgba('
    for x in range(0,3):
        if random.randint(0,1) == 1:
            color += '255,'
        else:
            color += '0,'
            flag = True
    if not flag:
        color = colorArr[0]
        return color
    return (color + '.9)')
def getColor2():
    flag = False
    color = 'rgba('
    for x in range(0,3):
        n = random.randint(0,256)
        color += (str(n) + ',')
        if n < 200:
            flag = True
    if not flag:
        color = colorArr[0]
        return color
    return (color + '.9)')
def getTrace(mergedDF):
    trace = Scatter(
        x=mergedDF['duration'],
        y=mergedDF['price'],
        text=mergedDF['flight'],
        mode='markers',
        hoverinfo='text+y',
        marker=dict(
            size=10,
            color = mergedDF['id'],
            colorscale = 'Viridis',
            opacity = 0.7
        )
    )
    return trace
def getTraceQueryDate(mergedDF):
    trace = Scatter(
        x=mergedDF['qDate'],
        y=mergedDF['price'],
        text=mergedDF['flight'],
        name=mergedDF['flight'][0][10:],
        # mode='markers',
        hoverinfo='text+y',
        marker=dict(
            size=10,
            color = mergedDF['id'],
            colorscale = 'Viridis',
            opacity = 0.7
        )
    )
    return trace
def findFlight(flight, df):
    result = []
    for index, row in df.iterrows():
        if row['flight'][:len(flight)] == flight:
            result.append(row)
            # print(row)
    return pd.DataFrame(result)
destCan = "can"
destHKG = 'hkg'
orig = "ord"
departD = ['2019-12-21', '2019-12-22']
returnD = ['2020-01-10','2020-01-11', '2020-01-12']
combinedD = []
readableD = []
sql = 'select distinct(price),flight,duration,flight1,t_count,query_date from '
connection = pymysql.connect(host='localhost', user='root', password='12345678', db='flightInfo', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
for x in departD:
    for y in returnD:
        combinedD.append(getSqlTableNameDate(x) + getSqlTableNameDate(y))
        readableD.append(x +'/' + y)
# combinedD = getSqlTableNameDate(departD) + getSqlTableNameDate(returnD)
dfCAN = []
dfHKG = []
for x in range(0,len(combinedD)):
    # cursor = connection.cursor()
    sqlCan = sql + orig + destCan + combinedD[x]
    cursor.execute(sqlCan)
    rowsCAN = cursor.fetchall()
    # print("===========" + 'can')
    dfCAN.append(toDF(rowsCAN, getColor2(), readableD[x]))
    # print("===========" + 'hkg')
    sqlHKG = sql + orig + destHKG + combinedD[x]
    cursor.execute(sqlHKG)
    rowsHKG = cursor.fetchall()
    dfHKG.append(toDF(rowsHKG, getColor2(), readableD[x]))
layout = Layout(
    xaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=True,
        # type='date',
        # tickformat='%H:%M:%S'
    ),
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=True
    ),
    hovermode='x'
)

figN = []
findFlightInCan = []
for x in dfCAN:
    findFlightInCan.append(findFlight(watchFlight,x))
mergedDF3 = pd.concat(findFlightInCan).sort_values('qDate')
# getTraceQueryDate(mergedDF3)
figN.append(Figure(data=[getTraceQueryDate(x.sort_values('qDate')) for x in findFlightInCan[:3]], layout=layout))
py.plot(figN[len(figN)-1], filename='can 12-21') #specific flight
figN.append(Figure(data=[getTraceQueryDate(x.sort_values('qDate')) for x in findFlightInCan[3:]], layout=layout))
time.sleep(10)
py.plot(figN[len(figN)-1], filename='can 12-22') #specific flight
figN.append(Figure(data=[getTraceQueryDate(x.sort_values('qDate')) for x in findFlightInCan], layout=layout))
time.sleep(10)
py.plot(figN[len(figN)-1], filename='can merged') #specific flight

# time.sleep(10)
#
# for x in range(0, len(dfCAN)):
#     mergedDF = pd.concat([dfCAN[x], dfHKG[x]])
#     mergedDF = mergedDF.sort_values('duration')
#     figN.append(Figure(data=[getTrace(mergedDF)], layout=layout))
# # tt = 'From ' + orig + ' to ' + destCan + '/' + destHKG + ' on ' + departD + ' ,return ' + returnD
#
# mergedDF = pd.concat(dfCAN).sort_values('duration')
# figN.append(Figure(data=[getTrace(mergedDF)], layout=layout))
# py.plot(figN[len(figN)-1], filename='x') #can
#
# mergedDF2 = pd.concat(dfHKG).sort_values('duration')
# figN.append(Figure(data=[getTrace(mergedDF2)], layout=layout))
# time.sleep(10)
# py.plot(figN[len(figN)-1], filename='y') #hkg
