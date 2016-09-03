# -*- coding: latin-1 -*-
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from functools import partial
from banco_dados import *
import numpy as np
'''
Classes para tela e gráfico.
Como por padrão o Qt4 não possui um objeto de gráfico adequado, é utilizado o matplotlib,
sendo que um objeto de tela comum do qt herdará suas propriedades.
'''

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111) 
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
 
 
class matplotlibWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

def plotar(self):
    ''' Função que plota o gráfico na GUI, utilizando a classe Matplotlib que sobrecarrega a o lable do qt (ver arquivo matplotlibwidgetFile.py) '''
    self.ui.widget.canvas.ax.clear()                                            # Limpa os eixos para plotar novamente
    if self.ui.checkBox_20.isChecked() and (                                    # Verifica se a checkbox do experimento atual esta marcada
        self.experimento_nome is not 'Sem Nome'):                               # Pega o nome do experimento e verifica se é 'Sem nome' ou não.                                                                     
        d = retorna_dados(1,                                                    # Pega os dados no bd   
            experimento=str(self.experimento_nome))
    else:
        delta_t = self.ui.horizontalSlider_8.value()                            # Pega os dados no bd
        d = retorna_dados(delta_t)
    try:
        if np.size(d[:,0]) > 1:                                                     # Adiciona os valores ao eixo do gráfico caso a checkbox do respectivo sensor
            if self.ui.checkBox.isChecked():                                        # esteja marcada
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,3])
            if self.ui.checkBox_2.isChecked():                                      # Repete o procedimento para todos os sensores
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,4])
            if self.ui.checkBox_4.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,5])
            if self.ui.checkBox_3.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,6])
            if self.ui.checkBox_6.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,7])
            if self.ui.checkBox_5.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,8])
            self.ui.widget.canvas.draw()
    except:
        pass

def grafico_update(self):
    ''' Método recursivo. 
    É chamado quando a checkbox de autoupdate do gráfico é ativada.
    A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no 
    spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
    até que a checkbox seja desabilitada ou a conecção seja desfeita. '''
    self.alerta_toolbar("update-grafico")
    if self.ui.checkBox_14.isChecked():                                         # Verifica se a checkbox de plotar o gráfico automaticamente está ativada
        plotar(self)                                                            # Chama a função plotar 
        tempo_delay = 1000*int(self.ui.spinBox_4.value())                       # Tempo até chamar a Thread
        self.timer_grafico.singleShot(tempo_delay,partial(grafico_update,self)) # Chama a própria função de forma recursiva

def tempo_grafico(self):
    '''
    Evento ocorre quando o slider abaixo do gráfico é pressinado.
    - Altera o tempo que será mostrado no gráfico (entre 1 e 99 min)
    em relação ao tempo actual.
    - Chama a função atualiza grafico.
    '''
    valor = self.ui.horizontalSlider_8.value()                                  # Pega o valor do intervalo de tempo do gráfico pelo slider
    texto = 'Intervalor de tempo = ' + str(valor) + ' min'                      # Texto para ser mostrado ao lado do slider com o valor escolhido
    self.ui.label_9.setText(texto)                                              # Altera o texto do lable na GUI