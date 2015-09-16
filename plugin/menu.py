from javax.swing import JFrame
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import JButton
from javax.swing import JFileChooser
from ij.io import OpenDialog
from loci.plugins import BF

class Example:

	# Opens an open dialog box for the user to select a file
	# Once selected, the file path is added to the textbox
	def browseForFile(self,event):
		chooseFile = JFileChooser()
		chooseFile.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES)
		ret = chooseFile.showDialog(self.frame, "Choose file")
		if chooseFile.getSelectedFile() is not None:
			self.textfield.text = chooseFile.getSelectedFile().getPath()
			#file = "/Users/curtis/data/0-toucan.png"
			#imps = BF.openImagePlus(file)
			#for imp in imps:
    		#imp.show()

	def __init__(self):
		frame = JFrame("Medical Image Processing")
		frame.setSize(600, 300)
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
		pnl = JPanel()
		frame.add(pnl)
		self.textfield = JTextField('',30)
		pnl.add(self.textfield)
		copyButton = JButton('Browse',actionPerformed=self.browseForFile)
		pnl.add(copyButton)
		frame.setVisible(True)

if __name__ == '__main__':
	#start things off.
	Example()