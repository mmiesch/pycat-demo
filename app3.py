"""
This builds off of the example in ex_clientside.py
"""

import random

from astropy.io import fits
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

app = Dash(__name__)

#------------------------------------------------------------------------------
# load image data
# arbitrary sequence of 10 STEREO L3 images
dir = './data'
files = [
    "STEREOA_L3_2012_09_16_113900.fts",
    "STEREOA_L3_2012_09_16_115400.fts",
    "STEREOA_L3_2012_09_16_122400.fts",
    "STEREOA_L3_2012_09_16_123900.fts",
    "STEREOA_L3_2012_09_16_125400.fts",
    "STEREOA_L3_2012_09_16_132400.fts",
    "STEREOA_L3_2012_09_16_133900.fts",
    "STEREOA_L3_2012_09_16_135400.fts",
    "STEREOA_L3_2012_09_16_142400.fts",
    "STEREOA_L3_2012_09_16_143900.fts"
]

imagelist = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    imagelist.append(hdu.data)

images = np.array(imagelist)

#------------------------------------------------------------------------------
# load scaled data

vmin = np.min(images)
vmax = np.max(images)

norm = 255.0/(vmax-vmin)

buffer = (norm*(images - vmin)).astype(np.uint8)

buffersize = buffer.shape[0]

#------------------------------------------------------------------------------
# generate figure

fig = px.imshow(buffer[0])

fig.update_layout({
    "xaxis": {
        "scaleanchor":"y",
        "showticklabels": False,
        "visible": False,
    },
    "yaxis": {
        "visible": False
    },
    "height": 800,
})

#------------------------------------------------------------------------------

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

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
                id = "gamma-correction",
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
        interval=10000,
        n_intervals=0
    ),

    # trigger plot updates
    dcc.Interval(
        id='client-interval',
        interval=1000,
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
              Input('gamma-correction', 'value'))
def change_gamma(gamma):
    data = (norm*(images - vmin)**gamma).astype(np.uint8)
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