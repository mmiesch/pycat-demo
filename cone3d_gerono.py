import numpy as np
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
import plotly.graph_objects as go

#-----------------------------------
def cone(radial_distance = 1.0, angular_width = 60.0, style=0):
    # the names of the arguments here follow the terminology
    # used for CAT

    # style = 0 is Gerono lemniscate
    # style = 1 is Bernoulli lemniscate

    N = 500

    zmax = radial_distance

    beta = np.radians(0.5*angular_width)
    rmax = 0.2 * zmax * np.tan(beta)

    tatz = np.arccos(0.2)
    c2 = rmax / (np.cos(tatz)*np.sin(tatz))

    t = np.linspace(0,np.pi/2,num=N+1,endpoint=False)[1:]

    z = zmax * np.cos(t)
    if style > 0:
        z /= 1.+(np.sin(t)**2)

    r = c2 * np.cos(t) * np.sin(t)
    if style > 0:
        r /= 1.+(np.sin(t)**2)

    return z, r

#-----------------------------------
z, r = cone()

# Create a 3D grid
theta = np.linspace(0, 2*np.pi, 100)
Z, Theta = np.meshgrid(z, theta)
R = np.tile(r, (len(theta), 1))

# Convert to Cartesian coordinates
X = R * np.cos(Theta)
Y = R * np.sin(Theta)

# Create a scalar field: distance from the surface (negative inside, positive outside)
# We'll use a simple radial distance from the (z, r) surface

# Flatten the surface points
points_surface = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))

# Define a 3D grid for the isosurface
x = np.linspace(X.min()-0.1, X.max()+0.1, 50)
y = np.linspace(Y.min()-0.1, Y.max()+0.1, 50)
z_grid = np.linspace(Z.min()-0.1, Z.max()+0.1, 50)
Xg, Yg, Zg = np.meshgrid(x, y, z_grid, indexing='ij')

# For each grid point, compute the minimum distance to the surface
grid_points = np.column_stack((Xg.ravel(), Yg.ravel(), Zg.ravel()))
tree = cKDTree(points_surface)
distances, _ = tree.query(grid_points)
scalar_field = distances.reshape(Xg.shape)

lighting_settings = dict(
    ambient=0.2,    # less ambient for more contrast
    diffuse=0.9,    # strong diffuse for clear shape
    specular=0.6,   # high specular for shiny highlights
    roughness=0.3,  # lower roughness for sharper highlights
    fresnel=0.5     # increase fresnel for edge highlights
)

# Plot the isosurface at a small value (close to the surface)
fig = go.Figure(data=go.Isosurface(
    x=Xg.flatten(),
    y=Yg.flatten(),
    z=Zg.flatten(),
    value=scalar_field.flatten(),
    isomin=0.0,
    isomax=0.05,
    surface_count=1,
    caps=dict(x_show=False, y_show=False, z_show=False),
    colorscale='Blackbody',
    opacity=1.0,
    lighting=lighting_settings,
    showscale=False
))

fig.update_layout(
    scene = dict(
       zaxis = dict(visible=False),
       yaxis = dict(visible=False),
       xaxis = dict(visible=False),
    )
)

fig.show()