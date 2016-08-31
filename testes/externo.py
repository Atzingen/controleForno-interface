# -*- coding: latin-1 -*-
from interface import Ui_MainWindow
from PyQt4 import QtGui, QtCore 
import sys
from principal import *


def func2(a):
	print "func2"
	janela = a[0]
	janela.label.setText(str(a[1]))


def func3(self):
	teste_externo(self,"teste")


def teste_externo(self,b):
	self.ui.label_2.setText("teste" + str(b))
	print a