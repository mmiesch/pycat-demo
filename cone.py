# platform to play with plotting the cone model

import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------
def cone(x,a):

    alpha = x*x
    gamma = a*a

    b = 2.0*(alpha + gamma)
    c = alpha*(alpha - 2.0 * gamma)

    beta = (- b + np.sqrt(b*b - 4.0*c))/2.0

    return np.sqrt(beta)

#-----------------------------------

N = 100

a1 = 1.0
a2 = 2.0

xmax = a1 * np.sqrt(2.0)
x1 = np.linspace(0.0,xmax,num=N)

xmax = a2 * np.sqrt(2.0)
x2 = np.linspace(0.0,xmax,num=N)

y1 = cone(x1,1.0)
y2 = cone(x2,2.0)

plt.plot(x1,y1,color='b')
plt.plot(x1,-y1,color='b')

plt.plot(x2,y2,color='r')
plt.plot(x2,-y2,color='r')

plt.show()


