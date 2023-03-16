# platform to play with plotting the cone model

import numpy as np
import plotly.express as px

#-----------------------------------
# create base cone

Nz = 20
Nr = 20

twopi = 2.0 * np.pi

D0 = np.sqrt(2.0)
z = np.linspace(0.0,D0,num=Nz)

alpha = z*z
b = 2.0*(alpha + 1.0)
c = alpha*(alpha - 2.0)

beta = (- b + np.sqrt(b*b - 4.0*c))/2.0

r = np.sqrt(beta)
rnorm = r / max(r)

# compute number of radial points for each z
Nrz = (rnorm*Nr).astype(np.int) + 1

# allocate aarays for points on surface
Npoints = np.sum(Nrz)
x0 = np.empty(Npoints)
y0 = np.empty(Npoints)
z0 = np.empty(Npoints)

# populate cone surface with points
i1 = 0
for j in np.arange(Nz):
    i2 = i1 + Nrz[j]
    phi = np.linspace(0.0,twopi,num=Nrz[j])
    x0[i1:i2] = r[j] * np.sin(phi)
    y0[i1:i2] = r[j] * np.cos(phi)
    z0[i1:i2] = z[j]
    print(80*'-'+f"\n{x0[i1:i2]} {y0[i1:i2]} {z0[i1:i2]}")
    i1 = i2

#-----------------------------------
