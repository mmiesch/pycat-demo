"""
This builds off of app3.py but it's an attempt to store the plot data in a buffer and only modify the data component of the figure, fig.frames[0].data[:].z), instead of redrawing the entire figure each time.  Currently I only know how to go about this with binary_string=False.  But even then it does not seem to be working.
"""

import random

from astropy.io import fits
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import json
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import sunpy.visualization.colormaps as cm

#------------------------------------------------------------------------------
def matplotlib_to_rgb(cmap, ncolors):
    h = 1.0/(ncolors-2)

    rgbmap = np.zeros((ncolors,3), dtype=np.uint8)

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        rgbmap[k,:] = (C[0], C[1], C[2])

    return rgbmap

def matplotlib_to_plotly(cmap, ncolors):
    h = 1.0/(ncolors-1)
    pl_colorscale = []

    for k in range(ncolors):
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

norm = 1.0/(vmax-vmin)

# used to reset the color scale
baseidx = np.arange(256)

#------------------------------------------------------------------------------
# lasco/C2 color scale

cmap_lasco = plt.get_cmap('soholasco2')
rgb_lasco = matplotlib_to_rgb(cmap_lasco, 255)
cscale_lasco = matplotlib_to_plotly(cmap_lasco,255)

#------------------------------------------------------------------------------
# generate original figure
# for performance, express the data as a 4D array, called rgb
# This includes the 3D data, expressed as a byte array (time,x,y),
# and a 4th dimension for the rgb values for each pixel value 0 to 254
# This allows you to use binary_string = True in the call to imshow,
# which greatly speeds up the rendering

# buffer for storing
rgb = np.zeros((images.shape[0],images.shape[1],images.shape[2],3),
                dtype=np.uint8)

basedata = (254*norm*(images - vmin)).astype(np.uint8)
for idx, val in np.ndenumerate(basedata):
    rgb[idx[0],idx[1],idx[2],:] = rgb_lasco[val,:]

fig = px.imshow(rgb, animation_frame=0,
            binary_string = True,
            labels={"animation_frame":"frame"},
            height=800,
            zmin=0, zmax=255
            )
fig.update_traces({
    "showscale": False,
    "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
    },
    selector = {'type':'heatmap'}
)

fig.update_layout(transition = {'duration': 0})
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 0
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

fig.update_layout({
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

reverse_button = {
    'args': [None, {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate',
             'fromcurrent': True, 'direction': 'reverse',
             'transition': {'duration': 0, 'easing': 'linear'}}],
    'label': '&#9664;',
    'method': 'animate'
}
fig.layout.updatemenus[0].buttons = (
    fig.layout.updatemenus[0].buttons[0],
    reverse_button,
    fig.layout.updatemenus[0].buttons[1],
    )

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
            'Color Max',
            dcc.Slider(
                id = "zmax-change",
                min = 1,
                max = 255,
                value = 1.0
            ),
        ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    dcc.Store(
        id='figure-data',
        data=rgb
    ),

    # this is to display the plot
    dcc.Graph(
        id='figure-graph',
    ),
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='figure-json'
        )
    ])])

@app.callback(Output('figure-data', 'data'),
              Input('gamma-correction', 'value'),
              State('figure-data','data'))
def update_figure_data(gamma,rgb):
    cidx = (255 * (baseidx/255.0)**(1/gamma)).astype(np.uint8)
    for idx, val in np.ndenumerate(basedata):
        rgb[idx[0],idx[1],idx[2],:] = rgb_lasco[cidx[val],:]

    return rgb

app.clientside_callback(
    """function (data,figure) {
        figure['frames'][0]['data'][0]['z'] = data[0]
        return figure
    }
    """,
    Output('figure-graph', 'figure'),
    Input('figure-data', 'data'),
    State('figure-graph', 'figure')
)

@app.callback(
    Output('figure-json', 'children'),
    Input('figure-store', 'data')
)
def generated_px_figure_json(data):
#    return '```\n'+json.dumps(data, indent=2)+'\n```'
    return '```\n'+json.dumps(data["layout"], indent=2)+'\n```'
#    return '```\n'+json.dumps(data["layout"]["template"]["data"], indent=2)+'\n```'
#    return '```\n'+json.dumps(data["layout"]["template"]["data"]["heatmap"][0], indent=2)+'\n```'

app.run()