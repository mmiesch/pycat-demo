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

surface = dict(show=True, count=15, fill=0.2, pattern='all')

# Improve appearance: smooth lighting, higher resolution, better color, and opacity
import plotly.colors

# Use a perceptually uniform colorscale
colorscale = plotly.colors.sequential.Viridis

# Optionally, set opacity and lighting
surface_count = 2  # show both sides of the cone

lighting_settings = dict(
    ambient=0.2,    # less ambient for more contrast
    diffuse=0.9,    # strong diffuse for clear shape
    specular=1.0,   # high specular for shiny highlights
    roughness=0.3,  # lower roughness for sharper highlights
    fresnel=0.5     # increase fresnel for edge highlights
)


isosurface_kwargs = dict(
    x = x.flatten(),
    y = y.flatten(),
    z = z.flatten(),
    value = values.flatten(),
    isomin = 0.0,
    isomax = 0.0,
    surface_count = surface_count,
    #colorscale = colorscale,
    colorscale = 'Blackbody',  # Using Blackbody for a more dramatic effect
    showscale = True,
    opacity = 0.7,
    caps=dict(x_show=False, y_show=False, z_show=False),
    lighting = lighting_settings
)

fig = go.Figure(data=go.Isosurface(**isosurface_kwargs))

#fig = go.Figure(data=go.Isosurface(
#    x = x.flatten(),
#    y = y.flatten(),
#    z = z.flatten(),
#    value = values.flatten(),
#    isomin = 0.0,
#    isomax = 0.0,
#    surface_count = 1,
#    colorscale='Blackbody',
#    showscale = False
#))

fig.update_layout(
    scene = dict(
       zaxis = dict(visible=False),
       yaxis = dict(visible=False),
       xaxis = dict(visible=False),
       #xaxis = dict(showticklabels=False,
       #             title='')
    )
)

frames = []
num_frames = 60
for i in range(num_frames):
    angle = 2 * np.pi * i / num_frames
    camera = dict(
        eye=dict(
            x=2 * np.cos(angle),
            y=2 * np.sin(angle),
            z=0.7
        )
    )
    frames.append(go.Frame(layout=dict(scene_camera=camera)))

fig.frames = frames

fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="Rotate",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(duration=0.01, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=0)
                        )
                    ]
                )
            ]
        )
    ]
)

# Remove colorbar (showscale) and the Rotate button
fig.update_traces(showscale=False)
fig.update_layout(updatemenus=[])

# Save animation as a movie file (e.g., mp4)
import plotly.io as pio

# Plotly does not natively support saving animated figures as mp4 directly.
# You can save the animation as a gif using Kaleido, then convert to mp4 with ffmpeg.
# Here's how to save as gif (requires plotly>=5.9.0 and kaleido):

# Uncomment the following lines if you want to save as gif:
#pio.write_image(fig, "cone3d_animation.gif", format="gif", scale=2, fps=20)

# Save each frame as a PNG image
#frame_images = []
#for i, frame in enumerate(fig.frames):
#    # Combine static traces (fig.data) with dynamic traces (frame.data)
#    all_data = list(fig.data) + list(frame.data)
#    temp_fig = go.Figure(data=all_data, layout=fig.layout)
#    image_path = f'frame_{i:03d}.png'
#    pio.write_image(temp_fig, image_path)
#    frame_images.append(image_path)
#    temp_fig = go.Figure(data=frame.data, layout=frame.layout)
#    # Apply any layout updates from the main figure that are not in the frame
#    temp_fig.update_layout(fig.layout)
#    image_path = f'frame_{i:03d}.png'
#    pio.write_image(temp_fig, image_path)
#    frame_images.append(image_path)

fig.show()
