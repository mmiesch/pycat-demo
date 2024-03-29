"""
This builds off of the example in ex_clientside.py
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

#------------------------------------------------------------------------------
# lasco/C2 color scale

cmap_lasco = plt.get_cmap('soholasco2')
cscale_lasco = matplotlib_to_plotly(cmap_lasco, 255)

#------------------------------------------------------------------------------
# for debugging
#data = (norm*(images - vmin)).astype(np.uint8)

data = images

fig = px.imshow(data, animation_frame=0,
            binary_string = True,
            labels={"animation_frame":"frame"},
            height=800,
            )

#fig = px.imshow(images[0],
#            binary_string = True,
#            height=800,
#            )

#fig.update_layout({
#    "coloraxis": {'colorscale': cscale_lasco},
#    "xaxis": {
#        "scaleanchor":"y",
#        "showticklabels": False,
#        "visible": False,
#    },
#    "yaxis": {
#        "visible": False
#    },
#    "showlegend": False,
#    "height": 800,
#    "paper_bgcolor": "black",
#    "plot_bgcolor": "black",
#})

print(80*'^')
print(fig.data[0])
#print(fig.data[0].source)
print(80*'^')
print(fig.frames[0].data[0])
print(80*'^')
print(80*'^')
print(fig.frames[1].data[0])
print(80*'^')

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

    dcc.Graph(
        figure=fig
    ),
    ])

app.run()