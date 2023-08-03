# This comes closer to what CAT actually does.
# compute either a gerono lemniscate or a bernoulli
# lemniscate using a parametric equation


import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------
def cone(radial_distance, angular_width, style=0):
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

z1, r1 = cone(1.0, 40.0, style = 0)
z2, r2 = cone(1.0, 40.0, style = 1)

fig = plt.figure(figsize=[12,4])

plt.fill_between(z1,-r1,y2=r1,color='b', alpha = 0.3)
plt.fill_between(z2,-r2,y2=r2,color='r', alpha = 0.3)

plt.show()