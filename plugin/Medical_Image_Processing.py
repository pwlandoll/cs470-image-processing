import os
import re

from ij import IJ
from ij import Menus
from ij import WindowManager
from ij.gui import GenericDialog
from ij.macro import Interpreter

from java.awt import Color
from java.awt import Dimension
from java.awt.event import ActionListener

from java.io import BufferedReader
from java.io import BufferedWriter
from java.io import File
from java.io import FileReader
from java.io import FileWriter
from java.io import IOException

from java.lang import System
from java.lang import Thread
from java.lang import Runnable

from javax.swing import BorderFactory
from javax.swing import BoxLayout
from javax.swing import JFrame
from javax.swing import JCheckBox
from javax.swing import JLabel
from javax.swing import JComboBox
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import JButton
from javax.swing import JFileChooser
from javax.swing import JMenu
from javax.swing import JMenuBar
from javax.swing import JMenuItem
from javax.swing import JPopupMenu
from javax.swing import JOptionPane
from javax.swing import JSeparator
from javax.swing import SwingConstants
from javax.swing.border import Border
from javax.swing.filechooser import FileNameExtensionFilter

from loci.plugins import BF

from pyper import *

#Wraps a method call to allow static methods to be called from ImageProcessorMenu
class CallableWrapper:
	def __init__(self, any):
		self.__call__ = any


#ActionListener for DelimiterComboBox
class DelimiterActionListener(ActionListener):
	def actionPerformed(self,event):
		#Get DelimiterComboBox object
		box = event.getSource()
		#Enable/Disable extension textfield based on selected delimiter
		ImageProcessorMenu.setExtensionTextfieldEnabled(box.getSelectedItem())


class ImageProcessorMenu:
	# Opens an open dialog box for the user to select a file
	# Once selected, the file path is added to the textbox
	def browseForFile(self,event):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of files or directories
		chooseFile.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES)
		chooseFile.setMultiSelectionEnabled(True)

		# Filter results
		filter = FileNameExtensionFilter("Image Files", ["jpg", "gif"])
		chooseFile.addChoosableFileFilter(filter)
		
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose file")
		if chooseFile.getSelectedFiles() is not None:
			if len(chooseFile.getSelectedFiles()) != 1:
				self.inputTextfield.text = "Multiple Files"
			else:
				self.inputTextfield.text = chooseFile.getSelectedFile().getPath()
			if ret == JFileChooser.APPROVE_OPTION:
				# Open the file using bio formats plugin
				self.file = chooseFile.getSelectedFiles()
				for x in range(0, len(self.file)):
					tempFile = self.file[x].getPath()
					imps = BF.openImagePlus(tempFile)
					for imp in imps:
						imp.show()

	# Closes the program
	def onExit(self, event):
		System.exit(0)

	def __init__(self):
		# Create the menu frame with size of 450x250
		frameWidth = 450
		frameHeight = 400
		self.frame = JFrame("Medical Image Processing")
		self.frame.setSize(frameWidth, frameHeight)
		self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		# Add a panel to the frame
		pnl = JPanel()
		pnl.setBounds(10,10,480,230)
		#pnl.setLayout(BoxLayout(BoxLayout.LINE_AXIS)
		self.frame.add(pnl)
		
		# Add a textfield to the frame to display the input directory
		self.inputTextfield = JTextField(30)
		self.inputTextfield.setText("Select Import Directory")
		pnl.add(self.inputTextfield)

		# Add a browse button to the frame for an input directory 
		inputButton = JButton('Select',actionPerformed=self.optionMenuPopup)
		pnl.add(inputButton)

		# Add a textfield to the frame to display the output directory
		self.outputTextfield = JTextField(30)
		self.outputTextfield.setText("Select Output Directory")
		pnl.add(self.outputTextfield)

		# Add a browse button to the frame to search for an output directory
		outputButton = JButton('Select',actionPerformed=self.setOutputDirectory)
		pnl.add(outputButton)

		# Add a textfield to the frame to display the macro file directory
		self.macroSelectTextfield = JTextField(30)
		self.macroSelectTextfield.setText("Select Macro File")
		self.macroSelectTextfield.setName("Macro File")
		pnl.add(self.macroSelectTextfield)

		# Add a browse button to the frame to search for a macro file
		macroFileSelectButton = JButton('Select',actionPerformed=self.setMacroFileDirectory)
		pnl.add(macroFileSelectButton)

		# Add a textfield to the frame to display the R Script directory
		self.rScriptSelectTextfield = JTextField(30)
		self.rScriptSelectTextfield.setText("Select R Script")
		self.rScriptSelectTextfield.setName("R Script")
		pnl.add(self.rScriptSelectTextfield)

		# Add a browse button to the frame to search for an R Script
		rScriptSelectButton = JButton('Select',actionPerformed=self.setRScriptDirectory)
		pnl.add(rScriptSelectButton)

		#Add separator line for user friendliness
		sep = JSeparator(SwingConstants.HORIZONTAL)
		sep.setPreferredSize(Dimension(frameWidth - 35,5))
		pnl.add(sep)

		#Save south-most panel as globally accessible object in order to iterate through pertinent components
		ImageProcessorMenu.fileSpecificationsPanel = pnl
		
		#Label for textfield below
		self.extensionLabel = JLabel("File Extensions:")
		pnl.add(self.extensionLabel)

		#ComboBox for selected file extension delimeter
		self.delimeterComboBox = JComboBox()
		self.delimeterComboBox.addItem("All File Types")
		self.delimeterComboBox.addItem("Include")
		self.delimeterComboBox.addItem("Exclude")
		self.delimeterComboBox.addActionListener(DelimiterActionListener())
		pnl.add(self.delimeterComboBox)
		
		# Add a textfield to the frame to get the user's selected file extensions
		self.extensionTextfield = JTextField(30)
		self.extensionTextfield.setText("Example: .jpg, .png")
		self.extensionTextfield.setName("Extensions")
		pnl.add(self.extensionTextfield)

		#Label for textfield below
		self.containsLabel = JLabel("File Name Contains:")
		pnl.add(self.containsLabel)
		
		# Add a textfield to the frame to get the specified text that a filename must contain
		self.containsTextfield = JTextField(30)
		pnl.add(self.containsTextfield)
		
		#Add a checkbox which determines whether or not to copy the original image file(s) to the newly created directory/directories
		self.copyImageToNewDirectoryCheckBox = JCheckBox("Make a Copy of Pre-Processed Image(s) in Output Directory")
		pnl.add(self.copyImageToNewDirectoryCheckBox)

		#Add separator line for user friendliness
		sep2 = JSeparator(SwingConstants.HORIZONTAL)
		sep2.setPreferredSize(Dimension(frameWidth - 35,5))
		pnl.add(sep2)

		# Add a start button to the frame
		self.startButton = JButton('Start', actionPerformed=self.start)
		self.startButton.setEnabled(False)
		self.startButton.setPreferredSize(Dimension(150,40))
		pnl.add(self.startButton)
		
		# Add a menu to the frame
		menubar = JMenuBar()
		file = JMenu("File")
		fileExit = JMenuItem("Exit", None, actionPerformed=self.onExit)
		fileExit.setToolTipText("Exit application")
		file.add(fileExit)
		createGeneralMacro = JMenuItem("Create Generalized Macro File", None, actionPerformed=self.generalizePrompts)
		createGeneralMacro.setToolTipText("Create a macro file that can be used in the processing pipeline using an existings macro file")
		file.add(createGeneralMacro)
		menubar.add(file)
		self.frame.setJMenuBar(menubar)

		#Disable file extension textfield off the bat
		self.setExtensionTextfieldEnabled("All File Types")
		
		# Show the frame, done last to show all components
		self.frame.setResizable(False)
		self.frame.setVisible(True)

	#Enables/Disables the file extension textfield based on the user's selected delimiter
	def setExtensionTextfieldEnabled(selectedDelimiter):
		extTextfield = JTextField()
		#Iterate through JPanel to find the extension textfield
		for c in ImageProcessorMenu.fileSpecificationsPanel.getComponents():
			if (isinstance(c,JTextField)):
				if (c.getName() == "Extensions"):
					extTextfield = c	
									
		#Enable the textfield
		if (selectedDelimiter == "All File Types"):
			border = BorderFactory.createLineBorder(Color.black)
			extTextfield.setEnabled(False)
  			extTextfield.setDisabledTextColor(Color.black)
  			extTextfield.setBackground(Color.lightGray)
			extTextfield.setBorder(border)
		#Disable the textfield
		else:
			border = BorderFactory.createLineBorder(Color.gray)
			extTextfield.setEnabled(True)
  			extTextfield.setBackground(Color.white)
			extTextfield.setBorder(border)

	#Wrap method call so that it is callable outside this class' scope
	setExtensionTextfieldEnabled = CallableWrapper(setExtensionTextfieldEnabled)
		
	def generalizePrompts(self, event):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of files or directories
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)

		# Filter results
		filter = FileNameExtensionFilter("Macro File", ["ijm"])
		chooseFile.addChoosableFileFilter(filter)
		
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose file")
		if chooseFile.getSelectedFile() is not None:
			if ret == JFileChooser.APPROVE_OPTION:
				frame = JFrame();
    			result = JOptionPane.showInputDialog(frame, "Enter image name used to create macro (including extension):");
    			if result != None:
    				self.generalize(chooseFile.getSelectedFile(), result)

	# Takes a specific macro file and generalizes it to be used in the processing pipeline
	# Needs to create a menu that will allow user to pick the file instead of a static one
	def generalize(self, macroFile, imageName):
		# Name of the file used to create the macro file, will change to prompt to ask user
		file = imageName
		
		# Name of the file without the file extension
		fileName = file
		if fileName.find(".") > 0:
			fileName = fileName[0: fileName.find(".")]
		
		# Directory to create the general macro in
		outputDir = File("C:\Users\Matthew\Documents\School\College\Fall 2015\cs470\outputs")
		outputDir.mkdir()
		
		try:
			fileContents = ""
			string = ""

			# Read in the original macro file
			br = BufferedReader(FileReader(macroFile))
			string = br.readLine()
			while string is not None:
				fileContents = fileContents + string
				string = br.readLine()
				
			# Replace anywhere text in the macro file where the images name is used with IMAGENAME
			fileContents = fileContents.replace(file, "IMAGENAME")
			fileContents = re.sub("open=[^\"]*IMAGENAME", "open=[INPUTPATH]", fileContents)
			fileContents = re.sub(r"save=[^\s\"]*\\",r"save=FILEPATH\\", fileContents)
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)IMAGENAME",r"save=[FILEPATH\\\1IMAGENAME]", fileContents)
			fileContents = re.sub("saveAs\(\"Results\", \".*\\\\", r'saveAs("Results", "FILEPATH\\', fileContents)
			fileContents = re.sub("saveAs\(\"Text\", \".*\\\\", r'saveAs("Text", "FILEPATH\\', fileContents)
			fileContents = re.sub(fileName, "NOEXTENSION", fileContents)
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)NOEXTENSION([^\s\"]*)",r"save=[FILEPATH\\\1NOEXTENSION\2]", fileContents)

			# Create the general macro file and write the generalized text to it, use a file browswer to select where to save file
			fileChooser = JFileChooser();
			if fileChooser.showOpenDialog(self.frame) == JFileChooser.APPROVE_OPTION:
				newMacro = fileChooser.getSelectedFile()
				writer = BufferedWriter(FileWriter(newMacro))
				writer.write(fileContents)
				writer.close()
		except IOException:
			print "IO exception"

	# Creates a menu popup for the select input directory button, select input directory or url csv file
	def optionMenuPopup(self, event):
		# Create the menu
		menu = JPopupMenu()

		# Select directory item
		directoryItem = JMenuItem("Select Directory", actionPerformed=self.setInputDirectory)
		directoryItem.setToolTipText("Browse for the directory containing the images to process")
		menu.add(directoryItem)

		# Select url csv file item
		urlItem = JMenuItem("Select URL File", actionPerformed=self.selectURLFile)
		urlItem.setToolTipText("Browse for the file containing a comma seperated list of urls that point to images to process")
		menu.add(urlItem)

		# Show the menu
		menu.show(event.getSource(), event.getSource().getWidth(), 0)


	def selectURLFile(self, event):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of directories
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose url file")
		if chooseFile.getSelectedFiles() is not None:

			# Save the selection to attributed associated with input or output
			if ret == JFileChooser.APPROVE_OPTION:
				self.urlLocation = chooseFile.getSelectedFile().getPath()
				self.inputTextfield.setText(chooseFile.getSelectedFile().getPath())
				self.shouldEnableStart()
				
	# Sets the input directory
	def setInputDirectory(self, event):
		self.setDirectory("Input")

	# Sets the output directory
	def setOutputDirectory(self, event):
		self.setDirectory("Output")

	#Sets the macro file directory
	def setMacroFileDirectory(self,event):
		self.setDirectory("Macro File")

	#Sets the R script directory
	def setRScriptDirectory(self,event):
		self.setDirectory("R Script")

	# Creates a filechooser for the user to select a directory for input or output
	# @param directoryType	Determines whether or not to be used to locate the input, output, macro file, or R script directory
	def setDirectory(self, directoryType):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		if (directoryType == "Input" or directoryType == "Output"):
			# Allow for selection of directories
			chooseFile.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
		else:
			#Allow for selection of files
			chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
			
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose " + directoryType + " directory")
		if chooseFile.getSelectedFiles() is not None:
		
			# Save the selection to attributed associated with input or output
			if ret == JFileChooser.APPROVE_OPTION:
				if directoryType == "Input":
					self.inputDirectory = chooseFile.getSelectedFile()
					self.inputTextfield.setText(chooseFile.getSelectedFile().getPath())
					self.urlLocation = None
				elif directoryType == "Output":
					self.outputDirectory = chooseFile.getSelectedFile() 
					self.outputTextfield.setText(chooseFile.getSelectedFile().getPath())
				elif directoryType == "Macro File":
					self.macroDirectory = chooseFile.getSelectedFile() 
					self.macroSelectTextfield.setText(chooseFile.getSelectedFile().getPath())
				elif directoryType == "R Script":
					self.rScriptDirectory = chooseFile.getSelectedFile() 
					self.rScriptSelectTextfield.setText(chooseFile.getSelectedFile().getPath())
				self.shouldEnableStart()
				
	def shouldEnableStart(self):
		# Enable the start button if both an input and output have been selected
		try:
			if self.inputDirectory is not None or self.urlLocation is not None and self.outputDirectory is not None:
				self.startButton.setEnabled(True)
		except AttributeError:
			print "Needed to put something here"
			
	# Downloads the images from the url file
	def start(self, event):
		try:
			if self.urlLocation is not None:
				self.downloadFiles(self.urlLocation)
		except AttributeError:
			print "Need to add other functionality"
		self.runMacro()
			
	def downloadFiles(self, filename):
		for image in self.readURLList(filename):
			IJ.save(image, self.outputDirectory.getPath() + "\\" + image.getTitle())
		
	# returns an array of ImageJ image objects
	def readURLList(self, filename):
		f, images = open(filename, 'r'), []
		for line in f:
			images.append(IJ.openImage(line))
		f.close()
		return images

	def runRScript(self, dataFilename, scriptFilename):
		# R() can be given a path to the R executable if necessary
		# e.g. R("C:/Program Files/R/R-3.2.2/bin")
		if self.rcmd:
			r = R(RCMD="%s" % self.rcmd)
		else:
			r = R()
		r("imageData = read.csv('%s')" % dataFilename)
		r("source('%s')" % scriptFilename)

	# Runs the macro file for each image in the input directory
	def runMacro(self):
		#Accepted file types
		self.validFileExtensions = [".png", ".jpg", ".gif", ".txt", ".tif", ".ini"]

  		self.choice = self.delimeterComboBox.getSelectedItem()

  		#Get user's desired file extensions
  		if (self.choice == "All File Types"):
  			self.selectedExtensions = self.validFileExtensions
  			
  		else:
  			self.selectedExtensions = self.extensionTextfield.getText()
  			self.selectedExtensions = self.selectedExtensions.lower()
  			self.selectedExtensions = self.selectedExtensions.split(", ")

  		#Validation routine to ensure selected file extensions are valid and comma seperated
  		if not (validateUserInput(self, self.extensionTextfield.getName(), self.selectedExtensions, self.validFileExtensions)):
  			return
		
		#Get file name contains pattern
		self.containString = self.containsTextfield.getText()

		# Location of the generalized macro function, this will be a prompt where the user selects the file
		self.macroFile = File(self.macroDirectory.getPath())
		

		#Validation routine to ensure selected macro file is actually a macro file (file extension = '.ijm')
  		if not (validateUserInput(self, self.macroSelectTextfield.getName(), [self.macroFile.getName()[-4:]], [".ijm"])):
  			return

		# Gets an array of all the images in the input directory
		listOfPictures = self.inputDirectory.listFiles()

		#Returns images as specified by the user and adds them to a list
		listOfPicturesBasedOnUserSpecs = getImagesBasedOnUserFileSpecications(self, listOfPictures)
		self.pictures = listOfPicturesBasedOnUserSpecs
		self.index = 0
		self.process()

	# Gets the next image to process and creates a specific macro for that file
	# Creates an instance of macroRunner to run the macro on a seperate thread
	def process(self):
		# Checks that there is another image to process
		if self.index < len(self.pictures):

			# Image to process
			file = self.pictures[self.index]
			
			# Increase the index indicating which file to be processed next
			self.index = self.index + 1
			
			# The name of the image without a file extension
			fileName = file.getName()
			if fileName.index(".") > 0:
				fileName = fileName[0: fileName.index(".")]
		
			# Create a folder with the name of the image in the output folder to house any outputs of the macro
			outputDir = File(self.outputDirectory.getPath() + "/" + fileName)
			outputDir.mkdir()

			# Create the specific macro by reading in the general macro file and modify it with regular expressions
			# INPUTPATH: Replaced with the path to the file to be processed (path includes the file with extension)
			# FILEPATH: Replaced with the path where any outputs from the macro will be saved
			# IMAGENAME: Replaced with the name of the file with file extension
			try:
				fileContents = ""
				string = ""
				# Read in the general macro
				br = BufferedReader(FileReader(self.macroFile))
				string = br.readLine()
				while string is not None:
					fileContents = fileContents + string
					string = br.readLine()
				# Replace all the generalized strings with specifics
				fileContents = fileContents.replace("INPUTPATH", file.getPath())
				fileContents = fileContents.replace("FILEPATH", outputDir.getPath())
				fileContents = fileContents.replace("IMAGENAME", file.getName())
				fileContents = fileContents.replace("NOEXTENSION", fileName)
				fileContents = fileContents.replace('run("View Step")','waitForUser("Press ok to continue")')
				fileContents = fileContents.replace("\\","\\\\")
				fileContents = fileContents + "if (isOpen(\"Results\")) { selectWindow(\"Results\"); run(\"Close\");}"
			except IOException:
				print "IOException"
			runner = macroRunner()
			runner.setMacro(fileContents)
			runner.setReference(self)
			thread = Thread(runner)
			thread.start()
					
			#Make a copy of the original image if the user has chosen to do so
			if (self.copyImageToNewDirectoryCheckBox.isSelected()):
				copyOriginalImageToNewDirectory(self, fileName, outputDir)

def validateUserInput(self, inputCategory, userInput, validInputs):
	isValid = True
	errorTitle = ""
	errorMessage = ""
	
	for ext in userInput:
		if not (ext in validInputs):
			isValid = False 			

 	if not(isValid):
		self.frameToDispose = GenericDialog("")
		if (inputCategory == "Extensions"):
			errorTitle = "ERROR - Invalid File Extension Format(s)"
			errorMessage = "Error: One or More of Your Selected File Extensions is Invalid. \n  Ensure All Selected File Extensions Are Valid and Seperated by Commas."
		elif (inputCategory == "Macro File"):
			errorTitle = "ERROR - Invalid Macro File"
			errorMessage = "Error: You Have Selected an Invalid Macro File.  Please Ensure Your Selected File Ends With '.ijm'."
			
		self.frameToDispose.setTitle(errorTitle)
		self.frameToDispose.addMessage(errorMessage)
		self.frameToDispose.showDialog()

	return isValid

#Copies the original image from the existing directory to the newly created one
def copyOriginalImageToNewDirectory(self, fileToSave, outputDir):
  	img = IJ.openImage(self.inputDirectory.getPath() + "\\" + fileToSave)
  	IJ.save(img, outputDir.getPath() + "\\" + fileToSave)
  	img.close()

#Gets values from file specification components within the JPanel and returns images based on user's specifications
def getImagesBasedOnUserFileSpecications(self, images):
	imagesToReturn = []
	for file in images:
		fileName = file.getName()
		#Check for file extensions
		if (fileName[-4:].lower() in self.selectedExtensions):
			if (self.choice == "Include" or self.choice == "All File Types"):
				if (self.containString == ""):
					#print "FOUND FILE (Include): " + fileName
					imagesToReturn.append(file)
		if not (fileName[-4:].lower() in self.selectedExtensions):
			if (self.choice == "Exclude"):
				if (self.containString == ""):
					#print "FOUND FILE (Exclude): " + fileName
					imagesToReturn.append(file)
		#Check for file name pattern
		if (self.containString in fileName and not self.containString == ""):
			#print "FOUND FILE (Contains): " + fileName
			imagesToReturn.append(file)

	return imagesToReturn

#############################################################
# Extends the class runnable to run on a seperate thread
# Recieves a macro file from the ImageProcessorMenu instance
# 	and runs the macro. After the macro is executed, it calls
#	the process method of the ImageProcessorMenu instance to
#	create a macro for the next file.
# Cannot get a new constuctor to work otherwise the set 
# 	methods would just be part of the constructor
#############################################################
class macroRunner(Runnable):

	# Overides the run method of the Runnable class
	# Creates an instance of Interpreter to run the macro
	# Runs the macro in the instance and calls process on 
	#	the ImageProcessorMenu instance
	def run(self):
		inter = Interpreter()
		inter.run(self.macroString)
		self.ref.process()

	# Sets the macro file
	# string, the macro file to be run
	def setMacro(self, string):
		self.macroString = string

	# Sets the ImageProcessMenu instance that is processing images
	# ref, the ImageProcessMenu instance
	def setReference(self, ref):
		self.ref = ref

if __name__ == '__main__':
	#start things off.
	ImageProcessorMenu()
