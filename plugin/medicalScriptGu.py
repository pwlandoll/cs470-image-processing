
from javax.swing import JFrame, JPanel, JTextField, JButton, JLabel
from ij.io import OpenDialog
import ctypes

class Example:
	# Opens an open dialog box for the user to select a file
	# Once selected, the file path is added to the textbox
	def browseForFile(self,event):
		validFileExtensions = [".png", ".jpg", ".gif", ".txt", ".tif"]
		op = OpenDialog("Select a File", "")
		if op.getDirectory() is not None and op.getFileName()[-4:].lower() in validFileExtensions:
			self.textfield.text = op.getDirectory() + op.getFileName()
		else:
			self.frameToDispose = self.MessageBox("Invalid File Format", 
												  "Error:    That File Format is Not Supported.  Please Choose a Valid File Type.",
												  500, 150)

	def __init__(self):
		frame = JFrame("Medical Image Processing")
		frame.setSize(600, 300)
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
		pnl = JPanel()
		frame.add(pnl)
		self.textfield = JTextField('',30)
		pnl.add(self.textfield)
		copyButton = JButton('Browse',actionPerformed=self.browseForFile)
		pnl.add(copyButton)
		frame.setVisible(True)

	#Use this handy method to create dialog windows
	def MessageBox(self, title, msg, width, height):
		frame = JFrame(title)
		frame.setSize(width, height)
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
		pnl = JPanel()
		frame.add(pnl)
		message = JLabel(msg)
		pnl.add(message)
		exitBtn = JButton('Okay', actionPerformed=self.close)
		pnl.add(exitBtn)
		frame.setVisible(True)
		return frame

	def close (self,event):
		self.frameToDispose.dispose()
		print "Hello"

if __name__ == '__main__':
	#start things off.
	Example() 