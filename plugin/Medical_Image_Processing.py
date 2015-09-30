from ij import IJ
from pyper import *
import os

def readURLList(filename):
	f, images = open(filename, 'r'), []
	for line in f:
		images.append(IJ.openImage(line))
	f.close()
	return images

filename = "C:\Users\Peter\Documents\GitHub\cs470-image-processing\plugin\samplelist.txt"

for image in readURLList(filename):
	image.show()

def runRScript():
	r = R()
	output = r('a <- 5; print(a)')
	return output

