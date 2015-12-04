from ij import Macro
from java.lang import Thread
from java.lang import Runnable
from java.awt import Robot
from java.awt.event import KeyEvent
from java.util import Timer
from java.util import TimerTask

class PressEnterRunner(Runnable):
	def run(self):
		self.timer = Timer()
		self.start()
		
	def start(self):
		try:
			self.task = PressEnterTask()
			self.task.setRef(self)
			self.timer.schedule(self.task, 10000)
		except AttributeError:
			pass	

	def stop(self):
		try:
			self.timer.cancel()
		except AttributeError:
			pass
		
	def reset(self):
		try:
			self.stop()
			self.start()
		except AttributeError:
			pass

class PressEnterTask(TimerTask):
	def run(self):
		robot = Robot()
		robot.keyPress(KeyEvent.VK_ENTER)
		try:
			self.ref.start()
		except:
			print "Error"

	def setRef(self, ref):
		self.ref = ref

arg = Macro.getOptions()	
if arg != None:
	arg = arg.replace(" ", "")
	runner = PressEnterRunner()
	if arg == "start": 
		Thread(runner).start()
	elif arg == "reset":
		runner.reset()
	elif arg == "stop":
		runner.stop()
	else:
		print "Unexpected arg"



