from javax.swing import JFrame
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import JButton
from javax.swing import JFileChooser
from javax.swing import JMenu
from javax.swing import JMenuBar
from javax.swing import JMenuItem
from javax.swing import JPopupMenu
from javax.swing import JOptionPane
from java.lang import System
from javax.swing.filechooser import FileNameExtensionFilter
from loci.plugins import BF
from ij import IJ
from ij.macro import MacroRunner
from java.io  import File
from java.io import BufferedReader
from java.io import FileReader
from java.io import IOException
from java.io import FileWriter
from java.io import BufferedWriter
from java.lang import Thread
from threading import Lock
from ij import WindowManager
from pyper import *
import os
import re

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
		self.frame = JFrame("Medical Image Processing")
		self.frame.setSize(450, 250)
		self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		# Add a panel to the frame
		pnl = JPanel()
		pnl.setBounds(10,10,480,230)
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

		# Add a start button to the frame
		self.startButton = JButton('Start', actionPerformed=self.start)
		self.startButton.setEnabled(False)
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

		# Show the frame, done last to show all components
		self.frame.setVisible(True)
		
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

			fileContents = fileContents.replace(file, "IMAGENAME")
			#fileContents = re.sub("open=\[[^\]]*\]", "open=[INPUTPATH]", fileContents)
			fileContents = re.sub("open=[^\"]*IMAGENAME", "open=[INPUTPATH]", fileContents)
			fileContents = re.sub(r"save=.*\\",r"save=FILEPATH\\", fileContents)
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)IMAGENAME",r"save=[FILEPATH\\\1IMAGENAME]", fileContents)
			fileContents = re.sub("saveAs\(\"Results\", \".*\\\\", "saveAs(\"Results\", \"FILEPATH\\\w", fileContents)

			# Create the general macro file and write the generalized text to it
			newMacro = File(outputDir.getPath() + "\\general_macro.ijm")
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

	# Creates a filechooser for the user to select a directory for input or output
	# @param inputOrOutput	Determines whether or not to be used to locate the input or output directory
	def setDirectory(self, inputOrOutput):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of directories
		chooseFile.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
		
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose " + inputOrOutput + " directory")
		if chooseFile.getSelectedFiles() is not None:
		
			# Save the selection to attributed associated with input or output
			if ret == JFileChooser.APPROVE_OPTION:
				if inputOrOutput == "Input":
					self.inputDirectory = chooseFile.getSelectedFile()
					self.inputTextfield.setText(chooseFile.getSelectedFile().getPath())
					self.urlLocation = None
				else:
					self.outputDirectory = chooseFile.getSelectedFile() 
					self.outputTextfield.setText(chooseFile.getSelectedFile().getPath())
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

	# It would help if dataFilename were an absolute path
	def runRScript(self, dataFilename):
		# Instead of running an R script, we'll be running R commands from here
		r = R()
		r("imageData = read.csv('%s')" % dataFilename)

	# Runs the macro file for each image in the input directory
	def runMacro(self):

		# Location of the generalized macro function, this will be a prompt where the user selects the file
		macroFile = File("C:\Users\Matthew\Documents\School\College\Fall 2015\cs470\Macro.ijm")

		# Gets an array of all the images in the input directory
		listOfPictures = self.inputDirectory.listFiles()

		# For each image in the array, create a specific macro for it and run that macro
		for file in listOfPictures:

			# The name of the image
			fileName = file.getName()

			# The name of the image without a file extension
			if fileName.index(".") > 0:
				fileName = fileName[0: fileName.index(".")]

			# Create a folder with the name of the image in the output folder to house any outputs of the macro
			outputDir = File(self.outputDirectory.getPath() + "\\" + fileName)
			outputDir.mkdir()

			
			try:
				fileContents = ""
				string = ""
				# Read in the general macro
				br = BufferedReader(FileReader(macroFile))
				string = br.readLine()
				while string is not None:
					fileContents = fileContents + string
					string = br.readLine()
				# Replace all the generalized strings with specifics
				fileContents = fileContents.replace("INPUTPATH", file.getPath())
				fileContents = fileContents.replace("FILEPATH", outputDir.getPath())
				fileContents = fileContents.replace("IMAGENAME", file.getName())
				fileContents = fileContents.replace("\\","\\\\")
			except IOException:
				print "IOException"
			IJ.runMacro(fileContents)
			
if __name__ == '__main__':
	#start things off.
	ImageProcessorMenu()