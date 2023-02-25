"""
This starts out as just an example where a clientside callback works.

Then the intention is to modify it to do image processing on a single image.
"""
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import json

import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

available_countries = df['country'].unique()

app.layout = html.Div([
    dcc.Graph(
        id='graph'
    ),
    dcc.Store(
        id='figure-store'
    ),
    'Indicator',
    dcc.Dropdown(
        {'pop' : 'Population', 'lifeExp': 'Life Expectancy', 'gdpPercap': 'GDP per Capita'},
        'pop',
        id='data-slider'
    ),
    'Country',
    dcc.Dropdown(available_countries, 'Canada', id='country-slider'),
    'Graph scale',
    dcc.RadioItems(
        ['linear', 'log'],
        'linear',
        id='log-button'
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
    Output('figure-store', 'data'),
    Input('data-slider', 'value'),
    Input('country-slider', 'value')
)
def update_store_data(indicator, country):
    dff = df[df['country'] == country]
    return px.scatter(dff, x='year', y=str(indicator))


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
    Output('graph', 'figure'),
    Input('figure-store', 'data'),
    Input('log-button', 'value')
)


@app.callback(
    Output('figure-contents', 'children'),
    Input('figure-store', 'data')
)
def generated_px_figure_json(data):
    return '```\n'+json.dumps(data, indent=2)+'\n```'


if __name__ == '__main__':
    app.run_server(debug=True)
