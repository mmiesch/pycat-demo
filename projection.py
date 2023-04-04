# platform to play with plotting the cone model

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from scipy.spatial import ConvexHull

#-----------------------------------
# create base cone

Nz = 400
Nr = 200

twopi = 2.0 * np.pi

z = np.linspace(0.0,1.0,num=Nz)

alpha = z*z
b = 2.0*alpha + 1.0
c = alpha*(alpha - 1.0)

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
    i1 = i2

#-----------------------------------
# set cone parameters

latitude = 45.0
longitude = 90.0
psi = 20.0
a = 2.0

#-----------------------------------
# scale with height and cone angle

rs = np.tan(np.radians(psi))
d = np.sqrt(2.0) * a

x0 = rs * d * x0
y0 = rs * d * y0
z0 = d * z0

#-----------------------------------
# Now rotate cone by specified colatitude and longitude

theta = np.radians(90.0 - latitude)
phi = np.radians(longitude)

# We only really need yprime and zprime
# no need to compute xprime

st = np.sin(theta)
ct = np.cos(theta)
sp = np.sin(phi)
cp = np.cos(phi)

yprime = ct*sp*x0 + cp*y0 + st*sp*z0
zprime = ct*z0 - st*x0

#-----------------------------------
# two plot options: set to 1 for line plot or 2 for contour plot
ptype = 3

if ptype == 1:

    #-----------------------------------
    # compute ymin, ymax for each z

    dz = .02
    hdz = 0.5 * dz
    zmin = np.min(zprime)
    zmax = np.max(zprime)
    imin = np.where(zprime == zmin)
    imax = np.where(zprime == zmax)
    yzmin = yprime[imin][0]
    yzmax = yprime[imax][0]

    bins = np.arange(zmin,zmax-dz,dz)
    idx = np.digitize(zprime, bins)
    zbin = bins[idx-1] + hdz

    # make sure first and last points are part of the array
    zz = np.concatenate([[zmin],zbin,[zmax]])
    yy = np.concatenate([[yzmin],yprime,[yzmax]])

    N=len(yy)
    for i in np.arange(0,10):
        print(f"{zz[i]} {yy[i]}")
    for i in np.arange(N-10,N):
        print(f"{zz[i]} {yy[i]}")

    df = pd.DataFrame({'z':zz,'y':yy})
    df = df.groupby(by='z',as_index=False,sort=True).agg({'y':['min','max']})
    df.columns = df.columns.droplevel(0)
    df.columns = ['z','ymin','ymax']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ymin'],y=df['z'],
        mode='lines', line = {'color':'blue'}))
    fig.add_trace(go.Scatter(x=df['ymax'],y=df['z'],
        mode='lines', line = {'color':'blue'}))
    fig.show()
elif ptype == 2:

    fig = go.Figure(go.Histogram2dContour(
            x=yprime, y=zprime,
            line = dict(
                smoothing=1,
                width=10
            ),
            contours = dict(
                start=0.5,
                end=0.5,
                coloring = "lines"
            )))
    fig.show()
else:

    points = np.zeros((Npoints,2))
    points[:,0] = zprime
    points[:,1] = yprime

    hull = ConvexHull(points)

    for simplex in hull.simplices:
        plt.plot(points[simplex,0], points[simplex,1])
    plt.show()

