import os
import re

from ij import IJ
from ij import Menus
from ij import WindowManager
from ij.gui import GenericDialog
from ij.macro import Interpreter

from java.awt import BorderLayout
from java.awt import Color
from java.awt import Container
from java.awt import Dimension
from java.awt.event import ActionListener
from java.awt.event import WindowAdapter

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
from javax.swing import JProgressBar;
from javax.swing import JOptionPane
from javax.swing import JSeparator
from javax.swing import SwingConstants
from javax.swing.border import Border
from javax.swing.filechooser import FileNameExtensionFilter

from loci.plugins import BF

from os.path import join


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

# This plugin creates a menu to batch process images using imagej's macro files.
# This pluign requires the user to have R installed on their machine.
# This plugin requires the user to have created a macro file with imagej's macro recorder
#	or to have hand crafted one.
# The plugin will then take that macro that was created from one specific image, and 
#	generalize it so that it can be used for batch processing of images.
# The user can select either a directory containing images, or a text file containing 
#	a list of urls to images. Then they select an output folder, where any new files
#	will be saved. Then they select one of the generalized macro files they have created.
#	They can then press start and it will perform the macro operation on all images found
#	in the directory or in the text file. When finished the results will be fed into an R
#	script for analyzing (need to implement)

class ImageProcessorMenu:
	# Closes the program
	def onExit(self, event):
		System.exit(0)

	# Constructor
	def __init__(self):
		#String of accepted file types for use throughout application
		self.validFileExtensionsString = ".jpg, .png, .tif"

		# Create the menu frame with size of 450x400
		frameWidth, frameHeight = 450, 400
		self.frame = JFrame("Medical Image Processing")
		self.frame.setSize(frameWidth, frameHeight)
		self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		# Add a panel to the frame
		pnl = JPanel()
		pnl.setBounds(10,10,480,230) #TODO: What are these? Use frameWidth/Height
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
		self.extensionTextfield = JTextField()
		self.extensionTextfield.setPreferredSize(Dimension(175,25))
		self.extensionTextfield.setText("Example: .jpg, .png")
		self.extensionTextfield.setName("Extensions")
		self.extensionTextfield.setToolTipText("Valid File Types: [" + self.validFileExtensionsString + "]")
		pnl.add(self.extensionTextfield)

		#Blank spaces for alignment purposes
		self.blankLbl = JLabel("     ")
		pnl.add(self.blankLbl)

		#Label for textfield below
		self.containsLabel = JLabel("File Name Contains:")
		pnl.add(self.containsLabel)

		# Add a textfield to the frame to get the specified text that a filename must contain
		self.containsTextfield = JTextField(30)
		pnl.add(self.containsTextfield)

		#Add a checkbox which determines whether or not to copy the original image file(s) to the newly created directory/directories
		self.copyImageToNewDirectoryCheckBox = JCheckBox("Copy Original Image(s) to Output Directory")
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

		# Create an exit menu option, Will close all windows associated with fiji
		fileExit = JMenuItem("Exit", None, actionPerformed=self.onExit)
		fileExit.setToolTipText("Exit application")
		file.add(fileExit)

		# Create a generalize macro menu option
		createGeneralMacro = JMenuItem("Create Generalized Macro File", None, actionPerformed=self.generalizePrompts)
		createGeneralMacro.setToolTipText("Create a macro file that can be used in the processing pipeline using an existings macro file")
		file.add(createGeneralMacro)

		# Add the menu to the frame
		menubar.add(file)
		self.frame.setJMenuBar(menubar)

		#Disable file extension textfield off the bat
		self.setExtensionTextfieldEnabled("All File Types")

		# Show the frame, done last to show all components
		self.frame.setResizable(False)
		self.frame.setVisible(True)
		self.checkIfPathSet()

	def checkIfPathSet(self):
		pluginDir = IJ.getDir("plugins") + "\Medical_Image"
		# Create the file to house the path
		file = File(pluginDir + "\Medical_Image_Processing.txt")
		if not file.exists():
			JOptionPane.showMessageDialog(self.frame, "No R path detected. You will be asked to select a directory\nIf you know the directory where R.exe is located select it.\n Otherwise, select your root directory (ie. C:/ or /root/)")
			self.rScriptSearch()

	#Enables/Disables the file extension textfield based on the user's selected delimiter
	def setExtensionTextfieldEnabled(selectedDelimiter):
		extTextfield = JTextField()
		# Iterate through JPanel to find the extension textfield
		for c in ImageProcessorMenu.fileSpecificationsPanel.getComponents():
			if (isinstance(c,JTextField)):
				if (c.getName() == "Extensions"):
					extTextfield = c

		# Disable the textfield
		if (selectedDelimiter == "All File Types"):
			border = BorderFactory.createLineBorder(Color.black)
			extTextfield.setEnabled(False)
			extTextfield.setDisabledTextColor(Color.black)
			extTextfield.setBackground(Color.lightGray)
			extTextfield.setBorder(border)
			extTextfield.setText("Example: .jpg, .png")
		# Enable the textfield
		else:
			border = BorderFactory.createLineBorder(Color.gray)
			extTextfield.setEnabled(True)
			extTextfield.setBackground(Color.white)
			extTextfield.setBorder(border)
			#Text will not clear if the user has specified extensions and has changed delimiter category
			if (extTextfield.getText() == "Example: .jpg, .png"):
				extTextfield.setText("")

	#Wrap method call so that it is callable outside this class' scope
	setExtensionTextfieldEnabled = CallableWrapper(setExtensionTextfieldEnabled)

	# Launches file chooser dialog boxes to select a macro to generalize, and when file was used to create it
	def generalizePrompts(self, event):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of files or directories
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)

		# Filter results to only .ijm files
		filter = FileNameExtensionFilter("Macro File", ["ijm"])
		chooseFile.addChoosableFileFilter(filter)

		# Show the chooser to select a .ijm file
		ret = chooseFile.showDialog(self.inputTextfield, "Choose file")

		# If a file is chosen continue to allow user to choose where to save the generalized file
		if chooseFile.getSelectedFile() is not None:
			if ret == JFileChooser.APPROVE_OPTION:
				frame = JFrame();

				# Creates a prompt asking the user of the name of the file used in creating the original macro
				result = JOptionPane.showInputDialog(frame, "Enter image name used to create macro (including extension):");
				if result != None:
					self.generalize(chooseFile.getSelectedFile(), result)

	# Takes a specific macro file and generalizes it to be used in the processing pipeline
	# macroFile, type=File, The specific macro file
	# file,	type=Sting, The name of the file used when creating the specific macro
	def generalize(self, macroFile, file):
		# Name of the file without the file extension
		fileName = file
		if fileName.find(".") > 0:
			fileName = fileName[0: fileName.find(".")]

		try:
			fileContents = ""
			string = ""

			# Read in the original macro file using a buffered reader
			br = BufferedReader(FileReader(macroFile))
			string = br.readLine()
			while string is not None:
				fileContents = fileContents + string
				string = br.readLine()

			# Replace anywhere text in the macro file where the images name is used with IMAGENAME
			fileContents = fileContents.replace(file, "IMAGENAME")

			# Replace the bio-formats importer directory path with INPUTPATH
			fileContents = re.sub("open=[^\"]*IMAGENAME", "open=[INPUTPATH]", fileContents)

			# Replace the bio-formats exporter directory path with FILEPATH
			fileContents = re.sub(r"save=[^\s\"]*\\",r"save=FILEPATH\\", fileContents)

			# Replace the bio-formats exporter directory path with FILPEPATH followed by text used to inidcate
			# 	what processing was done on the image and IMAGENAME
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)IMAGENAME",r"save=[FILEPATH\\\\\1IMAGENAME]", fileContents)

			# Replace the save results directory path with FILEPATH
			fileContents = re.sub("saveAs\(\"Results\", \".*\\\\", r'saveAs("Results", "FILEPATH\\\\', fileContents)

			# Replace the save text directory path with FILEPATH
			fileContents = re.sub("saveAs\(\"Text\", \".*\\\\", r'saveAs("Text", "FILEPATH\\\\', fileContents)

			# Replace all places where the image name without a file extension appears with NOEXTENSION
			fileContents = re.sub(fileName, "NOEXTENSION", fileContents)

			# Do not believe this is necessary, will keep till tested
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)NOEXTENSION([^\s\"]*)",r"save=[FILEPATH\\\\\1NOEXTENSION\2]", fileContents)

			# Replace all paths found in the open command with INPUTPATH\\IMAGENAME
			fileContents = re.sub('open\("[^"]*\\IMAGENAME"','open("INPUTPATH\\\\IMAGENAME"', fileContents)

			# Replace all paths found using run("save") with path FILEPATH\\IMAGENAME for instances that use the same file extension and FILEPATH\\NOEXTENSION for different file extensions
			fileContents = re.sub(r'run\("Save", "save=[^"]*\\([^"]*)IMAGENAME"', 'run("Save", "save=[FILEPATH\\\\\1IMAGENAME]"', fileContents)
			fileContents = re.sub(r'run\("Save", "save=[^"]*\\([^"]*)NOEXTENSION([^"]*)"', 'run("Save", "save=[FILEPATH\\\\\1NOEXTENSION\2]"', fileContents)

			# Replace all paths found using saveAs with path FILEPATH\\IMAGENAME for instances that use the same file extension and FILEPATH\\NOEXTENSION for different file extensions
			fileContents = re.sub(r'saveAs\([^,]*, "[^"]*\\([^"]*)IMAGENAME"\)', 'saveAs(\1, "FILEPATH\\\\\2IMAGENAME")', fileContents)
			fileContents = re.sub(r'saveAs\([^,]*, "[^"]*\\([^"]*)NOEXTENSION([^"]*)"\)', 'saveAs(\1,"FILEPATH\\\\\2NOEXTENSION\3")', fileContents)

			# Inserts code to save the images if no save commands are found in the original macro file
			if fileContents.find("Bio-Formats Exporter") == -1 and fileContents.find("saveAs(") == -1 and fileContents.find('run("Save"') == -1:
				# Split the macro by ; and add the text ;saveChanges(); inbetween each split to save any images changes that might have occured
				# This calls the function saveChanges() defined in the macro
				listOfLines = fileContents.split(";")
				fileContents = ""
				for line in listOfLines:
					fileContents = fileContents + line + ";" + "saveChanges();"


				# Inserts in import function if the user did not use one
				if fileContents.find("Bio-Formats Importer") == -1 and fileContents.find("open(") == -1:
					importCode = ('run("Bio-Formats Importer", "open=[INPUTPATH] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");'
									'run("Stack to RGB");'
									'selectedImage = getImageID();'
									'for (i=0; i < nImages; i++){ '
									'selectImage(i+1);'
									'if(!(selectedImage == getImageID())){'
									'close();i = i - 1;}}'
									'selectImage(selectedImage);'
									'rename(getInfo("image.filename"))')
					fileContents = importCode + fileContents

				# Add the function saveChanges() to the macro to check for any changes in the images that need to be saved
				functionToSave = ('function saveChanges(){'
									# Checks if an image is open
									'if(nImages != 0){'
										# Store the id of the open image to reselect it once the process is over
										'selectedImage = getImageID();'
										'for (i=0; i < nImages; i++){ '
											'selectImage(i+1);'
											'title = replace(getTitle(), " ", "_");'
											# If anything exists after the extension, move it to the front of the image name instead
											'if(indexOf(title, "_", indexOf(title, ".")) != -1){'
												'title = substring(title, indexOf(title, "_", indexOf(title, ".")) + 1) + substring(title, 0, indexOf(title, "_", indexOf(title, ".")));'
											'}'
											# If file doesn't exist, save it
											'if(File.exists("FILEPATH\\\\" + title) != 1){'
												'run("Bio-Formats Exporter", "save=[FILEPATH\\\\" + title + "]" + " export compression=Uncompressed");'
												'setOption("Changes", false);'
											'}'
											# If changes have been made to the image, save it
											'if(is("changes")){'
												# Name without extension
												'name = substring(title, 0, indexOf(title,"."));'
												# Filename counter
												'titleIteration = 0;'
												# File extension
												'ext = substring(title, indexOf(title, "."));'
												# While the file exists, increment the counter to produce a different name
												'while(File.exists("FILEPATH\\\\" + name + "(" + titleIteration + ")" + ext) == 1){'
													'titleIteration = titleIteration + 1;'
												'}'
												# Name of the file to export
												'title = name + "(" + titleIteration + ")" + ext;'
												'run("Bio-Formats Exporter", "save=[FILEPATH\\\\" + title + "]" + " export compression=Uncompressed");'
												# Rename the open window to the new file name
												'rename(title);'
												# Mark file has no changes
												'setOption("Changes", false);'
											'}'
										'}'
										# Select the image that was originally selected
										'selectImage(selectedImage);'
									'}'
								'}')
				fileContents = functionToSave + fileContents
				
			# Inserts a save results function if a results window is open and the user did not save it
			if fileContents.find('saveAs("Results"') == -1:
				fileContents = fileContents + "if (isOpen(\"Results\")) { selectWindow(\"Results\");saveAs(\"Results\", \"FILEPATH\\\\Results.csv\");}"

			# Closes any open images
			fileContents = fileContents + 'if(nImages != 0){for (i=0; i < nImages; i++){selectImage(i+1);close();i=i-1;}'

			# Closes the results window if one opens
			fileContents = fileContents + "if (isOpen(\"Results\")) { selectWindow(\"Results\"); run(\"Close\");}"
			
			# Create the general macro file and write the generalized text to it, use a file browswer to select where to save file
			fileChooser = JFileChooser();
			if fileChooser.showSaveDialog(self.frame) == JFileChooser.APPROVE_OPTION:
				newMacro = fileChooser.getSelectedFile()

				# Write genearalized macro using a buffered writer
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

	# Creates a file chooser to select a file with a list of urls that link to images
	def selectURLFile(self, event):
		# Creates a file chooser object
		chooseFile = JFileChooser()

		# Allow for selection of only files
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
		# Show the chooser
		ret = chooseFile.showDialog(self.inputTextfield, "Choose url file")
		if chooseFile.getSelectedFiles() is not None:

			# Save the selection to attributed associated with input or output
			if ret == JFileChooser.APPROVE_OPTION:
				# Save the path to the file
				self.urlLocation = chooseFile.getSelectedFile().getPath()
				# Change the text of the input textbox to the path to the url file
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
			#Jump to the user's previously selected directory location
			if (directoryType == "Input" and not self.inputTextfield.getText() == "Select Input Directory"):
				chooseFile.setCurrentDirectory(File(self.inputTextfield.getText()))
			elif (directoryType == "Output" and not self.outputTextfield.getText() == "Select Output Directory"):
				chooseFile.setCurrentDirectory(File(self.outputTextfield.getText()))
		else:
			#Allow for selection of files
			chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
			#Jump to the user's previously selected directory location
			if (directoryType == "Macro File" and not self.macroSelectTextfield.getText() == "Select Macro File"):
				chooseFile.setCurrentDirectory(File(self.macroSelectTextfield.getText()))
			elif (directoryType == "R Script" and not self.rScriptSelectTextfield.getText() == "Select R Script"):
				chooseFile.setCurrentDirectory(File(self.rScriptSelectTextfield.getText()))

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
			pass

	# Downloads the images from the url file
	def start(self, event):
		try:
			if self.urlLocation is not None:
				self.downloadFiles(self.urlLocation)
		except AttributeError:
			pass
		self.runMacro()

	# Downloads each image in the file of image urls
	def downloadFiles(self, filename):
		# Make the input directory the location of the downloaded images
		self.inputDirectory = self.outputDirectory.getPath() + "\\originalImages\\"
		self.inputDirectory.mkdirs()
		# Save each image in the file
		for image in self.readURLList(filename):
			IJ.save(image, self.inputDirectory + image.getTitle())

	# returns an array of ImageJ image objects
	def readURLList(self, filename):
		f, images = open(filename, 'r'), []
		for line in f:
			images.append(IJ.openImage(line))
		f.close()
		return images

	def runRScript(self, scriptFilename):
		if not self.rcommand:
			self.rcommand = "Rscript"
		os.system("{!s} {!s}".format(self.rcommand, scriptFilename))

	# Runs the macro file for each image in the input directory
	def runMacro(self):
		#Accepted file types
		self.validFileExtensions = self.validFileExtensionsString.split(", ")
		#Add blank string to list in case user does not specify file extensions
		self.validFileExtensions.append("")
		#Get the user's selected delimiter
		self.choice = self.delimeterComboBox.getSelectedItem()

		#Get user's desired file extensions
		#No need to get selected extensions if user wants all file types or has not specified any extensions
		if (self.choice == "All File Types" or (self.extensionTextfield.getText() == "")):
			self.selectedExtensions = self.validFileExtensions
		#User has chosen to include/exclude files of certain types
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

		#Location of R Script
		if not (self.rScriptSelectTextfield.getText() == "Select R Script"):
			rScript = File(self.rScriptDirectory.getPath())

			#Validation routine to ensure selected R Script is actually an R Script (file extension = '.R')
			if not (validateUserInput(self, self.rScriptSelectTextfield.getName(), [rScript.getName()[-2:]], [".R"])):
				return

		# Gets an array of all the images in the input directory
		listOfPictures = self.inputDirectory.listFiles()

		#Returns images as specified by the user and adds them to a list
		listOfPicturesBasedOnUserSpecs = getImagesBasedOnUserFileSpecications(self, listOfPictures)

		# Save the array of images to the instance
		self.pictures = listOfPicturesBasedOnUserSpecs

		# Read in the macro file with a buffered reader
		self.readInMacro()
		
		# Create an index indicating which image in the array is next to be processed
		self.index = 0
		self.process()

	#Reads in the macro file and stores it as a string to be modified during process
	def readInMacro(self):
		fileContents = ""
		string = ""
		# Read in the general macro
		br = BufferedReader(FileReader(self.macroFile))
		string = br.readLine()
		while string is not None:
			fileContents = fileContents + string
			string = br.readLine()
		self.macroString = fileContents

	# Gets the next image to process and creates a specific macro for that file
	# Creates an instance of macroRunner to run the macro on a seperate thread
	def process(self):
		# True when processing the first image
		if self.index == 0:
			# Hide the main menu
			self.frame.setVisible(False)

			# Create the progress menu and pass it a reference to the main menu
			self.macroMenu = MacroProgressMenu()
			self.macroMenu.setMenuReference(self)
			
		# Checks that there is another image to process
		if self.index < len(self.pictures):

			# Increase the progress bar's value
			self.macroMenu.setProgressBarValue(int(((self.index + 1.0) / len(self.pictures)) * 100))
			
			# Image to process
			file = self.pictures[self.index]

			# Increase the index indicating which file to be processed next
			self.index = self.index + 1

			# The name of the image without a file extension
			fileName = file.getName()
			if fileName.index(".") > 0:
				fileName = fileName[0: fileName.index(".")]

			#Will determine if user has specified an output directory or url location
			selectedDir = ""

			# Create a folder with the name of the image in the output folder to house any outputs of the macro
			if (self.outputDirectory is not None):
				outputDir = File(self.outputDirectory.getPath() + "/" + fileName)
				selectedDir = self.outputDirectory.getPath() + "/Log.txt"
			else:
				outputDir = File(self.urlLocation.getPath() + "/" + fileName)
				selectedDir = self.urlLocation.getPath() + "/Log.txt"
			
			print self.outputDirectory.getPath()
			print outputDir
			outputDir.mkdir()

			# INPUTPATH: Replaced with the path to the file to be processed (path includes the file with extension)
			# FILEPATH: Replaced with the path where any outputs from the macro will be saved
			# IMAGENAME: Replaced with the name of the file with file extension
			# NOEXTENSION: Replaced with the name of the file without file extension
			# run("View Step"): Replaced with macro command to wait for user input to contine, allow user to make
			#	sure the macro is working correctly
			try:
				# Copy the macro string to be modified, leaving the original
				fileContents = self.macroString
					
				# Replace all the generalized strings with specifics
				fileContents = fileContents.replace("INPUTPATH", file.getPath().replace("\\","\\\\"))
				fileContents = fileContents.replace("FILEPATH", outputDir.getPath().replace("\\","\\\\"))
				fileContents = fileContents.replace("IMAGENAME", file.getName().replace("\\","\\\\"))
				fileContents = fileContents.replace("NOEXTENSION", fileName.replace("\\","\\\\"))
				fileContents = fileContents.replace('run("View Step")','waitForUser("Press ok to continue")')

			except IOException:
				print "IOException"

			# Create a macroRunner object to run the macro on a seperate thread
			self.runner = macroRunner()

			# Give the macroRunner object the macro to run
			self.runner.setMacro(fileContents)

			# Give the macroRunner object a reference to this menu so it can call process
			# 	on this instance when it finishes running the macro so the next image can 
			# 	be processed
			self.runner.setReference(self)

			# Start the macro
			thread = Thread(self.runner)
			thread.start()

			#Create a txt file for log info
			log = open(selectedDir, 'a')
			log.write('Results for image: ' + outputDir.getPath() + '\n')

			#Make a copy of the original image if the user has chosen to do so
			if (self.copyImageToNewDirectoryCheckBox.isSelected()):
				copyOriginalImageToNewDirectory(self, fileName, outputDir)
				log.write('Copied image to: ' + self.outputDirectory.getPath() + '\n')

			#Append each processing operation to the log file
			log.write('Process performed: ' + '\n')
			operationsPerformed = fileContents.split(";")
			for i in operationsPerformed:
				log.write('\t' + i + '\n')
			log.write('\n')
			log.write('\n')

			#Close the file
			log.close()
		else:
			# Macros are finished running, so show the main menu and dispose
			#	of the progress menu.
			self.frame.setVisible(True)
			self.macroMenu.disposeMenu()

	# Searches for the R.exe file on the users system to give pyper the path to it
	# Creates a file chooser to allow the user to specificy in which directory
	#	and thus sub directories to look for it in. Allows the seach to happen
	# 	faster if the user knows where to look, or lets user with no knowledge 
	# 	of file systems find the file by specifiying the root of the drive
	# Saves the path in the Medical_Image_Processing.txt file in the 
	# 	Medical_Image folder found in the fiji plugins directory
	def rSearch(self):
		# File to search for
		lookfor = 'R.exe'

		# Create a file chooser to pick which directory to recrursively search in
		chooser = JFileChooser()
		chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
		if chooser.showDialog(self.frame, "Select") == JFileChooser.APPROVE_OPTION:

			# Recursively search all directories starting in the path choosen by the user
			for root, dirs, files in os.walk(chooser.getSelectedFile().getPath()):

				# If the file is in one of the directories, store the path and break
				if lookfor in files:
					found = join(root, lookfor)
					self.rcommand = found
					try:
						# Path to the Medical_Image directory
						pluginDir = IJ.getDir("plugins") + "\Medical_Image"

						# Create the file to house the path
						file = File(pluginDir + "\Medical_Image_Processing.txt")
						writer = BufferedWriter(FileWriter(file))

						# Create the contents of the file
						# rPath: Path to R.exe on the users system
						# inputPath: Last used input directory path
						# outputPath: Last used output directory path 
						# macroPath: Last used macro file path
						# rScriptPath: Last used r script file path
						contents = "rPath\t" + found + "\r\n"
						contents = contents + "inputPath\t\r\n"
						contents = contents + "outputPath\t\r\n"
						contents = contents + "macroPath\t\r\n"
						contents = contents + "rScriptPath\t\r\n"
						writer.write(contents)
						writer.close()
					except IOException:
						print "IO Exception"
					break

	# Looks for RScript.exe
	def rScriptSearch(self):
		chooseFile = JFileChooser()
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
		# TODO: Verify that the selected file is Rscript
		if chooseFile.showDialog(self.frame, "Select") is not None:
			self.rcommand = chooseFile.getSelectedFile()
		#JOptionPane.showMessageDialog(self.frame, self.rcommand)
		#self.saveToFile()

	# Funtion to open the text file where data is saved
	def saveToFile(self):
		try:
			pluginDir = IJ.getDir("plugins") + "/Medical_Image"
			f = File(pluginDir + "/Medical_Image_Processing.txt")
			writer = BufferedWriter(fileWriter(f))
			# Write stuff to file
			writer.write(contents)
			writer.close()
		except IOException:
			print "IO Exception"

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
	IJ.save(img, outputDir.getPath())
	img.close()

#Gets values from file specification components within the JPanel and returns images based on user's specifications
def getImagesBasedOnUserFileSpecications(self, images):
	imagesToReturn = []
	for file in images:
		fileName = file.getName()
		#Check for file extensions
		if (fileName[-4:].lower() in self.selectedExtensions):
			if ((self.choice == "Include" or self.choice == "All File Types") or (self.choice == "Exclude" and self.selectedExtensions == self.validFileExtensions)):
				if not (self.containString == ""):
					if (self.containString in fileName):
						imagesToReturn.append(file)
				else:
					imagesToReturn.append(file)
		if not (fileName[-4:].lower() in self.selectedExtensions):
			if (self.choice == "Exclude" and fileName[-4:].lower() in self.validFileExtensions):
				if not (self.containString == ""):
					#Check for file name pattern
					if (self.containString in fileName):
						imagesToReturn.append(file)
				#No file name pattern specified
				else:
					imagesToReturn.append(file)

	return imagesToReturn


# Extends the WindowAdapter class: does this to overide the windowClosing method
#	to create a custom close operation.
# Creates a progress bar indicating what percentage of images have been processed
# Closing the menu will stop the images from being processed
class MacroProgressMenu(WindowAdapter):
	def __init__(self):
		# Create a frame as backbone for the menu, add listener for custom close operation
		self.macroMenuFrame = JFrame("Processing Images...")
		self.macroMenuFrame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE)
		self.macroMenuFrame.addWindowListener(self)
		
		content = self.macroMenuFrame.getContentPane()

		# Create the progess bar
		self.progressBar = JProgressBar()
		self.setProgressBarValue(0)
		self.progressBar.setStringPainted(True)

		# Add a border
		border = BorderFactory.createTitledBorder("Processing...");
		self.progressBar.setBorder(border)
		content.add(self.progressBar, BorderLayout.NORTH)

		# Set size and show frame
		self.macroMenuFrame.setSize(300, 100)
		self.macroMenuFrame.setVisible(True)
		
	# Sets a reference to the main menu
	# Would put in constructor, but cannot get variables to be passed in that way
	def setMenuReference(self, ref):
		self.ref = ref

	# Sets the progress bar's value
	def setProgressBarValue(self, value):
		self.progressBar.setValue(value)

	# Override
	# Custom on close opperation
	def windowClosing(self, event):
		# Prevents more macros from running	
		self.ref.runner.run = False
		# Stops currently ruuing macro
		self.ref.runner.abortMacro()
		# Shows the main menu
		self.ref.frame.setVisible(True)

		# Disposes of this progress menu
		self.disposeMenu()

	# Disposes of this progress menu
	def disposeMenu(self):
		self.macroMenuFrame.dispose()


###############################################################
# Extends the class runnable to run on a seperate thread      #
# Recieves a macro file from the ImageProcessorMenu instance  #
# 	and runs the macro. After the macro is executed, it calls #
#	the process method of the ImageProcessorMenu instance to  #
#	create a macro for the next file.                         #
# Cannot get a new constuctor to work otherwise the set       #
# 	methods would just be part of the constructor             #
###############################################################
class macroRunner(Runnable):
		
	# Overides the run method of the Runnable class
	# Creates an instance of Interpreter to run the macro
	# Runs the macro in the instance and calls process on
	#	the ImageProcessorMenu instance
	def run(self):
		self.run = True
		self.inter = Interpreter()
		self.inter.run(self.macroString)
		# Prevents future macros from running if current macro was aborted
		if self.run:
			self.ref.process()

	# Sets the macro file
	# string, the macro file to be run
	def setMacro(self, string):
		self.macroString = string

	# Sets the ImageProcessMenu instance that is processing images
	# ref, the ImageProcessMenu instance
	def setReference(self, ref):
		self.ref = ref

	# Aborts the currently running macro
	def abortMacro(self):
		self.inter.abort()

if __name__ == '__main__':
	#start things off.
	ImageProcessorMenu()
