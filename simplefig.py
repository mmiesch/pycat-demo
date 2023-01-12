from astropy.io import fits
from datetime import date
from dash import Dash, dcc, html, Input, Output
#from skimage import data

import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import sunpy.visualization.colormaps as cm

EXPLAINER = """a simple animated figure to work with plotly"""

def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

def matplotlib_to_rgb(cmap, ncolors):
    h = 1.0/(ncolors-2)

    rgbmap = np.zeros((ncolors,3), dtype=np.uint8)

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        rgbmap[k,:] = (C[0], C[1], C[2])

    return rgbmap

#------------------------------------------------------------------------------
# define images

# arbitrary sequence of 10 STEREO L3 images
dir = '/home/mark.miesch/Products/image_processing/ATBD/data/stereo_a/L3_2012_09'
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

imagelist = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    imagelist.append(hdu.data)

images = np.array(imagelist)

#------------------------------------------------------------------------------
# define color scales
cmap_lasco = plt.get_cmap('soholasco2')
cmap_stereo = plt.get_cmap('stereocor2')

cscale_lasco = matplotlib_to_plotly(cmap_lasco, 255)
cscale_stereo = matplotlib_to_plotly(cmap_stereo, 255)

rgb_lasco = matplotlib_to_rgb(cmap_lasco, 255)
rgb_stereo = matplotlib_to_rgb(cmap_stereo, 255)

names = ["LASCO/C2","STEREO/COR2"]

scaledict = {names[0]: cscale_lasco,
             names[1]: cscale_stereo}

#for s in cscale_lasco:
#    print(s)

#--------------------------------------------------
# convert to rgb

rgb = np.zeros((images.shape[0],images.shape[1],images.shape[2],3),
                dtype=np.uint8)

h = 1.0/254.0

rgbmap = rgb_lasco

vmin = np.min(images)
vmax = np.max(images)
norm = 254.0/(vmax - vmin)
for k in np.arange(rgb.shape[0]):
    cidx = np.uint8(norm*(images[k,:,:] - vmin))
    for i in np.arange(cidx.shape[0]):
      for j in np.arange(cidx.shape[1]):
        rgb[k,i,j,0] = rgbmap[cidx[i,j],0]
        rgb[k,i,j,1] = rgbmap[cidx[i,j],1]
        rgb[k,i,j,2] = rgbmap[cidx[i,j],2]

#------------------------------------------------------------------------------
# plot figure
fig = px.imshow(rgb, animation_frame=0,
                binary_string = True,
                labels={"animation_frame":"frame"},
                height=800
                )

fig.update_traces({
      "showscale": False,
      "hovertemplate": 'x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>',
    },
    selector = {'type':'heatmap'}
)

fig.update_layout({
    "xaxis": {
        "scaleanchor":"y",
        "showticklabels": False,
        "visible": False,
    },
    "yaxis": {
        "visible": False
    },
    "font": {
        "size":30,
        "color":"goldenrod",
        "family": "Arial Black"
        },
    "paper_bgcolor": "black",
# this seems to mess up the animation
#    "margin": {
#        't': 10,
#        'b': 10,
#        'l': 10,
#        'r': 10
#    },
    "showlegend": False,
})

fig.update_layout(transition = {'duration': 0})

fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 0
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 0

#fig.update_traces(colorscale=cscale_lasco)

app = Dash()

app.layout = dbc.Container(
    [
        html.H1("Simple DASH demo"),
        dcc.Markdown(EXPLAINER),
        html.Hr(),
        dbc.Card(
            [dcc.Graph(
                figure = fig,
                id = "image-plot",
                config={"displayModeBar": False},
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
