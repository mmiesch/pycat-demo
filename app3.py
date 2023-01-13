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
        ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    # we'll store the plot data here from the server side
    dcc.Store(
        id='figure-store',
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

# recreate figure when gamma changes
@app.callback(Output('figure-store', 'data'),
              Input('gamma-correction', 'value'))
def update_figure_data(gamma):
    data = ((norm*(images - vmin))**gamma).astype(np.uint8)
    fig = px.imshow(data, animation_frame=0,
                binary_string = True,
                labels={"animation_frame":"frame"},
                height=800,
                zmin=0, zmax=255
                )
#    fig.update_traces({
#        #"showscale": False,
#        "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
#        },
#        selector = {'type':'heatmap'}
#    )

#    fig.data[0].showscale = False
#    fig.data[0].showlegend = False

#    fig.layout.template.data.heatmap[0].colorscale = cscale_lasco
#    fig.layout.heatmapgl[0].colorscale = cscale_lasco
#    fig.layout.coloraxis.colorscale = cscale_lasco

    fig.update_layout(transition = {'duration': 0})
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 0
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

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

    for f in fig.frames:
        f.layout.coloraxis.colorscale = cscale_lasco
#        f.data[0].showscale = False

    return fig

# regenerate display when the figure store changes
app.clientside_callback(
    """
    function(figure) {
        if(figure === undefined) {
            return {'data': [], 'layout': {}};
        }
        const fig = Object.assign({}, figure, {});
        return fig;
    }
    """,
    Output('figure-graph', 'figure'),
    Input('figure-store', 'data'),
)
#@app.callback(
#    Output('figure-graph', 'figure'),
#    Input('figure-store', 'data'),
#)
#def refresh_display(data):
#    return data

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