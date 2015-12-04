import os
import re

from csv import reader

from ij import IJ
from ij import Menus
from ij import WindowManager
from ij.gui import GenericDialog
from ij.io import LogStream
from ij.macro import Interpreter
from ij.macro import MacroRunner

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
import datetime

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

from java.util import Scanner

from loci.plugins import BF

from os.path import join

from subprocess import call

from urllib import urlretrieve


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

# Wraps a method call to allow static methods to be called from ImageProcessorMenu
class CallableWrapper:
	def __init__(self, any):
		self.__call__ = any

# ActionListener for DelimiterComboBox
class DelimiterActionListener(ActionListener):
	def actionPerformed(self,event):
		# Get DelimiterComboBox object
		box = event.getSource()
		# Enable/Disable extension textfield based on selected delimiter
		ImageProcessorMenu.setExtensionTextfieldEnabled(box.getSelectedItem())

# Main class
class ImageProcessorMenu:

	def __init__(self):
		# String of accepted file types for use throughout application
		self.defaultValidFileExtensionsString = ".png, .gif, .dcm, .jpg, .jpeg, .jpe, .jp2, .ome.fif, .ome.tiff, .ome.tf2, .ome.tf8, .ome.bft, .ome, .mov, .tif, .tiff, .tf2, .tf8, .btf, .v3draw, .wlz"
		# This will be set depending on the contents of the users acceptedFileExtensions.txt
		self.validFileExtensionsString = ""
		# Path for the stored accepted extension file
		self.acceptedExtensionFile = IJ.getDir("plugins") + "Medical_Image/acceptedFileExtensions.txt"

		# Path for the stored text file
		self.pathFile = IJ.getDir("plugins") + "Medical_Image/user_paths.txt"

		# Set frame size
		frameWidth, frameHeight = 550, 350
		# Set button size
		buttonWidth, buttonHeight = 130, 25
		
		# Create frame
		self.frame = JFrame("Medical Image Processing")
		self.frame.setSize(frameWidth, frameHeight)
		self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		# Add a panel to the frame
		pnl = JPanel()
		pnl.setBounds(10,10,frameWidth,frameHeight)
		#pnl.setLayout(BoxLayout(BoxLayout.LINE_AXIS)
		self.frame.add(pnl)

		# Add a textfield to the frame to display the input directory
		self.inputTextfield = JTextField(30)
		self.inputTextfield.setText("Select Import Directory")
		pnl.add(self.inputTextfield)

		# Add a browse button to the frame for an input directory 
		inputButton = JButton('Select Input',actionPerformed=self.optionMenuPopup)
		inputButton.setPreferredSize(Dimension(buttonWidth, buttonHeight))
		pnl.add(inputButton)

		# Add a textfield to the frame to display the output directory
		self.outputTextfield = JTextField(30)
		self.outputTextfield.setText("Select Output Directory")
		pnl.add(self.outputTextfield)

		# Add a browse button to the frame to search for an output directory
		outputButton = JButton('Select Output',actionPerformed=self.setOutputDirectory)
		outputButton.setPreferredSize(Dimension(buttonWidth, buttonHeight))
		pnl.add(outputButton)

		# Add a textfield to the frame to display the macro file directory
		self.macroSelectTextfield = JTextField(30)
		self.macroSelectTextfield.setText("Select Macro File")
		self.macroSelectTextfield.setName("Macro File")
		pnl.add(self.macroSelectTextfield)

		# Add a browse button to the frame to search for a macro file
		macroFileSelectButton = JButton('Select Macro',actionPerformed=self.setMacroFileDirectory)
		macroFileSelectButton.setPreferredSize(Dimension(buttonWidth, buttonHeight))
		pnl.add(macroFileSelectButton)

		# Add a textfield to the frame to display the R Script directory
		self.rScriptSelectTextfield = JTextField(30)
		self.rScriptSelectTextfield.setText("Select R Script")
		self.rScriptSelectTextfield.setName("R Script")
		pnl.add(self.rScriptSelectTextfield)

		# Add a browse button to the frame to search for an R Script
		rScriptSelectButton = JButton('Select R Script',actionPerformed=self.setRScriptDirectory)
		rScriptSelectButton.setPreferredSize(Dimension(buttonWidth, buttonHeight))
		pnl.add(rScriptSelectButton)

		# Add separator line for user friendliness
		sep = JSeparator(SwingConstants.HORIZONTAL)
		sep.setPreferredSize(Dimension(frameWidth - 35,5))
		pnl.add(sep)

		# Save south-most panel as globally accessible object in order to iterate through pertinent components
		ImageProcessorMenu.fileSpecificationsPanel = pnl

		# Label for textfield below
		self.extensionLabel = JLabel("File Extensions:")
		pnl.add(self.extensionLabel)

		# ComboBox for selected file extension delimeter
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

		# Blank spaces for alignment purposes
		self.blankLbl = JLabel("     ")
		pnl.add(self.blankLbl)

		# Label for textfield below
		self.containsLabel = JLabel("File Name Contains:")
		pnl.add(self.containsLabel)

		# Add a textfield to the frame to get the specified text that a filename must contain
		self.containsTextfield = JTextField(30)
		pnl.add(self.containsTextfield)

		# Add a checkbox which determines whether or not to copy the original image file(s) to the newly created directory/directories
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

		# Create a generalize macro menu option
		createGeneralMacro = JMenuItem("Create Generalized Macro File", None, actionPerformed=self.generalizePrompts)
		createGeneralMacro.setToolTipText("Create a macro file that can be used in the processing pipeline using an existings macro file")
		file.add(createGeneralMacro)

		# Create menu option to change the path to RScript.exe
		changeRPath = JMenuItem("Change R Path", None, actionPerformed=self.changeRPath)
		changeRPath.setToolTipText("Specify The Location of RScript.exe (Contained in the R Installation Directory by Default)")
		file.add(changeRPath)

		# Create menu option to run the r script on the csv files in the output directory
		runRWithoutImageProcessing = JMenuItem("Run R Script Without Processing Images", None, actionPerformed=self.runRWithoutImageProcessing)
		runRWithoutImageProcessing.setToolTipText("Runs the selected R script on already created .csv files")
		file.add(runRWithoutImageProcessing)

		# Create menu option to modify the default r script
		basicRModifier = JMenuItem("Create basic R Script",None, actionPerformed=self.basicRModifier)
		basicRModifier.setToolTipText("Load a csv file and select two categories to be used in a scatter plot")
		file.add(basicRModifier)

		# Create menu option to add file extensions to the list of accepted types
		addAcceptedFileExtension = JMenuItem("Add Accepted File Extension...", None, actionPerformed=AddFileExtensionMenu)
		addAcceptedFileExtension.setToolTipText("Add a Specified File Extension to the List of Accepted Types")
		file.add(addAcceptedFileExtension)

		# Create an exit menu option, Will close all windows associated with fiji
		fileExit = JMenuItem("Exit", None, actionPerformed=self.onExit)
		fileExit.setToolTipText("Exit application")
		file.add(fileExit)

		# Add the menu to the frame
		menubar.add(file)
		self.frame.setJMenuBar(menubar)

		# Disable file extension textfield off the bat
		self.setExtensionTextfieldEnabled("All File Types")

		# Show the frame, done last to show all components
		self.frame.setResizable(False)
		self.frame.setVisible(True)

		# Find the R executable
		self.findR(False)
		
		# Check if user has file containing accepted file extensions
		self.checkAcceptedExtensionsFile()

	# Closes the program
	def onExit(self, event):
		System.exit(0)

	def checkPathFile(self):
		if not os.path.exists(self.pathFile):
			# Create the user path file, and write empty file paths
			pathFile = open(self.pathFile, "w")
			pathFile.write("inputPath\t\r\n")
			pathFile.write("outputPath\t\r\n")
			pathFile.write("macroPath\t\r\n")
			pathFile.write("rPath\t\r\n")
			pathFile.write("rScriptPath\t\r\n")
			pathFile.close()

	# Checks to see if the file Medical_Image/acceptedFileExtensions.txt exists within FIJI's plugins directory
	def checkAcceptedExtensionsFile(self):
		# File does not exist
		if not os.path.exists(self.acceptedExtensionFile):
			# Create the user path file, and write empty file paths
			extFile = open(self.acceptedExtensionFile, "w")
			# Get default accepted file extensions
			defaultExtensions = self.defaultValidFileExtensionsString.split(',')
			for ext in defaultExtensions:
				extFile.write(ext.strip() + ", ")
			self.validFileExtensionsString = self.defaultValidFileExtensionsString
			extFile.close()
		# File exists
		else:
			file = open(self.acceptedExtensionFile, "r")
			# Temporary string for concatenation of file contents
			tmp = ""
			# Get extensions from file, concatenate to string
			for line in file:
				tmp = tmp + line
			self.validFileExtensionsString = tmp
			file.close()

		# Update tool tip text to reflect all valid file extensions
		self.extensionTextfield.setToolTipText("Valid File Types: [" + self.validFileExtensionsString + "]")

	# Read in the data from the path file, return as a dictionary
	def readPathFile(self):
		returnDictionary = {
			"inputPath": "",
			"outputPath": "",
			"macroPath": "",
			"rPath": "",
			"rScriptPath": ""}
		# Open the file as read-only
		pathFile = open(self.pathFile, 'r')
		# Take each line, split along delimeter, and store in dictionary
		for line in pathFile:
			# Split on tab character
			split = line.split("\t")
			# Update the dictionary only if splitting shows there was a value stored
			if len(split) > 1:
				returnDictionary[split[0]] = split[1].strip()
		pathFile.close()
		return returnDictionary

	def findR(self, change):
		# Get rPath from the path file
		# Requires that the path file exists
		self.checkPathFile()
		rPath = self.readPathFile()["rPath"]
		# If it found one, set the global variable and prepopulate directories, else further the search
		if rPath and not change:
			rcmd = rPath
			self.prepopulateDirectories()
		else:
			rcmd = None
			# Look for the Rscript command. First, try known locations for OS X, Linux, and Windows
			osxdir, linuxdir, windowsdir = "/usr/local/bin/Rscript", "/usr/bin/Rscript", "C:/Program Files/R" 
			if os.path.exists(osxdir) and not change:
				rcmd = osxdir
			elif os.path.exists(linuxdir) and not change:
				rcmd = linuxdir
			elif os.path.exists(windowsdir) and not change:
				# Set the R command to the latest version in the C:\Program Files\R folder
				try:
					rcmd = '"' + windowsdir + "/" + os.listdir(windowsdir)[-1] + '/bin/Rscript.exe"'
				except IndexError:
					# If the R directory exists, but has no subdirectories, then an IndexError happens
					# We don't care at this point, we'll just pass it over without setting rcmd.
					pass
			# If none of those work
			if not rcmd:
				message = ("No R path found. You will be asked to select the Rscript executable.\n"
					"On Windows systems, RScript.exe is found in the \\bin\\ folder of the R installation.\n"
					"On OS X, Rscript is usually found in /usr/local/bin/.\n"
					"On Linux, Rscript is usually found in /usr/bin.")
				if not change:
					JOptionPane.showMessageDialog(self.frame, message)
				chooseFile = JFileChooser()
				chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
				# Verify that the selected file is "Rscript" or "Rscript.exe"
				notR = True
				while notR:
					ret = chooseFile.showDialog(self.frame, "Select")
					if chooseFile.getSelectedFile() is not None and ret == JFileChooser.APPROVE_OPTION:
						r = chooseFile.getSelectedFile().getPath()
						if r[-7:] == "Rscript" or r[-11:] == "Rscript.exe":
							rcmd = r
							notR = False
						else:
							JOptionPane.showMessageDialog(self.frame, "The selected file must be Rscript or Rscript.exe")
					# If 'cancel' is selected then the loop breaks
					if ret == JFileChooser.CANCEL_OPTION:
						notR = False
		self.rcommand = rcmd
		
	# Enables/Disables the file extension textfield based on the user's selected delimiter
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
			# Text will not clear if the user has specified extensions and has changed delimiter category
			if (extTextfield.getText() == "Example: .jpg, .png"):
				extTextfield.setText("")

	# Wrap method call so that it is callable outside this class' scope
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
		# TODO: combine statements
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
			fileContents = re.sub(r"save=[^\s\"]*\\",r"save=FILEPATH/", fileContents)

			# Replace the bio-formats exporter directory path with FILPEPATH followed by text used to inidcate
			# 	what processing was done on the image and IMAGENAME
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)IMAGENAME",r"save=[FILEPATH/\1IMAGENAME]", fileContents)

			# Replace the save results directory path with FILEPATH
			fileContents = re.sub("saveAs\(\"Results\", \".*\\\\", r'saveAs("Results", "FILEPATH/../', fileContents)

			# Replace the save text directory path with FILEPATH
			fileContents = re.sub("saveAs\(\"Text\", \".*\\\\", r'saveAs("Text", "FILEPATH/../', fileContents)

			# Replace all places where the image name without a file extension appears with NOEXTENSION
			fileContents = re.sub(fileName, "NOEXTENSION", fileContents)

			# Do not believe this is necessary, will keep till tested
			fileContents = re.sub(r"save=FILEPATH\\([^\s\"]*)NOEXTENSION([^\s\"]*)",r"save=[FILEPATH/\1NOEXTENSION\2]", fileContents)

			# Replace all paths found in the open command with INPUTPATH\\IMAGENAME
			fileContents = re.sub('open\("[^"]*\\IMAGENAME"','open("INPUTPATH/IMAGENAME"', fileContents)

			# Replace all paths found using run("save") with path FILEPATH\\IMAGENAME for instances that use the same file extension and FILEPATH\\NOEXTENSION for different file extensions
			fileContents = re.sub(r'run\("Save", "save=[^"]*\\([^"]*)IMAGENAME"', 'run("Save", "save=[FILEPATH/\1IMAGENAME]"', fileContents)
			fileContents = re.sub(r'run\("Save", "save=[^"]*\\([^"]*)NOEXTENSION([^"]*)"', 'run("Save", "save=[FILEPATH/\1NOEXTENSION\2]"', fileContents)

			# Replace all paths found using saveAs with path FILEPATH\\IMAGENAME for instances that use the same file extension and FILEPATH\\NOEXTENSION for different file extensions
			fileContents = re.sub(r'saveAs\([^,]*, "[^"]*\\([^"]*)IMAGENAME"\)', 'saveAs(\1, "FILEPATH/\2IMAGENAME")', fileContents)
			fileContents = re.sub(r'saveAs\([^,]*, "[^"]*\\([^"]*)NOEXTENSION([^"]*)"\)', 'saveAs(\1,"FILEPATH/\2NOEXTENSION\3")', fileContents)

			# Inserts code to save the images if no save commands are found in the original macro file
			if fileContents.find("Bio-Formats Exporter") == -1 and fileContents.find("saveAs(") == -1 and fileContents.find('run("Save"') == -1:
				# Split the macro by ; and add the text ;saveChanges(); inbetween each split to save any images changes that might have occured
				# This calls the function saveChanges() defined in the macro
				listOfLines = fileContents.split(";")
				fileContents = ""
				for line in listOfLines:
					if re.match("run.*",line):
						command = re.sub(r'run\("([^"]*)"[^\)]*\)', r'\1',line).replace(".","").replace(" ","_")
					else:
						command = "unknown"
					fileContents = fileContents + line + ";" + "saveChanges(\"" + command + "\");" + 'run("Press Enter", "reset");'
			else:
				fileContents = fileContents.replace(";",';saveResults();run("Press Enter", "reset");')
			fileContents = 'run("Press Enter", "start");' + fileContents + 'run("Press Enter", "stop");'


			# Inserts in import function if the user did not use one
			if fileContents.find("Bio-Formats Importer") == -1 and fileContents.find("open(") == -1:
				# Import the image using the bio-formats importer
				importCode = ('IJ.redirectErrorMessages();'
							  'open("INPUTPATH");'
							  'if(nImages < 1){'
								  'run("Bio-Formats Importer", "open=[INPUTPATH] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT");'
								  'if(is("composite") == 1){'
								  	  # Merge the image into one channel, instead of three seperate red, green, and blue channels
									  'run("Stack to RGB");'
									  # Remember the id of the new image
									  'selectedImage = getImageID();'
									  # Close the seperate channel images
									  'for (i=0; i < nImages; i++){ '
									  	'selectImage(i+1);'
									  	'if(!(selectedImage == getImageID())){'
									  		'close();'
									  		'i = i - 1;'
									  	'}'
									  '}'
									  # Reselect the new image
									  'selectImage(selectedImage);'
									  # Rename window the file name (removes (RGB) from the end of the file window)
									  'rename(getInfo("image.filename"));'
								  '}'
							  '}')

				fileContents = importCode + fileContents

							  # Checks if image is has a valid extension, if not, replace it with .tif
			functionToSave = ('function getSaveName(image){'
								# Name of the file
								'name = substring(image, 0, indexOf(image,"."));'
								# Extension
								'ext = substring(image, indexOf(image,"."));'
								# Extensions supported by Bio-Formats-Exporter
								'validExts = ".jpg, .jpeg, .jpe, .jp2, .ome.fif, .ome.tiff, .ome.tf2, .ome.tf8, .ome.bft, .ome, .mov, .tif, .tiff, .tf2, .tf8, .btf, .v3draw, .wlz";'
								# Checks if ext is in validExts
								'if(indexOf(validExts, ext) == -1){'
									'image = name + ".tif";'
								'}'
								# Return same string passed in, or same name with .tif extension
								'return image;'
							  '}'
							  # Creates the column name in the results window and adds the imageName to each record
							  'function saveResults(){'
							    # Checks if a results window is open	
								'if (isOpen("Results")) {'
									# Loop for every record in the results window
									'for(i=0;i<getValue("results.count");i++){'
										# Add the imagename to the record
										'setResult("Image Name", i, List.get(getImageID()));'
										'setResult("Base Image", i, "IMAGENAME");'
									'}'
									'selectWindow("Results");'
									# Strip the extension from the file name and save the results as the imagename.csv
									'saveAs("Results", "FILEPATH/../" + substring(List.get(getImageID()),0,indexOf(List.get(getImageID()),".")) +".csv");'
									# Close the results window
									'run("Close");'
								'}'
							  '}'
							  # Add the function saveChanges() to the macro to check for any changes in the images that need to be saved
							  'function saveChanges(command){'
								# Checks if an image is open
								'if(nImages != 0){'
									# Store the id of the open image to reselect it once the process is over
									'selectedImage = getImageID();'
									'for (i=0; i < nImages; i++){ '
										'selectImage(i+1);'
										# Get the id of the image
										'imageID = getImageID();'
										# Checks if the imageID exists in the list, if not we need to create an entry for it
										# List uses key,value pairs, in this use case, the key is the imageID, the value is the imageName
										'if(List.get(imageID) == ""){'
											# If there was no previous image set the name of the file to its window title
											'if(List.get("previousImage") == ""){'
												'List.set(imageID,getTitle());'
											'}'
											# Otherwise make it its window title stripped of the extension, followed by the name of the previous image
											'else{'
												'title = replace(getTitle(), " ", "_");'
												'if(indexOf(title, "_", indexOf(title, ".")) != -1){'
													'title = substring(title, indexOf(title, "_", indexOf(title, ".")) + 1) + substring(title, 0, indexOf(title, "_", indexOf(title, ".")));'
												'}'
												'List.set(imageID, substring(title,0,indexOf(title,".")) + "_" + List.get(List.get("previousImage")));'
											'}'
										'}'
										'title = replace(List.get(imageID), " ", "_");'
										# If anything exists after the extension, move it to the front of the image name instead
										'if(indexOf(title, "_", indexOf(title, ".")) != -1){'
											'title = substring(title, indexOf(title, "_", indexOf(title, ".")) + 1) + substring(title, 0, indexOf(title, "_", indexOf(title, ".")));'
										'}'
										'title = getSaveName(title);'
										# If file doesn't exist, save it
										'if(File.exists("FILEPATH/" + title) != 1){'
											'run("Bio-Formats Exporter", "save=[FILEPATH/" + title + "]" + " export compression=Uncompressed");'
											'setOption("Changes", false);'
										'}'
										# If changes have been made to the image, save it
										'if(is("changes")){'
											'title = command + "_" + title;'
											'if(File.exists("FILEPATH/" + title) == 1){'
												# Name without extension
												'name = substring(title, 0, indexOf(title,"."));'
												# Filename counter
												'titleIteration = 0;'
												# File extension
												'ext = substring(title, indexOf(title, "."));'
												# While the file exists, increment the counter to produce a different name
												'while(File.exists("FILEPATH/" + name + "(" + titleIteration + ")" + ext) == 1){'
													'titleIteration = titleIteration + 1;'
												'}'
												# Name of the file to export
												'title = name + "(" + titleIteration + ")" + ext;'
												'run("Bio-Formats Exporter", "save=[FILEPATH/" + title + "]" + " export compression=Uncompressed");'
											'}'
											'else{'
												'run("Bio-Formats Exporter", "save=[FILEPATH/" + title + "]" + " export compression=Uncompressed");'
											'}'
											# Change the name of the image in the List
											'List.set(imageID, title);'
											# Mark file has no changes
											'setOption("Changes", false);'
										'}'
									'}'
									# Select the image that was originally selected
									'selectImage(selectedImage);'
									# Save the results windows if its open
									'saveResults();'
									# Set the previous image to the selectedImage id
									'List.set("previousImage", selectedImage);'
								'}'
							'}')
			fileContents = functionToSave + fileContents

			# Closes any open images
			fileContents = fileContents + 'if(nImages != 0){for (i=0; i < nImages; i++){selectImage(i+1);close();i=i-1;}'

			# Create the general macro file and write the generalized text to it, use a file browswer to select where to save file
			fileChooser = JFileChooser();
			if fileChooser.showSaveDialog(self.frame) == JFileChooser.APPROVE_OPTION:
				path = fileChooser.getSelectedFile().getPath()
				if path[-4:] != ".ijm":
					path = path + ".ijm"
				newMacro = File(path)

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
		self.setDirectory("Input", None)

	# Sets the output directory
	def setOutputDirectory(self, event):
		self.setDirectory("Output", None)

	# Sets the macro file directory
	def setMacroFileDirectory(self,event):
		self.setDirectory("Macro File", None)

	# Sets the R script directory
	def setRScriptDirectory(self, event):
		self.setDirectory("R Script", None)

	# Sets the R Path (RScript.exe) directory
	def setRPathDirectory(self, event):
		self.setDirectory("R Path", None)

	# Action listener for Change R Path menu option
	def changeRPath(self, event):
		self.findR(True)

	# Creates a filechooser for the user to select a directory for input or output
	# @param directoryType	Determines whether or not to be used to locate the input, output, macro file, or R script directory
	def setDirectory(self, directoryType, savedFilePath):
		# User has no previously saved directory paths, open the file chooser
		if savedFilePath is None:
			# Creates a file chooser object
			chooseFile = JFileChooser()

			if (directoryType == "Input" or directoryType == "Output"):
				# Allow for selection of directories
				chooseFile.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
				# Jump to the user's previously selected directory location
				if (directoryType == "Input" and not self.inputTextfield.getText() == "Select Input Directory"):
					chooseFile.setCurrentDirectory(File(self.inputTextfield.getText()))
				elif (directoryType == "Output" and not self.outputTextfield.getText() == "Select Output Directory"):
					chooseFile.setCurrentDirectory(File(self.outputTextfield.getText()))
			else:
				# Allow for selection of files
				chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
				# Jump to the user's previously selected directory location
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
		# User has data for previously saved directories, populate the text fields and global variables with pertinent information
		else:
			# Get the file from specified path
			file = File(savedFilePath)

			# Only populate the path to the directory if the directory itself actually exists (user may have deleted it)
			if (os.path.exists(file.getPath())):
				# Set directory based on type
				if (directoryType == "Input"):
					self.inputDirectory = file
					self.inputTextfield.setText(file.getPath())
					self.urlLocation = None
				elif directoryType == "Output":
					self.outputDirectory = file
					self.outputTextfield.setText(savedFilePath)
				elif directoryType == "Macro File":
					self.macroDirectory = file
					self.macroSelectTextfield.setText(savedFilePath)
				elif directoryType == "R Path":
					self.rcommand = savedFilePath
				elif directoryType == "R Script":
					self.rScriptDirectory = file
					self.rScriptSelectTextfield.setText(savedFilePath)

				self.shouldEnableStart()

	def shouldEnableStart(self):
		# Enable the start button if both an input and output have been selected
		try:
			if ((self.inputDirectory is not None or self.urlLocation is not None) and (self.outputDirectory is not None)):
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

		#Do not start running if directory contains no images
		if (len(self.inputDirectory.listFiles()) > 0):
			self.runMacro()
		else:
			self.showErrorDialog("ERROR - Directory Contains No Images", "Selected Directory is Empty.  Please Choose a Directory That Contains At Least One Image")

	# Downloads each image in the file of image urls
	def downloadFiles(self, filename):
		# Make the input directory the location of the downloaded images
		self.inputDirectory = self.outputDirectory.getPath() + "/originalImages/"
		self.inputDirectory = File(self.inputDirectory)
		self.inputDirectory.mkdirs()
		# Save each image in the file
		for line in open(filename):
			try:
				path = self.inputDirectory.getPath().replace("\\","/") + '/' + line[line.rfind('/') + 1:].replace("/","//")
				urlretrieve(line.strip(), path.strip())
			except:
				# JAVA 7 and below will not authenticate with SSL Certificates of length 1024 and above
				# no workaround I can see as fiji uses its own version of java
				print "unable to access server"

	# Runs the R script selected by the user
	# If no R script was selected, do nothing
	def runRScript(self, scriptFilename, outputDirectory):
		# If the path to Rscript is not set, set it
		if not self.rcommand:
			findR(False)

		path = scriptFilename.getPath()
		# Checks if the path to RScript includes a quote as the first character
		# If it does, then the scriptFilename must be encapsulated in quotes
		# This is necessary for filepaths with spaces in them in windows

		# Makes sure rcommand is surrounded by quotes on windows
		if ".exe" in self.rcommand and self.rcommand[0:1] != '"':
			self.rcommand = '"' + self.rcommand + '"'

		# Makes sure arguments for the command line command are in quotes on windows
		if ".exe" in self.rcommand:
			scriptFilename = '"' + scriptFilename.getPath() + '"'
			outputDirectory = '"' + outputDirectory.getPath() + '"'

		# Runs the command line command to execute the r script
		# shell=True parameter necessary for *nix systems
		LogStream.redirectSystem()
		call("%s %s %s" % (self.rcommand, scriptFilename, outputDirectory), shell = True)
		if re.match(".*is not recognized.*",IJ.getLog()):
			call("%s %s %s" % (self.rcommand, scriptFilename, outputDirectory))

	# Runs the macro file for each image in the input directory
	def runMacro(self):
		# Accepted file types
		self.validFileExtensions = self.validFileExtensionsString.split(", ")
		# Add blank string to list in case user does not specify file extensions
		self.validFileExtensions.append("")
		# Get the user's selected delimiter
		self.choice = self.delimeterComboBox.getSelectedItem()

		# Get user's desired file extensions
		# No need to get selected extensions if user wants all file types or has not specified any extensions
		if (self.choice == "All File Types" or (self.extensionTextfield.getText() == "")):
			self.selectedExtensions = self.validFileExtensions
		# User has chosen to include/exclude files of certain types
		else:
			self.selectedExtensions = self.extensionTextfield.getText()
			self.selectedExtensions = self.selectedExtensions.lower()
			self.selectedExtensions = self.selectedExtensions.split(", ")

			# Validation routine to ensure selected file extensions are valid and comma seperated
			if not (self.validateUserInput(self.extensionTextfield.getName(), self.selectedExtensions, self.validFileExtensions)):
				return

		# Get file name contains pattern
		self.containString = self.containsTextfield.getText()

		# Location of the generalized macro function, this will be a prompt where the user selects the file
		self.macroFile = File(self.macroDirectory.getPath())

		# Validation routine to ensure selected macro file is actually a macro file (file extension = '.ijm')
		if not (self.validateUserInput(self.macroSelectTextfield.getName(), [self.macroFile.getName()[-4:]], [".ijm"])):
			return

		# Location of R Script
		if not (self.rScriptSelectTextfield.getText() == "Select R Script"):
			rScript = File(self.rScriptDirectory.getPath())

			# Validation routine to ensure selected R Script is actually an R Script (file extension = '.R')
			if not (self.validateUserInput(self.rScriptSelectTextfield.getName(), [rScript.getName()[-2:]], [".R"])):
				return

		# Gets an array of all the images in the input directory
		listOfPictures = self.inputDirectory.listFiles()

		# Returns images as specified by the user and adds them to a list
		listOfPicturesBasedOnUserSpecs = self.getImagesBasedOnUserFileSpecications(listOfPictures)

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
			self.macroMenu.setProgressBarValue(int(((self.index * 1.0) / len(self.pictures)) * 100))

			# Image to process
			file = self.pictures[self.index]

			# Increase the index indicating which file to be processed next
			self.index = self.index + 1

			# The name of the image without a file extension
			fileName = file.getName()
			if fileName.index(".") > 0:
				fileName = fileName[0: fileName.index(".")]

			# Will determine if user has specified an output directory or url location
			logFileDir = ""

			# Create a folder with the name of the image in the output folder to house any outputs of the macro
			if (self.outputDirectory is not None):
				outputDir = File(self.outputDirectory.getPath() + "/" + fileName)
				logFileDir = self.outputDirectory.getPath() + "/Log.txt"
			else:
				outputDir = File(self.urlLocation.getPath() + "/" + fileName)
				logFileDir = self.urlLocation.getPath() + "/Log.txt"

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
				fileContents = fileContents.replace("FILEPATH", outputDir.getPath().replace("\\","/"))
				fileContents = fileContents.replace("IMAGENAME", file.getName().replace("\\","/"))
				fileContents = fileContents.replace("NOEXTENSION", fileName.replace("\\","/"))
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

			# Make a copy of the original image if the user has chosen to do so
			if (self.copyImageToNewDirectoryCheckBox.isSelected()):
				self.copyOriginalImageToNewDirectory(file, outputDir)

			#Creates a log file (or appends to it if one already exists) which will record processing procedures and other pertinent information
			self.createLogFile(file, logFileDir, outputDir, fileContents)

			self.updateUserPathFile()
		else:
			# Macros are finished running, so show the main menu and dispose
			#	of the progress menu.
			self.frame.setVisible(True)
			self.macroMenu.disposeMenu()

			# Run the R script if one has been selected
			try:
				self.runRScript(self.rScriptDirectory, self.outputDirectory)
			except AttributeError:
				print "No R Script Selected"

	# Creates a generic dialog window to display error messages
	def showErrorDialog(self, title, message):
		self.frameToDispose = GenericDialog("")
		self.frameToDispose.setTitle(title)
		self.frameToDispose.addMessage(message)
		self.frameToDispose.showDialog()

	def validateUserInput(self, inputCategory, userInput, validInputs):
		isValid = True
		errorTitle = ""
		errorMessage = ""

		for ext in userInput:
			if not (ext in validInputs):
				isValid = False

		if not(isValid):
			if (inputCategory == "Extensions"):
				errorTitle = "ERROR - Invalid File Extension Format(s)"
				errorMessage = "Error: One or More of Your Selected File Extensions is Invalid. \n" + "Ensure All Selected File Extensions Are Valid and Seperated by Commas."
			elif (inputCategory == "Macro File"):
				errorTitle = "ERROR - Invalid Macro File"
				errorMessage = "Error: You Have Selected an Invalid Macro File.  Please Ensure Your Selected File Ends With '.ijm'."
			elif (inputCategory == "R Script"):
				errorTitle = "ERROR - Invalid R Script"
				errorMessage = "Erro: You Have Selected an Invalid R Script.  Please Ensure Your Selected File Ends With '.R'."
			elif (inputCategory == "R Path"):
				errorTitle = "ERROR - Invalid R Path"
				errorMessage = "Error: " + "'" + userInput[0] + "'" + " is Not the Correct File.  Please Ensure You Have Navigated to the R Installation Directory and Have Selected 'Rscript.exe'"

			self.showErrorDialog(errorTitle, errorMessage)
		return isValid

	# Copies the original image from the existing directory to the newly created one
	def copyOriginalImageToNewDirectory(self, fileToSave, outputDir):
		try:
			shutil.copy(self.inputDirectory.getPath() + "/" + fileToSave.getName(), outputDir.getPath() + "/" + fileToSave.getName())
		except:
			"some error"

	# Gets values from file specification components within the JPanel and returns images based on user's specifications
	def getImagesBasedOnUserFileSpecications(self, images):
		imagesToReturn = []
		for file in images:
			fileName = file.getName()
			# Check for file extensions
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
						# Check for file name pattern
						if (self.containString in fileName):
							imagesToReturn.append(file)
					# No file name pattern specified
					else:
						imagesToReturn.append(file)
		return imagesToReturn

	# Creates/appends to a log file in the user's specified output directory which will record all processing done on selected images
	def createLogFile(self, img, logFileDir, outputDir, fileContents):
		# Create a txt file for log info
		log = open(logFileDir, 'a')
		log.write(str(datetime.datetime.now()) +' - Results for image: ' + img.getPath() + '\n')

		# If the user has chosen to copy over the original image, record it in log file
		if (self.copyImageToNewDirectoryCheckBox.isSelected()):
				log.write(str(datetime.datetime.now()) +'Copied image to: ' + outputDir.getPath() + '\n')

		# Append each processing operation to the log file
		log.write('Process performed: ' + '\n')
		operationsPerformed = fileContents.split(";")
		for i in operationsPerformed:
			log.write('\t' + str(datetime.datetime.now()) + ' - ' + i + '\n')
		log.write('\n')
		log.write('\n')

		# Close the file
		log.close()

	# Updates a text file containing the file paths for the user's selected input, output, macro file, R installation (.exe) path, and R Script directories
	# This file's data will be used to prepopulate the text fields with the user's last selected directories
	def updateUserPathFile(self):
		# Path to the Medical_Image directory
		pluginDir = IJ.getDir("plugins") + "Medical_Image"

		# Create the file to house the path
		file = File(pluginDir + "/user_paths.txt")
		writer = BufferedWriter(FileWriter(file))

		# Create the contents of the file
		# rPath: Path to R.exe on the users system
		# inputPath: Last used input directory path
		# outputPath: Last used output directory path
		# macroPath: Last used macro file path
		# rScriptPath: Last used r script file path
		contents = "rPath\t" + self.rcommand + "\r\n"
		contents = contents + "inputPath\t" + self.inputDirectory.getPath() + "\r\n"
		contents = contents + "outputPath\t" + self.outputDirectory.getPath() + "\r\n"
		contents = contents + "macroPath\t" + self.macroDirectory.getPath() + "\r\n"

		if not(self.rScriptDirectory is None):
			contents = contents + "rScriptPath\t" + self.rScriptDirectory.getPath() + "\r\n"
		else:	
			contents = contents + "rScriptPath\t\r\n"

		writer.write(contents)
		writer.close()

	# Gets text file containing user's last used file paths
	def getUserPathFile(self):
		directoryNames = ["rPath","inputPath", "outputPath", "macroPath"]
		# Path to the Medical_Image directory
		pluginDir = IJ.getDir("plugins") + "Medical_Image"

		# Get file containing user's saved file paths
		file = File(pluginDir + "\user_paths.txt")
		sc = Scanner(file, "UTF-8")

		# Append file contents to temporary string
		filetxt = ""
		while (sc.hasNext()):
			filetxt = filetxt + sc.nextLine()

		# Replace directory names within string with * in order to correctly extract paths
		for name in directoryNames:
			filetxt = re.sub(name, "*", filetxt)

		# Split tmp string to array.  Each element represents a different path
		paths = filetxt.split("*")

		# Remove trailing and leading whitespace
		for i in range(0, len(paths)):
			paths[i] = paths[i].strip()

		return paths

	# Assign each global path variable to corresponding path from array.  Also change text of each textfield.
	def prepopulateDirectories(self):
		# Get user paths file
		paths = self.readPathFile()		

		# Populate R Path
		if paths['rPath'] != "":
			self.setDirectory("R Path", paths['rPath'])
		# Populate Input Directory Path
		if paths['inputPath'] != "":
			self.setDirectory("Input", paths['inputPath'])
		# Populate Output Directory Path
		if paths['outputPath'] != "":
			self.setDirectory("Output", paths['outputPath'])
		# Populate Macro File Path
		if paths['macroPath'] != "":
			self.setDirectory("Macro File", paths['macroPath'])
		# Populate R Script Path
		if paths['rScriptPath'] != "":
			self.setDirectory("R Script", paths['rScriptPath'])

		self.shouldEnableStart()

	# Adds selected extension(s) to the text file containing the lsit of accepted file types. Also updates the global list variable for valid file types.
	def updateUserAcceptedExtensions(self,extensions):
		# Path to the Medical_Image directory
		pluginDir = IJ.getDir("plugins") + "Medical_Image"

		# Create a txt file for log info
		file = open(pluginDir + "/acceptedFileExtensions.txt", 'a')

		for ext in extensions:
			# Boolean to indicate specified extension is already in the list - no need to add it again
			duplicate = False
			if ext.strip() in self.validFileExtensionsString:
				duplicate = True
			if not (duplicate):
				# write extension to file
				file.write(ext.strip() + ", ")
				# add new extensions to global list
				self.validFileExtensionsString = self.validFileExtensionsString + ", " + ext.strip()

		# Update tool tip text to reflect all valid file extensions
		self.extensionTextfield.setToolTipText("Valid File Types: [" + self.validFileExtensionsString + "]")
		# Close the file
		file.close()

	updateUserAcceptedExtensions = CallableWrapper(updateUserAcceptedExtensions)

	# Runs the r script without having to process the images first
	# requires both the r script directory and output directory
	# If these are not set, will notify user, and prompt user for the locations
	def runRWithoutImageProcessing(self,event):
		try:
			# If the rScriptDirectory and outputDirectory are set, run the r script
			if self.rScriptDirectory != None and self.outputDirectory != None:
				self.runRScript(self.rScriptDirectory, self.outputDirectory)
		except:
			# One of the two directories was not set, show user the error
			self.showErrorDialog("Error","Both an output directory and R script must be selected")
			# If user clicks cancel on error message, don't continue
			if not self.frameToDispose.wasCanceled():
				# Checks if it was the output directory not set, if so prompt the user to set it
				try:
					self.outputDirectory
				except:
					self.setDirectory("Output",None)
				# Checks if it was the r script directory not set, if so prompt the user to set it
				try:
					self.rScriptDirectory
				except:
					self.setDirectory("R Script",None)
				# Run the method again
				self.runRWithoutImageProcessing(self)

	# Prompts the user to select a .csv file
	# Creates a frame that has two drop down menus, one for an x variable and one for a y variable
	# Drop down menus are populated with the column names from the csv file
	# Creates a basic R script using the selected variables
	def basicRModifier(self,event):
		chooseFile = JFileChooser()
		chooseFile.setFileSelectionMode(JFileChooser.FILES_ONLY)
		ret = chooseFile.showDialog(self.frame, "Select csv file")
		if chooseFile.getSelectedFile() is not None and ret == JFileChooser.APPROVE_OPTION:
			if chooseFile.getSelectedFile().getPath()[-4:] == ".csv":
				csvFile = open(chooseFile.getSelectedFile().getPath(), "rt")
				try:
					csvreader = reader(csvFile)
					columns = csvreader.next()
					frame = JFrame("Create Basic R Script")
					frame.setSize(400,150)
					frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
					panel = JPanel()
					panel.setBounds(10,10,400,150)
					frame.add(panel)
					xLabel = JLabel("X Variable:")
					yLabel = JLabel("Y Variable:")
					self.xComboBox = JComboBox()
					self.yComboBox = JComboBox()
					for column in columns:
						self.xComboBox.addItem(column)
						self.yComboBox.addItem(column)
					self.xComboBox.setSelectedIndex(0)
					self.yComboBox.setSelectedIndex(0)
					button = JButton("Ok", actionPerformed=self.errorCheckSelected)
					panel.add(xLabel)
					panel.add(self.xComboBox)
					panel.add(yLabel)
					panel.add(self.yComboBox)
					panel.add(button)
					frame.add(panel)
					frame.show()
				except:
					print "Error"
			else:
				self.showErrorDialog("Error","Must be a .csv file")
				# If user clicks cancel on error message, don't continue
				if not self.frameToDispose.wasCanceled():
					self.basicRModifier(None)

	def errorCheckSelected(self,event):
		if self.xComboBox.getSelectedItem() == " " or self.yComboBox.getSelectedItem() == " ":
			self.showErrorDialog("Error","Both an x and y variable must be selected")
		else:
			self.generateBasicRScript(self.xComboBox.getSelectedItem(), self.yComboBox.getSelectedItem())

	# TODO: implement
	def generateBasicRScript(self, xVariable, yVariable):
		defaultR = open(IJ.getDir("plugins") + "Medical_Image/default.R", "r")
		newR = ""
		for line in defaultR:
			if line[0:1] != "#":
				newR = newR + line
		out = open(IJ.getDir("plugins") + "Medical_Image/testing.R", "w")
		out.write(newR)
		out.close()

	### End of ImageProcessorMenu


# Creates a Window which prompts the user to enter their desired file types to be added to the list of accepted file types
class AddFileExtensionMenu():
	# Gets the user's specified extension(s)
	def getUserInput(self, event):
		# Split each extension to array
		extensions = self.addExtTextfield.getText().split(',')
		ImageProcessorMenu.updateUserAcceptedExtensions(ImageProcessorMenu(), extensions)

	# Window Constructor
	def __init__(self, event):
		# Create frame
		frameWidth, frameHeight = 600, 300
		self.addExtMenuFrame = JFrame("Add File Extension")
		self.addExtMenuFrame.setSize(frameWidth, frameHeight)
		self.addExtMenuFrame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		content = self.addExtMenuFrame.getContentPane()

		# Add a panel to the frame
		pnl = JPanel()
		pnl.setBounds(10,10,frameWidth,frameHeight)
		self.addExtMenuFrame.add(pnl)

		# Add labels to prompt the user
		self.promptUserLbl1 = JLabel("Enter All File Extensions That You Wish to Add to the List of Accepted File Extnensions Below.")
		pnl.add(self.promptUserLbl1)
		self.promptUserLbl2 = JLabel("Ensure that Each Extension is Comma-Seperated: ")
		pnl.add(self.promptUserLbl2)

		# Add a textfield to the frame to get the user's selected file extensions to add
		self.addExtTextfield = JTextField()
		self.addExtTextfield.setPreferredSize(Dimension(175,25))
		self.addExtTextfield.setText("Example: .jpg, .png")
		pnl.add(self.addExtTextfield)

		# Add an 'Add' button to the frame to execute adding the specified extension to the accepted list
		self.addExtBtn = JButton('Add', actionPerformed=self.getUserInput)
		self.addExtBtn.setEnabled(True)
		self.addExtBtn.setPreferredSize(Dimension(150,40))
		pnl.add(self.addExtBtn)

		# Show the frame and disable resizing of it
		self.addExtMenuFrame.setResizable(False)
		self.addExtMenuFrame.setVisible(True)


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

		# Stops the automatic enter pressing
		MacroRunner('run("Press Enter", "stop");')

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
		try:
			self.inter.run(self.macroString)
		except:
			MacroRunner('run("Press Enter", "stop");')
		# Prevents future macros from running if current macro was aborted
		if self.run:
			#ADD FOR FINAL
			#WindowManager.closeAllWindows()
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
	# Start things off.
	ImageProcessorMenu()
