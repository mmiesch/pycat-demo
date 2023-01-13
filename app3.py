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
import matplotlib.pyplot as plt
import sunpy.visualization.colormaps as cm

#------------------------------------------------------------------------------
def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

#------------------------------------------------------------------------------
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
# lasco/C2 color scale

cmap_lasco = plt.get_cmap('soholasco2')

cscale_lasco = matplotlib_to_plotly(cmap_lasco, 255)

#------------------------------------------------------------------------------
# generate figure

fig = px.imshow(buffer[0], zmin=0, zmax=255)

fig.update_traces({
    "showscale": False,
    "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
    },
    selector = {'type':'heatmap'}
)

fig.data[0].showscale = False

fig.update_layout({
    "coloraxis": {'colorscale': cscale_lasco},
    "xaxis": {
        "scaleanchor":"y",
        "showticklabels": False,
        "visible": False,
    },
    "yaxis": {
        "visible": False
    },
    "showlegend": False,
    "height": 800,
    "paper_bgcolor": "black",
    "plot_bgcolor": "black",
})

#------------------------------------------------------------------------------

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#------------------------------------------------------------------------------

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Simple DASH Demo',
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
            ),
            'Frame selection',
            dcc.Slider(
                id = "frame-selection",
                min = 0,
                max = buffersize-1,
                step = 1,
                value = 0
            ),
        ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
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
    Input('frame-selection', 'value'),
    State('buffer', 'data'),
    State('example-graph', 'figure')
)
def update_figure(frame, data, figure):
    figure['data'][0]['z'] = data[frame]
    return figure

app.run()