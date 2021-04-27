import plotly.offline as py
from plotly.graph_objs import *
import pandas as pd
import math

my_cols = ['px_est', 'py_est', 'vx_est', 'vy_est', 'px_meas', 'py_meas', 'px_gt', 'py_gt', 'vx_gt', 'vy_gt']
with open('output-lidar-ctrv.txt') as df:
    table_ekf_output = pd.read_table(df, sep=' ', header=None, names=my_cols, lineterminator='\n')

    # table_ekf_output



# Measurements
trace2 = Scatter(
    x=table_ekf_output['px_meas'],
    y=table_ekf_output['py_meas'],
    xaxis='x2',
    yaxis='y2',
    name='Measurements',
    marker = dict(size = 3 ,color =6),
    mode='markers'

)

# estimations
trace1 = Scatter(
    x=table_ekf_output['px_est'],
    y=table_ekf_output['py_est'],
    xaxis='x2',
    yaxis='y2',
    name='Estimation with CTRV model',
    marker = dict(size = 3 ,color = 'blue'),
    mode='markers'
)

# Ground Truth
trace3 = Scatter(x=table_ekf_output['px_gt'], y=table_ekf_output['py_gt'],
                 xaxis='x2',
                 yaxis='y2',
                 name='Ground Truth',
                 marker = dict(size = 3 ,color =2),
                 mode='markers'
                 )

data = [trace1, trace2, trace3]

layout = Layout(
    xaxis2=dict(

        anchor='x2',
        title='position x'
    ),
    yaxis2=dict(

        anchor='y2',
        title='position y'
    )
)

fig = Figure(data=data, layout=layout)
py.plot(fig, filename='KF_lidar_ctrv.html')
