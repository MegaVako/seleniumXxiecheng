import pymysql
import pymysql.cursors
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import datetime as dt
import numpy as np
connection = pymysql.connect(host='localhost', user='root', password='12345678', db='flightInfo', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
sql = 'select distinct(price),flight,duration,tempID from test2 where flight In ( select flight from test2 group by flight ) order by flight,price '
cursor.execute(sql)
rows = cursor.fetchall()
# for x in rows:
#     x['flight'] = x['flight'] + str(x['tempID'])
newTime = []
df = pd.DataFrame( [[i[ij] for ij in i] for i in rows] )
df.rename(columns={0: 'price', 1: 'flight', 2: 'duration', 3: 'id'}, inplace=True);

df['duration'] = pd.to_datetime(df['duration'])
df['duration'] = df['duration'].dt.time
df = df.sort_values('duration')
# for x in df['duration']:
#     tempX = str(x)[len(str(x))-8:]
#     newTime.append(dt.time(int(tempX[0:2]), int(tempX[3:5]), int(tempX[6:8])))
#newTime = [DT.datetime.strptime(str(x)[len(str(x))-8:], '%H:%M:%S') for x in df['duration']]

trace0 = go.Scatter(
    x=df['duration'],
    y=df['price'],
    text=df['flight'],
    mode='markers',
    marker=dict(
        size=16,
        color = np.random.randn(5000),
        colorscale='Viridis'
    )
)
layout = go.Layout(
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
    )
)
fig = go.Figure(data=[trace0], layout=layout)
py.plot(fig, filename='bubblechart-text')
