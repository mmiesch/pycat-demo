from dash import Dash, dcc, html

app = Dash(__name__)

slider = html.Div(
  children=[
    html.Label("Frame selection", htmlFor="frame-slider"),
    dcc.Slider(min=1, max=10, step=1, value=1, id="frame-slider")
  ]
)

app.layout = html.Div(
    children=[
      html.H1(children="Dash Demo",),
      html.P(
        children="Demo of Plotly DASH relevant to pyCAT",
      ),
      slider
    ],
    style={"margin": 30}
)

if __name__ == "__main__":
    app.run(debug=True)
