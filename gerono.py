# This comes closer to what CAT actually does.
# compute either a gerono lemniscate or a bernoulli
# lemniscate using a parametric equation


import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------
def cone(radial_distance, angular_width, style=0):
    # the names of the arguments here follow the terminology
    # used for CAT

    N = 500

    zmax = radial_distance

    zpt = zmax/5.0
    tatz = np.arccos(0.2)

    beta = np.radians(0.5*angular_width)
    ymax = zpt * np.tan(beta)

    c1 = zmax
    c2 = ymax / (np.cos(tatz)*np.sin(tatz))
    c3 = 1.0

    t = np.linspace(0,np.pi/2,num=N+1,endpoint=False)[1:]

    z = c1 * np.cos(t)
    if style > 0:
        z /= 1.+(np.sin(t)**2)

    r = c2 * np.cos(t) * np.sin(t)
    if style > 0:
        r /= 1.+(np.sin(t)**2)

    return z, r

#-----------------------------------

z1, r1 = cone(1.0, 40.0, style = 0)
z2, r2 = cone(1.0, 40.0, style = 1)

fig = plt.figure(figsize=[4,12])

plt.fill(r1,z1,color='b', alpha = 0.3)
plt.fill(r2,z2,color='r', alpha = 0.3)

reflect = True

if reflect:
    plt.fill(-r1,z1,color='b', alpha = 0.3)
    plt.fill(-r2,z2,color='r', alpha = 0.3)

plt.show()

