from datetime import date
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
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

#def matplotlib_to_plotly(cmap, pl_entries):
#    h = 1.0/(pl_entries-1)
#    pl_colorscale = []
#
#    for k in range(pl_entries):
#        C = map(np.uint8, np.array(cmap(k*h)[:3])*255)
#        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])
#
#    return pl_colorscale

# sample image for plotting
image = data.shepp_logan_phantom()

#cmap = get_cmap('soholasco2')
cmap = plt.get_cmap('stereocor2')

#cscale = matplotlib_to_plotly(cmap, 255)

app = Dash()

app.layout = dbc.Container(
    [
        html.H1("Simple DASH demo"),
        dcc.Markdown(EXPLAINER),
        html.Hr(),
        dbc.Card(
            [
                html.H4("Plot options", className="card-title"),
                dcc.Dropdown(
                    options=[
                        {"label": f"Option {i}", "value": i} for i in range(10)
                    ]
                ),
            ],
            body=True,
            className="mb-3",
        ),
        dbc.Card(
            [
                html.H4("Frame selection", className="card-title"),
                dcc.Slider(
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
                figure={
                    "data": [
                        {
                            "z": image,
                            "type": "heatmap",
                            "showscale": False,
                            "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
                            #"color_continuous_scale": cmap
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
                },
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

if __name__ == "__main__":
    app.run_server(debug=True)
