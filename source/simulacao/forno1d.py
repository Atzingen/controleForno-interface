# -*- coding: latin-1 -*-
from __future__ import division
from PyQt4 import QtGui
from PyQt4 import QtCore
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, cm
import scipy.misc
import pylab
import cv2
import graficos

def display_perfilForno(self, T):
    #T = calcula_perfil(30,250,280,260,300,100,350)
    R = gera_matriz_imagem(T)
    T_max, T_min = T.max(), T.min()

    if self.ui.spinBox_forno_max.value() < T_max:
        bar_max = T_max + 10
        self.ui.spinBox_forno_max.setValue(T_max + 10)
    else:
        bar_max = self.ui.spinBox_forno_max.value()
    if self.ui.spinBox_forno_min.value() > T_min:
        bar_min = T_min - 10
        self.ui.spinBox_forno_min.setValue(T_min + 10)
    else:
        bar_min = self.ui.spinBox_forno_min.value()


    self.ui.widget_2.canvas.ax.clear()
    cax = self.ui.widget_2.canvas.ax.imshow(R,label="teste",interpolation='nearest',
                                      aspect='auto', cmap=cm.jet, vmin=bar_min, vmax=bar_max)
    self.ui.widget_2.canvas.ax.axis('off')
    self.ui.widget_2.canvas.fig.savefig(self.caminho_inicial + '/imagens/temperatura.jpg', bbox_inches='tight', pad_inches=0)

    self.ui.widget_2.canvas.ax.axis('on')
    #self.ui.widget_2.canvas.fig.colorbar(cax)
    self.ui.widget_2.canvas.draw()

    perfil = cv2.imread(self.caminho_inicial + '/imagens/temperatura.jpg')
    perfil = perfil[7:-25,27:]

    forno = self.img_forno
    col, lin, _ = forno.shape
    perfil = cv2.resize(perfil,(lin, col))

    pts1 = np.float32([[0,0],[0,col],[lin,col],[lin,0]])
    p1, p2, p3, p4 = [85,120], [380,170], [780,50], [600,40]
    pts2 = np.float32([p1, p2, p3, p4])

    M = cv2.getPerspectiveTransform(pts1,pts2)

    perfil = cv2.warpPerspective(perfil,M,(lin,col))
    perfil = cv2.addWeighted(perfil,0.4,forno,0.6,0)
    cv2.imwrite(self.caminho_inicial + '/imagens/teste-img.jpg',perfil)
    self.ui.label_37.setPixmap(QtGui.QPixmap(self.caminho_inicial + '/imagens/teste-img.jpg').scaled(self.ui.label_37.size(), QtCore.Qt.KeepAspectRatio))

def calcula_perfil(Ta, T1 , T2, T3, R1, R2, R3):
    L = 1.8         # comprimento em metros
    n = 30          # número de elementos finitos
    n_sor = 1.85

    # Pontos com informação do sensor
    p_n1 = int(n/4)
    p_n2 = int(2*n/4)
    p_n3 = int(3*n/4)

    dx = L / (n+1.0)

    fonte = np.ones(n+1)
    fonte[:int(n/3)] = R1
    fonte[int(n/3)+1:int(2*n/3)] = R2
    fonte[int(2*n/3):] = R3

    T = np.ones(n+1)*(2*Ta+T1+T2+T3)/5.0
    T[0] = Ta
    T[p_n1] = T1
    T[p_n2] = T2
    T[p_n3] = T3
    T[-1] = Ta

    for r in range(200):
        for i in range(1,n):
            if i == p_n1: # - 1:
                T[i] = T1
            elif i == p_n2:
                T[i] = T2
            elif i == p_n3:
                T[i] = T3
            else:
                Tn = (T[i-1] + T[i+1])/2.0 + (dx**2)*fonte[i]
                T[i] = T[i] +n_sor*( Tn - T[i] )
    return T

def gera_matriz_imagem(T):
    n = int(T.shape[0])
    R = np.empty([n,n])
    for i in range(n):
        R[:,i] = T[i]
    return R
