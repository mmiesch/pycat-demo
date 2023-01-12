"""
This builds off of the example in ex_clientside.py
"""

import random

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

app = Dash(__name__)

figsize = 100
buffersize = 5
buffer = np.random.random(size=(buffersize, figsize, figsize))  # some random image, quite literally
fig = px.imshow(buffer[0])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#------------------------------------------------------------------------------
# define min/max for gamma correction

vmin = np.min(buffer)
vmax = np.max(buffer)

#------------------------------------------------------------------------------

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Example dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(
        id='div-test',
        children=[
            'Gamma Correction',
            dcc.Slider(
                id = "color-chooser",
                min = 0.0,
                max = 5.0,
                value = 1.0
            )
        ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    # trigger data updates
    dcc.Interval(
        id='server-interval',
        interval=1000,
        n_intervals=0
    ),

    # trigger plot updates
    dcc.Interval(
        id='client-interval',
        interval=200,
        n_intervals=0
    ),

    # we'll store the plot data here from the server side
    dcc.Store(
        id='buffer',
        data=buffer
    ),

    # our plot
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

# reset client n_intervals every second
@app.callback(Output('client-interval', 'n_intervals'),
              Input('server-interval', 'n_intervals'))
def reset_counter(n_intervals):
    return 0

@app.callback(Output('buffer', 'data'),
              Input('color-chooser', 'value'))
def update_color_table(cmap):
    data = np.random.random(size=(buffersize, figsize, figsize))
    return data

# and finally we use the buffer to update the plot at a higher frequency.
# this is what I'd like to turn into a clientside callback. it works for now, but
# only up to a certain interval size.
app.clientside_callback(
    """function (n_intervals, data, figure) {
        newFig = JSON.parse(JSON.stringify(figure))
        newFig['data'][0]['z'] = data[n_intervals]
        return newFig
    }""",
    Output('example-graph', 'figure'),
    Input('client-interval', 'n_intervals'),
    State('buffer', 'data'),
    State('example-graph', 'figure')
)
def update_figure(n_intervals, data, figure):
    i = random.randint(0, buffersize-1)
    figure['data'][0]['z'] = data[i]
    return figure



app.run()