import os
from ij import IJ, ImagePlus
from ij.gui import GenericDialog
  
def run():
  srcDir = IJ.getDirectory("Input_directory")
  if not srcDir:
    return
  dstDir = IJ.getDirectory("Output_directory")
  if not dstDir:
    return

  gd = GenericDialog("Process Folder")
  gd.addStringField("File_extension", "")
  gd.addStringField("File_name_contains", "")
  gd.addCheckbox("Keep directory structure when saving", True)
  gd.showDialog()
  if gd.wasCanceled():
    return
  ext = gd.getNextString()
  containString = gd.getNextString()
  keepDirectories = gd.getNextBoolean()
  for root, directories, filenames in os.walk(srcDir):
    for filename in filenames:
    	#hidden file
       if filename.endswith(".db"):
         continue
      # Check for file extension
      #if not filename.endswith(ext):
        #continue
      # Check for file name pattern
     # if containString not in filename:
        #continue
       process(srcDir, dstDir, root, filename, keepDirectories)

     
def process(srcDir, dstDir, currentDir, fileName, keepDirectories):
  print "Processing:"
   
  # Opening the image
  print "Open image file", fileName
  imp = IJ.openImage(os.path.join(currentDir, fileName))
  #opens the image. removed imp.close() so image opens
  imp.show()
   
  # Put your processing commands here
  # Added code to output width, height, title, stack size, etc.. 
  #Follow this example if needed
  #from ij import IJ
  #imp = IJ.getImage()
  #statistics
  #print imp.getStatistics()
  
  width = imp.getWidth()
  height = imp.getHeight()
  print ""
  print "title:", imp.getTitle()
  print "width:", width
  print "height:", height
  print "stack size:", imp.getStackSize()

  #return bit depth
  bitDepth = imp.getBitDepth()
  type = "RGB"
  if bitDepth!=24:
   type = str(bitDepth)+"-bit"
   print "type:", type

  #return if composite or hyperstack
  composite = imp.isComposite()
  hyperstack = imp.isHyperStack()
  print "composite:", composite
  print "hyperstack:", hyperstack
  if composite or hyperstack:
    print "channels:", imp.getNChannels()
    print "slices:", imp.getNSlices()
    print "frames:", imp.getNFrames()

  #returns calibration
  cal = imp.getCalibration()
  scaled = cal.scaled();
  print "scaled:", scaled
  if scaled:
    units = cal.units
    print "pixel width:", cal.pixelWidth
    print "pixel height:", cal.pixelHeight
    print "pixel depth:", cal.pixelDepth
   
  # Saving the image
  saveDir = currentDir.replace(srcDir, dstDir) if keepDirectories else dstDir
  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
  print "Saving to", saveDir
  IJ.saveAs(imp, ".jpg", os.path.join(saveDir, fileName+"_processed"));
 
run()
