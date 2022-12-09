from dash import Dash, dcc, html

app = Dash(__name__)

slider = dcc.Slider(min=1, max=10, step=1, value=1)

app.layout = html.Div(slider, style={"margin": 30})

if __name__ == "__main__":
    app.run(debug=True)
