from timeit import repeat
import pydicom as dicom
import sys
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

import os

# Defining path of Dicom images
path="./Head"
ct_images=os.listdir(path)

# Load the Dicom files
slices = [dicom.read_file(path+'/'+s,force=True) for s in ct_images]

# ensure they are in the coorect order
slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])

#create 3D  array
img_shape = list(slices[0].pixel_array.shape)
img_shape.append(len(slices))
volume3d=np.zeros(img_shape)

#fill 3D array with  the images from the files
for i,s in enumerate(slices):
    array2D=s.pixel_array
    volume3d[:,:,i]= array2D


def play(array):
    # Defining axial Plane plot
    fig = plt.figure(1)
    im = plt.imshow(array[:,:,0],cmap='gray')
    plt.title("Axial")
    # The function to call at each frame with next value in frames
    def animate(i): 
        im.set_array(array[:,:,i])
        im.autoscale()
        return [im]
    anim = animation.FuncAnimation(fig, animate, frames=img_shape[2], interval=12, blit=True)

    # Defining Sagital Plane plot
    fig2 = plt.figure(2)
    im2 = plt.imshow((array[:,0,:]),cmap='gray')
    plt.title("Sagital")
    # The function to call at each frame with next value in frames
    def animate2(i):
        im2.set_array((array[:,i,:]))
        im2.autoscale()
        return [im2]
    anim2 = animation.FuncAnimation(fig, animate2, frames=img_shape[1], interval=12, blit=True)

    # Defining Coronal Plane plot
    fig3 = plt.figure(3)
    im3 = plt.imshow((array[0,:,:]),cmap='gray')
    plt.title("Coronal")
    # The function to call at each frame with next value in frames
    def animate3(i):
        im3.set_array((array[i,:,:]))
        im3.autoscale()
        return [im3]
    anim3 = animation.FuncAnimation(fig, animate3, frames=img_shape[0], interval=12, blit=True)

    plt.show()

# call play function to play in axial / Sagital / Coronal planes   
play(volume3d)