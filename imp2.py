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

# reference image
ref_frame = 4
im = images[:,:,ref_frame]

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
cscale_lasco = matplotlib_to_plotly(cmap_lasco,256)

nidx = np.arange(256,dtype='float')/255
cscale_buffer = cscale_lasco.copy()

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
    dcc.Store(
        id = 'colorscale',
        data = cscale_buffer
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
        max = 4.0,
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

#@app.callback(
#    Output("colorscale", "data"),
#    Input("gamma-slider","value")
#)
#def update_colorscale(gamma):
#    newidx = (255*np.power(nidx,(1.0/gamma))).astype(np.uint8)
#
#    # first implementation - see if it works - could likely be faster
#    newcs = cscale_lasco
#    for i in np.arange(len(newcs)):
#        newcs[i][1] = cscale_lasco[newidx[i]][1]
#    return newcs

@app.callback(
    Output("figure-store", "data"),
    Input("gamma-slider","value"),
    State("figure-store","data"),
    State("colorscale","data")
)
def update_colorscale(gamma, figure, newcs):
    newidx = (255*np.power(nidx,(1.0/gamma))).astype(np.uint8)

    for i in np.arange(len(newcs)):
        newcs[i][1] = cscale_lasco[newidx[i]][1]

    figure["layout"]["coloraxis"]["colorscale"] = newcs

    return figure

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
                    ...figure.layout.coloraxis,
                    cmin: rng[0], cmax: rng[1]
                }
            }
        });
        return fig;
    }
    """,
    Output('graph', 'figure'),
    Input('range-slider', 'value'),
    Input('figure-store', 'data')
)

# A try at gamma correction - not working
#app.clientside_callback(
#    """
#    function(rng, cscale, figure) {
#        cs = JSON.parse(JSON.stringify(cscale))
#        if(figure === undefined) {
#            return {'data': [], 'layout': {}};
#        }
#        const fig = Object.assign({}, figure, {
#            'layout': {
#                ...figure.layout,
#                'coloraxis': {
#                    ...figure.layout.coloraxis,
#                    cmin: rng[0], cmax: rng[1],
#                    colorscale: cs
#                }
#            }
#        });
#        return fig;
#    }
#    """,
#    Output('graph', 'figure'),
#    [Input('range-slider', 'value'), Input('colorscale','data')],
#    State('figure-store', 'data')
#)

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
