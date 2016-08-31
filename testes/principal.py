# -*- coding: latin-1 -*-
from interface import Ui_MainWindow
from PyQt4 import QtGui, QtCore 
import sys
from externo import *

from functools import partial

global a
a = 2

class Main(QtGui.QMainWindow):
	"""docstring for Main"""
	def __init__(self):
		QtGui.QMainWindow.__init__(self)						# Interface Gráfica			
		self.ui = Ui_MainWindow()   							# Qtdesigner
		self.ui.setupUi(self) 	
		self.ui.pushButton.pressed.connect(partial(func2, [self.ui, 2]))	
		self.ui.pushButton_2.pressed.connect(partial(func3,self))	
	print 'obj', a
	def func1(self):
		self.ui.label.setText("hello")


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Main()
	window.show()
	sys.exit(app.exec_())