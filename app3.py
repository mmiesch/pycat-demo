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
# define color scales
names = ["LASCO/C2","STEREO/COR2"]

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
            'Select color scale',
            dcc.Dropdown(
                id = "color-chooser",
                options = names,
                value = "LASCO/C2"
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

# I also added the below reset to make sure the data didnt get out of bounds.
#@app.callback(Output('buffer', 'data'),
#              Output('client-interval', 'n_intervals'),
#              Input('server-interval', 'n_intervals'))
#def update_data(n_intervals):
#    data = np.random.random(size=(buffersize, figsize, figsize))
#    return data, 0

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