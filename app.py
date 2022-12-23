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

imagelist = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    imagelist.append(hdu.data)

images = np.array(imagelist)

#------------------------------------------------------------------------------
# scaled integer images

vmin = np.min(images)
vmax = np.max(images)
norm = 255.0/(vmax-vmin)

print(f"range {vmin} {vmax}")

scaled_images = (norm*(images-vmin)).astype(np.uint8)

#------------------------------------------------------------------------------
# define color scales
cmap_lasco = plt.get_cmap('soholasco2')
cmap_stereo = plt.get_cmap('stereocor2')

cscale_lasco = matplotlib_to_plotly(cmap_lasco, 255)
cscale_stereo = matplotlib_to_plotly(cmap_stereo, 255)

names = ["LASCO/C2","STEREO/COR2"]

scaledict = {names[0]: cscale_lasco,
             names[1]: cscale_stereo}

#------------------------------------------------------------------------------
# plot figure
fig = px.imshow(scaled_images, animation_frame=0,
                labels=dict(animation_frame="frame"),
                zmin=0,
                zmax=255
                )

fig.update_traces({
    "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
    "showscale": False
    },
    selector = {'type':'heatmap'}
)

fig.data[0].showscale = False
for f in fig.frames:
    f.data[0].showscale = False

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
    "height": 800,
    "showlegend": False,
    "font": {
        "size":30,
        "color":"goldenrod",
        "family": "Arial Black"
        },
    "paper_bgcolor": "black",
    "plot_bgcolor": "black",
    "transition": {'duration': 1000}
})

fig.update_layout(transition = {'duration': 1000})

# I think this is the frame rate in ms
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 0

# This is the transition between frames - not sure why it is different
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

# trying to see if this makes it faster in case it is trying to do a linear 
# interpolation - doesn't seem to matter
#fig.layout.updatemenus[0].buttons[0].args[1]['transition']['easing'] = None

#fig.layout.updatemenus[0].buttons[0].args[1]['direction'] = 'reverse'

#print(fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'])

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

print(fig)

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
            [dcc.Graph(
                id = "image-plot",
                config={"displayModeBar": False},
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
    [Input("color-chooser", "value")],
)
def update_plot(cscale):
    for f in fig.frames:
        f.layout.coloraxis.colorscale = scaledict[cscale] 
    fig.update_layout({
        "coloraxis": {'colorscale': scaledict[cscale]},
    })
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
