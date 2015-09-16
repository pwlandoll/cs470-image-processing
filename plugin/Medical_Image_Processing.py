#from ij import IJ
import urllib2

def readURLList(filename):
	f, images = open(filename, 'r'), []
	for line in f:
		images.append(urllib2.urlopen(line))
	f.close()
	return images

urls = readURLList("samplelist.txt")
