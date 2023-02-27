"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""

from astropy.io import fits
#from dash import Dash, dcc, html, Input, Output, State
from dash import dcc
from dash_extensions.enrich import Output, DashProxy, Input, State, MultiplexerTransform, html
from skimage.measure import block_reduce

import matplotlib.pyplot as plt
import numpy as np
import json
import sunpy.visualization.colormaps as cm

import plotly.express as px

#------------------------------------------------------------------------------
# create app object

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DashProxy(__name__, external_stylesheets=external_stylesheets,transforms=[MultiplexerTransform()])

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

fullres = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    fullres.append(hdu.data)
fullres = np.array(fullres)

print(f"fullres {fullres.shape}")

vmin = np.min(fullres)
vmax = np.max(fullres)
norm = 1.0 / (vmax-vmin)

# downsample to 512 x 512
# and render as uint8
images = []
cval = np.nanmin(fullres)
for n in np.arange(fullres.shape[0]):
    im = block_reduce(fullres[n,:,:],
            block_size = 2,
            func = np.nanmedian,
            cval = cval)
    image_data = (254*norm*(im - vmin)).astype(np.uint8)
    images.append(image_data)
images = np.array(images)

# reference image
ref_frame = 4
image_data = images[ref_frame,:,:]

print(f"Image range {np.min(image_data)} {np.max(image_data)}")
print(f"Image size {image_data.shape}")

# buffer for movie data
rgbimages = np.zeros((images.shape[0],images.shape[1],images.shape[2],3),
                dtype=np.uint8)

#------------------------------------------------------------------------------
# color table

def matplotlib_to_plotly(cmap, ncolors):
    h = 1.0/(ncolors-1)
    pl_colorscale = []

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

def plotly_to_rgb(cscale):
    ncolors = len(cscale)
    rgbmap = np.zeros((ncolors,3), dtype=np.uint8)
    for k in range(ncolors):
        s = cscale[k][1]
        rgbmap[k,:] = np.uint8(s[s.find('(')+1:s.find(')')].split(','))
    return rgbmap

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
    dcc.Store(
        id = "color-range",
        data = (0,255)
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
    html.Button("Animation",
        id = "animate-button",
        style = {"color":"DarkBlue",
                 "backgroundColor":"goldenrod",
                 "height":60},
    ),
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='figure-contents'
        )
    ])
], style={"font-size":30})

@app.callback(
    Output("colorscale", "data"),
    Input("gamma-slider","value"),
    State("colorscale","data")
)
def update_colorscale(gamma, newcs):
    newidx = (255*np.power(nidx,(1.0/gamma))).astype(np.uint8)
    for i in np.arange(len(newcs)):
        newcs[i][1] = cscale_lasco[newidx[i]][1]
    return newcs

@app.callback(
    Output("color-range","data"),
    Input("range-slider","value")
)
def update_color_range(rng):
    return (rng[0],rng[1])

@app.callback(
    Output("figure-store", "data"),
    Input("colorscale","data"),
    State("figure-store","data")
)
def update_colorscale(newcs, figure):
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
    Input('color-range', 'data'),
    Input('figure-store', 'data')
)

@app.callback(
    Output('graph','figure'),
    Input('animate-button','n_clicks'),
    State('colorscale','data'),
    State('color-range','data')
)
def make_movie(nclicks,cscale,rng):

    rgbmap = plotly_to_rgb(cscale)

    for idx, val in np.ndenumerate(images):
        rgbimages[idx[0],idx[1],idx[2],:] = rgbmap[val,:]

    fig = px.imshow(rgbimages, animation_frame=0,
                binary_string = True,
                labels={"animation_frame":"frame"},
                height=600,
                zmin = rng[0],
                zmax = rng[1]
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

    return fig

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
