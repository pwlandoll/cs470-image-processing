from ij import IJ

imp = IJ.openImage("http://imagej.net/images/blobs.gif")
IJ.run(imp, "Histogram", "")

##How ImageJ does it, internally, has to do with the ImageStatisics class:
stats = imp.getStatistics()
print stats.histogram


##The histogram, area and mean are computed by default. Other values like the median need to be specified.
##To calculate other parameters, specify them by bitwise-or composition (see flags in Measurements):

stats = imp.getStatistics(Measurements.MEAN | Measurements.MEDIAN | Measurements.AREA)
print "mean:", stats.mean, "median:", stats.median, "area:", stats.area

##If we set a ROI to the image, then we are measuring only for the inside of the ROI. Here we set an oval ROI of radius 25 pixels, centered:

roi = OvalRoi(imp.width/2 - radius, imp.height/2 -radius, radius*2, radius*2)
imp.setRoi(roi)
stats = imp.getStatistics(Measurements.MEAN | Measurements.MEDIAN | Measurements.AREA)
print "mean:", stats.mean, "median:", stats.median, "area:", stats.area

##To display the histogram window ourselves, we may use the HistogramWindow class:
hwin = HistogramWindow(imp)

##... of which we may grab the image (the plot itself) and save it:

plotimage = hwin.getImagePlus()
IJ.save(plotimage, "/path/to/our/folder/plot.tif")
