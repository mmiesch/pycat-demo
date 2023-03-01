# platform to play with plotting the cone model

import numpy as np
import matplotlib.pyplot as plt


#-----------------------------------
def cone(a, ys):

    xmax = a * np.sqrt(2.0)
    x = np.linspace(0.0,xmax,num=N)

    alpha = x*x
    gamma = a*a

    b = 2.0*(alpha + gamma)
    c = alpha*(alpha - 2.0 * gamma)

    beta = (- b + np.sqrt(b*b - 4.0*c))/2.0

    y = ys * np.sqrt(beta)

    return x, y

#-----------------------------------

N = 100

x1, y1 = cone(1.0, 1.0)
x2, y2 = cone(2.0, 1.0)
x3, y3 = cone(2.0, 0.3)

plt.plot(x1,y1,color='b')
plt.plot(x1,-y1,color='b')

plt.plot(x2,y2,color='r')
plt.plot(x2,-y2,color='r')

plt.plot(x3,y3,color='black')
plt.plot(x3,-y3,color='black')

plt.show()


