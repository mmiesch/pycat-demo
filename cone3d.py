# platform to play with plotting the cone model

import numpy as np
import plotly.graph_objects as go

#-----------------------------------
N = 500

x, y, z = np.mgrid[0:3:80j, -2:2:80j, -2:2:80j]

a = 2.0
rs = 0.8

alpha = x*x
beta = (y*y + z*z)/(rs*rs)
gamma = a*a

values = np.power((alpha + beta),2) - 2*gamma * (alpha - beta)

fig = go.Figure(data=go.Isosurface(
    x = x.flatten(),
    y = y.flatten(),
    z = z.flatten(),
    value = values.flatten(),
    isomin = 0.0,
    isomax = 0.0,
    surface_count = 1,
    colorscale='Blackbody',
    showscale = False
))

fig.update_layout(
    scene = dict(
       zaxis = dict(visible=False),
       yaxis = dict(visible=False),
       xaxis = dict(showticklabels=False,
                    title='')
    )
)

fig.show()
