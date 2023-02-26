"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""

from astropy.io import fits
from dash import Dash, dcc, html, Input, Output, State
from skimage.measure import block_reduce

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import sunpy.visualization.colormaps as cm

import plotly.express as px

#------------------------------------------------------------------------------
# create app object

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

#------------------------------------------------------------------------------
# scatterplot data

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

available_countries = df['country'].unique()

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
    "height": 800,
    "paper_bgcolor": "black",
    "plot_bgcolor": "black",
})

#------------------------------------------------------------------------------

app.layout = html.Div([
    dcc.Graph(
        id='scatterplot-graph'
    ),
    dcc.Store(
        id='scatterplot-figure-store'
    ),
    'Country',
    dcc.Dropdown(available_countries, 'Canada', id='scatterplot-country-slider'),
    'Graph scale',
    dcc.RadioItems(
        ['linear', 'log'],
        'linear',
        id='scatterplot-log-button'
    ),
    dcc.Graph(
        id='graph'
    ),
    dcc.Store(
        id = 'figure-store',
        data = fig
    ),
    'Color Saturation',
    dcc.Slider(
        id = "zmax-slider",
        min = 1,
        max = 255,
        value = 255
    ),
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='figure-contents'
        )
    ])
])


@app.callback(
    Output('scatterplot-figure-store', 'data'),
    Input('scatterplot-country-slider', 'value')
)
def update_store_data(country):
    dff = df[df['country'] == country]
    return px.scatter(dff, x='year', y='pop')

app.clientside_callback(
    """
    function(figure, scale) {
        if(figure === undefined) {
            return {'data': [], 'layout': {}};
        }
        const fig = Object.assign({}, figure, {
            'layout': {
                ...figure.layout,
                'yaxis': {
                    ...figure.layout.yaxis, type: scale
                }
             }
        });
        return fig;
    }
    """,
    Output('scatterplot-graph', 'figure'),
    Input('scatterplot-figure-store', 'data'),
    Input('scatterplot-log-button', 'value')
)

app.clientside_callback(
    """
    function(zmax, figure) {
        if(figure === undefined) {
            return {'data': [], 'layout': {}};
        }
        const fig = Object.assign({}, figure, {
            'layout': {
                ...figure.layout,
                'coloraxis': {
                    ...figure.layout.coloraxis, cmax: zmax
                }
            }
        });
        return fig;
    }
    """,
    Output('graph', 'figure'),
    Input('zmax-slider', 'value'),
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
