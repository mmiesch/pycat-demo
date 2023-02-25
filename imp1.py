"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""
from dash import Dash, dcc, html, Input, Output
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
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='scatterplot-figure-contents'
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


@app.callback(
    Output('scatterplot-figure-contents', 'children'),
    Input('scatterplot-figure-store', 'data')
)
def generated_px_figure_json(data):
    return '```\n'+json.dumps(data, indent=2)+'\n```'


if __name__ == '__main__':
    app.run_server(debug=True)
