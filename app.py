from astropy.io import fits
from datetime import date
from dash import Dash, dcc, html, Input, Output
from skimage import data

import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import sunpy.visualization.colormaps as cm

EXPLAINER = """This is a simple demo of a DASH application that is relevant for
pyCAT.  It starts from a dash example and css template obtained from here:
https://github.com/tcbegley/dash-bootstrap-css"""

# Note: the original example from the dash-bootstrap-css repo has lots
# of other useful examples, like a checklist, a range slider, and
# selectors for single dates or date ranges.  Worth going back to as
# we make this more sophisticated.

# you can read in a series of fits images into a list or numpy array here 
# before calling the application.  Then that list is available to you.

def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale
#------------------------------------------------------------------------------
# define images

# arbitrary sequence of 10 STEREO L3 images
dir = '/home/mark.miesch/Products/image_processing/ATBD/data/stereo_a/L3_2012_09'
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

images = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    images.append(hdu.data)

# sample image for plotting
#image = data.shepp_logan_phantom()

image = images[0]

#------------------------------------------------------------------------------
# define color scales
cmap_lasco = plt.get_cmap('soholasco2')
cmap_stereo = plt.get_cmap('stereocor2')

cscale_lasco = matplotlib_to_plotly(cmap_lasco, 255)
cscale_stereo = matplotlib_to_plotly(cmap_stereo, 255)

names = ["LASCO/C2","STEREO/COR2"]

scaledict = {names[0]: cscale_lasco,
             names[1]: cscale_stereo}

app = Dash()

app.layout = dbc.Container(
    [
        html.H1("Simple DASH demo"),
        dcc.Markdown(EXPLAINER),
        html.Hr(),
        dbc.Card(
            [
                html.H4("Color Table", className="card-title"),
                dcc.Dropdown(
                    id = "color-chooser",
                    options=names,
                    value = "LASCO/C2"
                ),
            ],
            body=True,
            className="mb-3",
        ),
        dbc.Card(
            [
                html.H4("Frame selection", className="card-title"),
                dcc.Slider(
                    id = "frame-chooser",
                    min=1,
                    max=10,
                    step=1,
                    value=1,
                    marks={i: {"label": str(i)} for i in range(0, 21, 4)},
                ),
            ],
            body=True,
            className="mb-3",
        ),
        dbc.Card(
            [dcc.Graph(
                id = "image-plot",
                config={"displayModeBar": False}
            ),
            ],
            body=True,
            className="mb-3"
        )
    ],
    id="container",
    style={"marginBottom": "300px", "marginTop": "20px"},
    className="dash-bootstrap",
)

@app.callback(
    Output("image-plot", "figure"),
    [Input("color-chooser", "value"), Input("frame-chooser", "value")],
)
def update_plot(cscale, frame):
    image_plot = {
        "data": [
            {
                "z": images[frame-1],
                "type": "heatmap",
                "showscale": False,
                "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
                "colorscale": scaledict[cscale]
            },
        ],
        "layout": {
            "xaxis": {
                "scaleanchor":'y',
                "showticklabels": False,
                "visible": False
                },
            "yaxis": {
                "showticklabels": False,
                "visible": False
                },
            "margin": {
                't': 10,
                'b': 10,
                'l': 10,
                'r': 10,
            },
            "height": 800,
            "showlegend": False,
            "paper_bgcolor": "black",
            "plot_bgcolor": "black",
        },
    }
    return image_plot

if __name__ == "__main__":
    app.run_server(debug=True)
