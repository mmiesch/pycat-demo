from datetime import date
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

EXPLAINER = """This is a simple demo of a DASH application that is relevant for
pyCAT.  It starts from a dash example and css template obtained from here:
https://github.com/tcbegley/dash-bootstrap-css"""

# Note: the original example from the dash-bootstrap-css repo has lots
# of other useful examples, like a checklist, a range slider, and
# selectors for single dates or date ranges.  Worth going back to as
# we make this more sophisticated.

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
    ],
    id="container",
    style={"marginBottom": "300px", "marginTop": "20px"},
    className="dash-bootstrap",
)

if __name__ == "__main__":
    app.run_server(debug=True)
