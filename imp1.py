"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""

from astropy.io import fits
from dash import Dash, dcc, html, Input, Output, State
from skimage.measure import block_reduce

import matplotlib.pyplot as plt
import numpy as np
import json
import sunpy.visualization.colormaps as cm

import plotly.express as px

#------------------------------------------------------------------------------
# create app object

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

#------------------------------------------------------------------------------
# image data

fname = "./data/STEREOA_L3_2012_09_16_125400.fts"

hdu = fits.open(fname)[0]

im = hdu.data

# downsample to 512 x 512
im = block_reduce(hdu.data, block_size = 2, func = np.nanmedian, cval = np.nanmin(im))

vmin = np.min(im)
vmax = np.max(im)
norm = 1.0 / (vmax-vmin)

image_data = (254*norm*(im - vmin)).astype(np.uint8)

print(f"Image range {np.min(image_data)} {np.max(image_data)}")
print(f"Image size {image_data.shape}")

#------------------------------------------------------------------------------
# color table

def matplotlib_to_plotly(cmap, ncolors):
    h = 1.0/(ncolors-1)
    pl_colorscale = []

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

cmap_lasco = plt.get_cmap('soholasco2')
cscale_lasco = matplotlib_to_plotly(cmap_lasco,255)

#------------------------------------------------------------------------------
# create figure

fig = px.imshow(image_data,
                zmin=0,
                zmax=255
                )
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
    "height": 600,
    "paper_bgcolor": "black",
    "plot_bgcolor": "black",
})

#------------------------------------------------------------------------------
# define layout

app.layout = html.Div([
    dcc.Graph(
        id='graph'
    ),
    dcc.Store(
        id = 'figure-store',
        data = fig
    ),
    'Color Saturation',
    dcc.RangeSlider(
        id = "range-slider",
        min = 1,
        max = 255,
        value = [1,255]
    ),
    'Gamma',
    dcc.Slider(
        id = "gamma-slider",
        min = 0.01,
        max = 5.0,
        value = 1.0
    ),
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='figure-contents'
        )
    ])
])

app.clientside_callback(
    """
    function(rng, figure) {
        if(figure === undefined) {
            return {'data': [], 'layout': {}};
        }
        const fig = Object.assign({}, figure, {
            'layout': {
                ...figure.layout,
                'coloraxis': {
                    ...figure.layout.coloraxis, cmin: rng[0], cmax: rng[1]
                }
            }
        });
        return fig;
    }
    """,
    Output('graph', 'figure'),
    Input('range-slider', 'value'),
    State('figure-store', 'data')
)

@app.callback(
    Output('figure-contents', 'children'),
    Input('graph', 'figure')
)
def print_figure_contents(data):
#    return '```\n'+json.dumps(data, indent=2)+'\n```'
    return '```\n'+json.dumps(data["layout"], indent=2)+'\n```'
#    return '```\n'+json.dumps(data["layout"]["coloraxis"], indent=2)+'\n```'
#    return '```\n'+json.dumps(data["name"], indent=2)+'\n```'


if __name__ == '__main__':
    app.run_server(debug=True)
