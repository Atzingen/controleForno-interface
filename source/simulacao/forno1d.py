# -*- coding: latin-1 -*-
from __future__ import division
from PyQt4 import QtGui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, cm
import scipy.misc
import pylab
import cv2
import graficos

def teste(self):
    print 'teste'
    T = calcula_perfil(200,250,280,260,300,100,350)
    R = gera_matriz_imagem(T)
    self.ui.widget_2.canvas.ax.clear()
    cax = self.ui.widget_2.canvas.ax.imshow(R,label="teste",interpolation='nearest',
                                      aspect='auto', cmap=cm.jet)
    self.ui.widget_2.canvas.fig.colorbar(cax)
    self.ui.widget_2.canvas.draw()
    self.ui.widget_2.canvas.fig.savefig('imagens/temperatura.jpg')
    perfil_temp = cv2.imread('imagens/temperatura.jpg')
    forno = cv2.imread('imagens/forno_layout.png')
    L, A = forno.shape[:2]
    perfil_temp = cv2.resize(perfil_temp,(A, L), interpolation = cv2.INTER_CUBIC)
    dst = cv2.addWeighted(perfil_temp,0.3,forno,0.7,0)
    cv2.imwrite('imagens/teste-img.jpg',dst)
    self.ui.label_37.setPixmap(QtGui.QPixmap("imagens/teste-img.jpg"))

def calcula_perfil(Ta, T1 , T2, T3, R1, R2, R3):
    L = 1.8         # comprimento em metros
    # Ta = 293.1      # Temperatura ambiente
    # T1 = 397.3      # Temperatura no sensor 1
    # T2 = 412.3      # Temperatura no sensor 2
    # T3 = 386.1      # Temperatura no sensor 3

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
