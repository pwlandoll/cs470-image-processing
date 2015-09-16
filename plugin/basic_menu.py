from javax.swing import JFrame, JPanel, JTextField, JButton
from ij.io import OpenDialog

class Example:

	# Opens an open dialog box for the user to select a file
	# Once selected, the file path is added to the textbox
	def browseForFile(self,event):
		op = OpenDialog("Select a File", "")
		if op.getDirectory() is not None:
			self.textfield.text = op.getDirectory() + op.getFileName()

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