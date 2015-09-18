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

class Example:

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
		ret = chooseFile.showDialog(self.textfield, "Choose file")
		if chooseFile.getSelectedFiles() is not None:
			if len(chooseFile.getSelectedFiles()) != 1:
				self.textfield.text = "Multiple Files"
			else:
				self.textfield.text = chooseFile.getSelectedFile().getPath()
			if ret == JFileChooser.APPROVE_OPTION:
				# Open the file using bio formats plugin
				self.file = chooseFile.getSelectedFiles()
				for x in range(0, len(self.file)):
					tempFile = self.file[x].getPath()
					imps = BF.openImagePlus(tempFile)
					for imp in imps:
						imp.show()

	def onExit(self, event):
		System.exit(0)

	def __init__(self):
		# Create the menu frame with size of 600x300
		self.frame = JFrame("Medical Image Processing")
		self.frame.setSize(600, 300)
		self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

		# Add a panel to the frame
		pnl = JPanel()
		self.frame.add(pnl)

		# Add a textfield to the frame
		self.textfield = JTextField('',30)
		pnl.add(self.textfield)

		# Add a browse button to the frame
		self.browseButton = JButton('Browse',actionPerformed=self.optionMenuPopup)
		pnl.add(self.browseButton)

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

	def optionMenuPopup(self, event):
		menu = JPopupMenu()
		singleImage = JMenuItem("Open image(s)", actionPerformed=self.browseForFile)
		singleImage.setToolTipText("Browse for any number of images to open")
		menu.add(singleImage)
		menu.show(self.browseButton, self.browseButton.getWidth(), 0)
		

if __name__ == '__main__':
	#start things off.
	Example()