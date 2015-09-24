from javax.swing import JFrame
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import JButton
from javax.swing import JFileChooser
from javax.swing import JMenu
from javax.swing import JMenuBar
from javax.swing import JMenuItem
from javax.swing import JPopupMenu
from java.lang import System
from javax.swing.filechooser import FileNameExtensionFilter
from loci.plugins import BF

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
		self.startButton = JButton('Start', actionPerformed=self.optionMenuPopup)
		self.startButton.setEnabled(False)
		pnl.add(self.startButton)

		# Add a menu to the frame
		menubar = JMenuBar()
		file = JMenu("File")
		fileExit = JMenuItem("Exit", None, actionPerformed=self.onExit)
		fileExit.setToolTipText("Exit application")
		file.add(fileExit)
		menubar.add(file)
		self.frame.setJMenuBar(menubar)

		# Show the frame, done last to show all components
		self.frame.setVisible(True)

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
		print "need to do something here"

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
				else:
					self.outputDirectory = chooseFile.getSelectedFile() 
					self.outputTextfield.setText(chooseFile.getSelectedFile().getPath())
					
				# Enable the start button if both an input and output have been selected
				try:
					if self.inputDirectory is not None and self.outputDirectory is not None:
						self.startButton.setEnabled(True)
				except AttributeError:
					print "Needed to put something here"					

if __name__ == '__main__':
	#start things off.
	ImageProcessorMenu()