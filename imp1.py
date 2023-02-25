"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""

from astropy.io import fits
from dash import Dash, dcc, html, Input, Output
from skimage.measure import block_reduce

import numpy as np
import pandas as pd
import json

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

fig = px.imshow(image_data,
                zmin=0,
                zmax=255
                )
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
        id='graph',
        figure = px.imshow(image_data,
                zmin=0,
                zmax=255
                )
    ),
    dcc.Store(
        id='figure-store',
        data=fig
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

@app.callback(
    Output('graph', 'figure'),
    Input('figure-store', 'data')
)
def update_figure(newfig):
    return newfig

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


@app.callback(
    Output('figure-contents', 'children'),
    Input('scatterplot-figure-store', 'data')
)
def generated_px_figure_json(data):
    return '```\n'+json.dumps(data, indent=2)+'\n```'


if __name__ == '__main__':
    app.run_server(debug=True)
