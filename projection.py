# platform to play with plotting the cone model

import numpy as np
import pandas as pd
import plotly.express as px

#-----------------------------------
# create base cone

Nz = 40
Nr = 40

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
Nrz = (rnorm*Nr).astype(np.int32) + 1

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
#    print(80*'-'+f"\n{x0[i1:i2]} {y0[i1:i2]} {z0[i1:i2]}")
    i1 = i2

#-----------------------------------
# Now rotate cone by specified colatitude and longitude

# these are the input values
colatitude = 30.0
longitude = 0.0

theta = np.radians(colatitude)
phi = np.radians(longitude)

# We only really need yprime and zprime
# no need to compute xprime

st = np.sin(theta)
ct = np.cos(theta)
sp = np.sin(phi)
cp = np.cos(phi)

yprime = ct*sp*x0 + cp*y0 + st*sp*z0
zprime = -st*x0 + ct*z0

#-----------------------------------
# compute ymin, ymax for each z

df = pd.DataFrame({'z':np.around(zprime,2),'y':yprime})
df = df.groupby(by='z',as_index=False,sort=True).agg({'y':['min','max']})

print(df.to_string())

print(df['min'])

#-----------------------------------

#fig = px.line(df, x='y',y='z')

#fig.show()