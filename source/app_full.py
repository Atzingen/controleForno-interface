# -*- coding: latin-1 -*-
import sys, platform
from PyQt4 import QtGui, QtCore
from tela import Main

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if (platform.system() == 'Darwin'):
        app.setStyle(QtGui.QStyleFactory.create("macintosh"))
    else:
        app.setStyle(QtGui.QStyleFactory.create("plastique"))
    window = Main()
    window.showFullScreen()    ###   full screen (lcd) 5 polegadas
    sys.exit(app.exec_())
