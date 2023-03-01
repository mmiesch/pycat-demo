# platform to play with plotting the cone model

import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------
def cone(a, rs):

    zmax = a * np.sqrt(2.0)
    z = np.linspace(0.0,zmax,num=N)

    alpha = z*z
    gamma = a*a

    b = 2.0*(alpha + gamma)
    c = alpha*(alpha - 2.0 * gamma)

    beta = (- b + np.sqrt(b*b - 4.0*c))/2.0

    r = rs * np.sqrt(beta)

    return z, r

#-----------------------------------

N = 500

z1, r1 = cone(1.0, 1.0)
z2, r2 = cone(2.0, 1.0)
z3, r3 = cone(2.0, 0.3)

fig = plt.figure(figsize=[4,12])

plt.fill(r1,z1,color='b', alpha = 0.3)
plt.fill(r2,z2,color='r', alpha = 0.3)
plt.fill(r3,z3,color='black', alpha = 0.3)

reflect = True

if reflect:
    plt.fill(-r1,z1,color='b', alpha = 0.3)
    plt.fill(-r2,z2,color='r', alpha = 0.3)
    plt.fill(-r3,z3,color='black', alpha = 0.3)

plt.show()

