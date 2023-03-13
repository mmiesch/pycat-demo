"""
Sample Bokeh app

Spin-up server with

```bash
bokeh serve --show app_mo_bokeh.py
```

"""
from random import randint
import numpy as np
from datetime import datetime as dt
from astropy.io import fits
from bokeh.io import curdoc
from bokeh.layouts import gridplot, column, layout
from bokeh.models import ColumnDataSource, Slider, Button, DatePicker
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.themes import Theme
from bokeh.plotting import figure


def load_cor():
    dir = "./CAT_images/2021122[12]/STEREO_A"
    # import glob
    # files=sorted(glob.glob(f"{dir}/*"))
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
    print(f"First files found :{files[0:2]}")
    imagelist = []
    for f in files:
        fname = dir + '/' + f
        hdu = fits.open(fname)[0]
        imagelist.append(hdu.data)

    images = np.array(imagelist)
    print(f"Shape of image data matrix: {images.shape}")
    vmin = np.min(images)
    vmax = np.max(images)
    norm = 255.0 / (vmax - vmin)

    scaled_images = (norm * (images - vmin)).astype(np.uint8)
    return scaled_images, norm, vmin, vmax, files


data, norm, vmin, vmax, files = load_cor()
data_size = data[0].shape[0]

image_data = data.copy()

# num_images = 70
# data_size = 512
# image_data = [[np.random.rand(data_size, data_size)] for i in range(num_images)]
# print(image_data[0].shape)
# Create plots and datasources
plot_size = 512
sources = {}
sources['COR3'] = ColumnDataSource(
    {'value': [image_data[0]]}
#    {'value': image_data[0]}
)
plots = figure(plot_width=plot_size,
               plot_height=plot_size,
               x_range=(0, data_size),
               y_range=(0, data_size),
               match_aspect=True,
               output_backend="webgl"
               )

plots.image('value',
            source=sources['COR3'],
            x=0,
            y=0,
            dw=data_size,
            dh=data_size,
            palette="Greys256")
plots.title.text = files[0].split("/")[-1]
color_mapper = LinearColorMapper(palette="Greys256", low=0, high=255)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0,1), title='Weight')
plots.add_layout(color_bar, 'right')


# slider = Slider(start=0, end=len(image_data), value=1, step=1, title="Image index")
frame_slider = Slider(start=0, end=len(data), value=1, step=1, title="Image index")
gamma_slider = Slider(start=0, end=5, value=1, step=.1, title="Gamma")
date_picker = DatePicker(value=dt.utcnow().strftime('%Y-%m-%d'),min_date="2021-01-01", max_date="2024-01-13")

def update_frame(attr, old, new):
    # sources['COR3'].data = {'value': image_data[slider.value]}
    print(f"{frame_slider.value}:{files[frame_slider.value].split('/')[-1]}")
    sources['COR3'].data = {'value': [image_data[frame_slider.value, :, :]]}
    print(image_data[frame_slider.value,:5,:5])
    plots.title.text=files[frame_slider.value].split("/")[-1]


frame_slider.on_change('value', update_frame)


# # recreate figure when gamma changes
# @app.callback(Output('data-store', 'data'),
#               Input('gamma-correction', 'value'))
# def update_figure_data(gamma):
#     data = (254*(norm*(images - vmin))**gamma).astype(np.uint8)
#     for idx, val in np.ndenumerate(data):
#         rgb[idx[0],idx[1],idx[2],:] = rgb_lasco[val,:]
#
#     return data

def update_gamma(attr, old, new):
    global image_data
    # sources['COR3'].data = {'value': image_data[slider.value]}
    gamma = gamma_slider.value
    print("Updating gamma")
    print(image_data[frame_slider.value, :5, :5])
    image_data = (254 * (norm * (data - vmin)) ** gamma).astype(np.uint8)
    print(image_data[frame_slider.value, :5, :5])
    sources['COR3'].data = {'value': [image_data[frame_slider.value, :, :]]}


gamma_slider.on_change('value', update_gamma)



def animate_update():
    global data
    idx = frame_slider.value + 1
    if idx > len(data)-1:
        idx = 0
    frame_slider.value = idx


callback_id = None


def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)


button = Button(label='► Play', width=60)
button.on_event('button_click', animate)

# Document
curdoc().add_root(layout([date_picker,button],column(plots, frame_slider,gamma_slider)))
#curdoc().add_root(column(plots, frame_slider, gamma_slider, button))

#curdoc().theme = 'dark_minimal'
curdoc().theme = Theme('theme.yaml')
curdoc().title='CAT tool'
