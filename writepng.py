"""
This builds off of app3.py but it's an attempt to store the plot data in a buffer and only modify the data component of the figure, fig.frames[0].data[:].z), instead of redrawing the entire figure each time.  Currently I only know how to go about this with binary_string=False.  But even then it does not seem to be working.
"""

from astropy.io import fits
from skimage.io import imsave
import numpy as np
import matplotlib.pyplot as plt
import sunpy.visualization.colormaps as cm

#------------------------------------------------------------------------------
def matplotlib_to_rgb(cmap, ncolors):
    h = 1.0/(ncolors-2)

    rgbmap = np.zeros((ncolors,3), dtype=np.uint8)

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        rgbmap[k,:] = (C[0], C[1], C[2])

    return rgbmap

def matplotlib_to_plotly(cmap, ncolors):
    h = 1.0/(ncolors-1)
    pl_colorscale = []

    for k in range(ncolors):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

#------------------------------------------------------------------------------
# load image data
# arbitrary sequence of 10 STEREO L3 images
dir = './data'
files = [
    "STEREOA_L3_2012_09_16_113900.fts",
    "STEREOA_L3_2012_09_16_115400.fts",
    "STEREOA_L3_2012_09_16_122400.fts",
    "STEREOA_L3_2012_09_16_123900.fts",
    "STEREOA_L3_2012_09_16_125400.fts",
    "STEREOA_L3_2012_09_16_132400.fts",
    "STEREOA_L3_2012_09_16_133900.fts",
    "STEREOA_L3_2012_09_16_135400.fts",
    "STEREOA_L3_2012_09_16_142400.fts",
    "STEREOA_L3_2012_09_16_143900.fts"
]

imagelist = []
for f in files:
    fname = dir + '/' + f
    hdu = fits.open(fname)[0]
    imagelist.append(hdu.data)

images = np.array(imagelist)

#------------------------------------------------------------------------------
# load scaled data

vmin = np.min(images)
vmax = np.max(images)

norm = 1.0/(vmax-vmin)

# used to reset the color scale
baseidx = np.arange(256)

#------------------------------------------------------------------------------
# lasco/C2 color scale

cmap_lasco = plt.get_cmap('soholasco2')
rgb_lasco = matplotlib_to_rgb(cmap_lasco, 255)
cscale_lasco = matplotlib_to_plotly(cmap_lasco,255)

#------------------------------------------------------------------------------
# generate original figure
# for performance, express the data as a 4D array, called rgb
# This includes the 3D data, expressed as a byte array (time,x,y),
# and a 4th dimension for the rgb values for each pixel value 0 to 254
# This allows you to use binary_string = True in the call to imshow,
# which greatly speeds up the rendering

# buffer for storing
rgb = np.zeros((images.shape[0],images.shape[1],images.shape[2],3),
                dtype=np.uint8)

basedata = (254*norm*(images - vmin)).astype(np.uint8)
for idx, val in np.ndenumerate(basedata):
    rgb[idx[0],idx[1],idx[2],:] = rgb_lasco[val,:]

#------------------------------------------------------------------------------

outdir = './data/images/'

nt = images.shape[0]
nx = images.shape[1]
ny = images.shape[2]

im = np.zeros((nx,ny,3))

for i in np.arange(nt):
    im[:,:,:] = rgb[i,:,:,:]
    filename = outdir + f"image{i}.png"
    imsave(filename, im)

