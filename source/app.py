# -*- coding: latin-1 -*-
import sys, platform
from PyQt4 import QtGui, QtCore
from tela import Main
import modulo_global

if __name__ == "__main__":
    global caminho_banco
    caminho_banco = modulo_global.caminho_banco()
    print 'start app ', caminho_banco
    app = QtGui.QApplication(sys.argv)
    if (platform.system() == 'Darwin'):
        app.setStyle(QtGui.QStyleFactory.create("macintosh"))
    else:
        app.setStyle(QtGui.QStyleFactory.create("plastique"))
    window = Main()
    window.show()               ###   resolucao fixa ou para hdmi / vnc
    #window.showFullScreen()    ###   full screen (lcd) 5 polegadas
    sys.exit(app.exec_())
