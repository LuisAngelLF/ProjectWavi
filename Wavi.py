# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 mayo 22:27:06 2020

@author: Luis Angel

6/6/20
Se logro cambio de todas las fucniones principales por metodos

"""

import sys
import time
# ---------- Módulos para graficar con Matplotlib -----------------------------
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
# ------------ Módulos para los Widgets de la apliación------------------------
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout,
                             QTabWidget, QPushButton, QLabel, QAction,
                             QMessageBox, QVBoxLayout, QComboBox,
                             QGroupBox, QCheckBox, QSpinBox)
# ---------- Módulos para establecer imágenes y sus características------------
from PyQt5.QtGui import QIcon, QPixmap
# ---------- Módulo para definir características de los Widgets ---------------
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
# ------------ Módulos para graficar señales y usar métodos númericos ---------
import scipy.signal as signal
import numpy as np
from numpy.fft import fftshift
# import peakutils
import pyqtgraph as pg
import pyqtgraph.exporters
import re  # Usado en metodo actualizaCentro

# Versión de la aplicación
__version__ = '1.0.0'

class VentanaPrincipal(QMainWindow):
    # Variables para guardar los valores de las señales generadas por ambos
    # canales
    signal_osc_CH1 = []
    signal_spc_CH1 = []
    signal_osc_CH2 = []
    signal_spc_CH2 = []
    
    def __init__(self, parent=None):
        
        super(VentanaPrincipal, self).__init__(parent)
        
        # Características de la ventana principal
        titulo = 'Wav-I'
        toplef_y = 40
        toplef_x = 10
        altura = 700
        ancho = 1000
        self.setWindowTitle(titulo)  # Se da título a la ventana
        # Se establecen las medidas de la ventana principal
        self.setGeometry(toplef_x, toplef_y, ancho, altura)
        # Se establce el icono de la aplicación
        self.setWindowIcon(QtGui.QIcon('UA_M.png'))
        
        # ----------------------- MenúSuperior --------------------------------
        # Se crea una variable de tipo atributo para establecer un menú
        # Principal
        menu_superior = self.menuBar()

        # ----------- Se agregan opciones al menú principal -------------------
        salir_menu = menu_superior.addMenu('Salir')
        info_menu = menu_superior.addMenu('Ayuda')
        # ayuda_menu = menu_superior.addMenu('Ayuda')

        # Se crean las características y las acciones, de las opciones,
        # Del menú principal
        accion_salir = QAction(QIcon('exit.png'), '&Salir', self)
        accion_salir.setShortcut('Alt+F4')  # Se crea un atajo con el teclado
        accion_info = QAction(QIcon('info.pgn'), 'Acerca de Wav-I...', self)
        accion_info.setShortcut('Ctrl+A')
        # Se le agrega una acción al menú principal
        salir_menu.addAction(accion_salir)
        info_menu.addAction(accion_info)
        # ---------------------------------------------------------------------
        # Función para las acciones del menú superior 'salir'
        def sal_menu():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle('Wav-I')
            msg.setText('¿Estás seguro que deseas salir')
            msg.addButton('Sí', QMessageBox.AcceptRole)
            msg.addButton('No', QMessageBox.NoRole)
            # Se verifica si el usuario quiere salir o no
            run = msg.exec_()  # Se ejecuta el mensaje
        
            if run == QMessageBox.AcceptRole:
                self.close()   # Se cierra la aplicación
        # Se conecta con la función que cierra la aplicación
        accion_salir.triggered.connect(sal_menu)
        # Función de ayuda
        def inf_menu():
            QMessageBox.about(self, 'Acerca de Wav-I', 'Wav-I versión '
                              + __version__ +
                              '\nUniversidad Autónoma Metropolitana \n'
                              'Unidad Iztapalapa')
            
        # Se conecta con la funcion que brinda información de ayuda
        accion_info.triggered.connect(inf_menu)
        
        # Se ubica en el WidgetCentral al método que inicia las pestañas que
        # Componen a la aplicación
        self.setCentralWidget(self.Tab_run())
        
        # Parámetros iniciales para el canal 1
        self.signal_generador_CH1 = 'Seno'  # Se escoge la señal seno por defecto
        self.A_CH1 = 1                      # Amplitud: 1 V, por defecto
        self.f_CH1 = 1e3                    # Frecuencia: 1000 Hz, por defecto
        self.T_CH1 = 1 / self.f_CH1
        self.fs_CH1 = 250.0 * self.f_CH1      # Frecuencia de muestreo
        self.Ts_CH1 = 1. / self.fs_CH1
        self.fase_CH1 = 0                   # Fase: 0°, por defecto
        self.ofs_CH1 = 0                    # Offset: 0 V, por defecto
        self.cicloT_CH1 = 0.5               # Ciclo de trabajo: 50 %
        self.N_CH1=(4*self.T_CH1)/self.Ts_CH1
        self.graph_key_CH1 = False  # Variable para detener o comenzar la animación
        # Parámetros iniciales para el canal 2
        self.signal_generador_CH2 = 'Seno'  # Se escoge la señal seno por defecto
        self.A_CH2 = 1                      # Amplitud: 1 V, por defecto
        self.f_CH2 = 1e3                    # Frecuencia: 1000 Hz, por defecto
        self.T_CH2 = 1 / self.f_CH2
        self.fs_CH2 = 250.0 * self.f_CH2      # Frecuencia de muestreo
        self.Ts_CH2 = 1. / self.fs_CH2
        self.fase_CH2 = 0                   # Fase: 0°, por defecto
        self.ofs_CH2 = 0                    # Offset: 0 V, por defecto
        self.cicloT_CH2 = 0.5               # Ciclo de trabajo: 50 %
        self.N_CH2=(4*self.T_CH2)/self.Ts_CH2
        self.graph_key_CH2 = False  # Variable para detener o comenzar la animación
    #-------------------------------------------------------------------------------
    # Método para inicializar las pestañas de la aplicación
    def Tab_run(self):
        
        self.crea_tab = QTabWidget()  # Se crea el objeto tab como top level widget
        # Llamamos a cada método que inicia a las pestañas de la aplicación
        self.crea_tab.addTab(self.tab_inicio(), 'Inicio')
        self.crea_tab.addTab(self.tab_gen_fun(), 'GENERADOR DE FUNCIONES')
        self.crea_tab.addTab(self.tab_osc(), 'OSCILOSCOPIO')
        self.crea_tab.addTab(self.tab_esp(), 'ANALIZADOR DE ESPECTROS')
        self.crea_tab.setMovable(True)
        
        # Variables que llevan el conteo de las imagenes guardadas para las
        # tres pestañas
        self.ni_1 = 0       # generador_canal1
        self.ni_2 = 0       # generador_canal2
        self.ni_osc = 0     # osciloscopio
        self.ni_spc = 0     # analizador de espectros
        
        return self.crea_tab  # Regresa el widget con todo lo que incluye
    #----------------------------------------------------------------------------------
    # Método para la pestaña Inicio
    def tab_inicio(self):
        
        # Creamos el objeto que será la pestaña en cuestión y que contendrá
        # a los demás widgets
        tab_inicio = QWidget()
        # Se instancia un objeto de tipo Qlabel
        label_image = QLabel()
        # Se instancia un objeto de tipo QPixmap (imagen) y se carga
        # Una imagen .jpg
        pixmap = QPixmap('UAM.jpg')
        label_image.setPixmap(pixmap)  # Se añade a la etiqueta la imagen .jpg
        label_texto = QLabel(''
        'DIVISIÓN DE CIENCIAS BÁSICAS E INGENIERÍA\n'
        'DEPARTAMENTO DE INGENIERÍA ELÉCTRICA\n'
        'Licenciatura en Ingeniería electrónica\n\n'
        'OSCILOSCOPIO, GENERADOR DE FUNCIONES Y ANALIZADOR DE FUNCIONES PARA '
        'RASPBERRY 3B+\n\n'
        'Asesores responsables: \nDr. Rafael Aguilar Gonzáles\n'
        'Dr. Alfonso Prieto Guerrero\n\n'
        'Aplicación desarrollada por: Andrade Hernández Juan Carlos y '
        'López Flores Luis Ángel\n\n\n'
        'Mostrar que se puede ser feliz es un acto de defensa propia, de '
        'rebeldía. JLCF.')
        label_texto.setFont(QtGui.QFont('Times New Roman', 11,))
        # Se instancia un objeto de tipo QGrid
        grid_inicio = QGridLayout()
        # Se añade la etiqueta a la cuadrícula dándole ubicación en formato de
        # Fila, columna
        grid_inicio.addWidget(label_image, 0, 0, Qt.AlignCenter)
        grid_inicio.addWidget(label_texto, 1, 0, Qt.AlignCenter)

        tab_inicio.setLayout(grid_inicio)  # Se muestra a la cuadrícula
        
        return tab_inicio
    
# =============================================================================
#!!! GENERADOR DE FUNCIONES    
# =============================================================================
    # Método para la pestaña Generador de Funciones
    def tab_gen_fun(self):
        
        tab_gen = QWidget()
 
        # Boton de ayuda para el usuario
        btn_ayuda = QPushButton('Ayuda')
        btn_ayuda.setFont(QtGui.QFont('Times New Roman', 14,
                                           weight=QtGui.QFont.Bold))
        btn_ayuda.setStyleSheet('background-color: #FFF300;'
                                'border: 1px solid black')
        # Función para la acción del botón ayuda
        def ayuda_info():
            # Texto que se muestra cuando se oprime el botón de ayuda
            QMessageBox.about(self,
            'Ayuda', 'Instrucciones de funcionamiento para el generador de '
            'funciones:\n\n1. Debes elegir las características de la señal '
            'que deseas generar, en el siguiente orden: primero la unidad (V, mV,'
            ' Hz, etc.) y después la magnitud (1, 10, 100, etc.)\n'
            '2. Tienes que presionar el boton RUN para generar la señal.\n'
            '3. Para detener la señal generada se presiona el boton STOP.\n'
            '4. Para generar una nueva señal es necesario repetir el punto 1'
            ', de lo contrario no se actualizará la señal.\n\n\n'
            'NOTA: Si no se han seleccionado parametros para generar una señal,'
            ' se utilizaran los siguientes valores por defecto:\n\nFrecuencia      '    
            ' : 1 kHz\nAmplitud (Vp) : 1 V\nFase                  : 0°\n'
            'Offset               : 0 V\nCiclo de Trabajo: 50%')

        btn_ayuda.clicked.connect(ayuda_info)
        
        # Creamos una label para avisar cuando se está generando una nueva
        # señal
        self.aviso_gen_CH1 = QLabel()
        # Se le cambia el tamaño y la fuente al texto de la etiqueta
        self.aviso_gen_CH1.setFont(QtGui.QFont('Times New Roman', 13))
        self.aviso_gen_CH1.setStyleSheet('color: #5E1BF5')
        self.aviso_gen_CH2 = QLabel()
        self.aviso_gen_CH2.setFont(QtGui.QFont('Times New Roman', 13))
        self.aviso_gen_CH2.setStyleSheet('color: #5E1BF5')
        
        # Creamos el grid principal para los botones de la pestaña, CH2
        grid_gen_CH2 = QGridLayout()
        # Creamos el grid principal para los botones de la pestaña, CH1
        grid_gen_CH1 = QGridLayout()
        
        # Se instancia un objeto de tipo QGruopBox para los botones que van a
        # generar a la señal
        groupBox_gen_CH2 = QGroupBox('Elige la señal que deseas generar: CH2')
        groupBox_gen_CH2.setFont(QtGui.QFont('Times New Roman', 12))
        groupBox_gen_CH1 = QGroupBox('Elige la señal que deseas generar: CH1')
        groupBox_gen_CH1.setFont(QtGui.QFont('Times New Roman', 12))
        
        # ------------ Widgets para las características de la señal -----------
        label1_CH1 = QLabel('Tipo de señal: ')
        label1_CH1.setFont(QtGui.QFont('Times New Roman', 11,
                                   weight=QtGui.QFont.Bold))
        # Se instancia un objeto-atributo de tipo QComboBox
        combo1_CH1 = QComboBox()
        combo1_CH1.addItem('Seno')
        combo1_CH1.addItem('Coseno')
        combo1_CH1.addItem('Impulso')
        combo1_CH1.addItem('Cuadrada')
        combo1_CH1.addItem('Diente de sierra')
        combo1_CH1.addItem('Escalón unitario')
        combo1_CH1.addItem('DC')
        combo1_CH1.addItem('Exponencial')
        # combo1_CH1.addItem('Bits aleatorios')
        combo1_CH1.addItem('Triangular')
        
        # Cada que se elige una opción de la caja de contenido, se pasa el
        # Texto que se eligió al método llamado
        combo1_CH1.activated[str].connect(self.seleccion_signal_ch1)
        # Se añaden los widgets al grid
        grid_gen_CH1.addWidget(label1_CH1, 0, 0)
        grid_gen_CH1.addWidget(combo1_CH1, 0, 2)
    
        label1_CH2 = QLabel('Tipo de señal: ')
        label1_CH2.setFont(QtGui.QFont('Times New Roman', 11,
                                       weight=QtGui.QFont.Bold))
        # Se instancia un objeto-atributo de tipo QComboBox
        combo1_CH2 = QComboBox()
        combo1_CH2.addItem('Seno')
        combo1_CH2.addItem('Coseno')
        combo1_CH2.addItem('Impulso')
        combo1_CH2.addItem('Cuadrada')
        combo1_CH2.addItem('Diente de sierra')
        combo1_CH2.addItem('Escalón unitario')
        combo1_CH2.addItem('DC')
        combo1_CH2.addItem('Exponencial')
        # combo1_CH2.addItem('Bits aleatorios')
        combo1_CH2.addItem('Triangular')
        
        #####
        # Cada que se elige una opción de la caja de contenido, se pasa el
        # Texto que se eligió al método llamado
        combo1_CH2.activated[str].connect(self.seleccion_signal_ch2)
        # Se añaden los widgets al grid
        grid_gen_CH2.addWidget(label1_CH2, 0, 0)
        grid_gen_CH2.addWidget(combo1_CH2, 0, 2)
        
        label2_CH1 = QLabel('Amplitud: ')
        label2_CH1.setFont(QtGui.QFont('Times New Roman', 11,
                                   weight=QtGui.QFont.Bold))
        # Se crea una comboBox para los valores de la amplitud
        self.combo2_CH1 = QComboBox()
        # Se permite que se pueda editar el texto de la caja de contenido
        self.combo2_CH1.setEditable(True)
        # Se crea una comboBox para las unidades de la amplitud
        self.combo2_0_CH1 = QComboBox()
        self.combo2_0_CH1.addItem('V')
        self.combo2_0_CH1.addItem('mV')
        self.combo2_0_CH1.setCurrentIndex(0)
        
        #####
        self.combo2_0_CH1.activated[str].connect(self.combo_unid_amp_ch1)
        grid_gen_CH1.addWidget(label2_CH1, 1, 0)
        grid_gen_CH1.addWidget(self.combo2_CH1, 1, 2)
        grid_gen_CH1.addWidget(self.combo2_0_CH1, 1, 4)        
        
        label2_CH2 = QLabel('Amplitud: ')
        label2_CH2.setFont(QtGui.QFont('Times New Roman', 11,
                                   weight=QtGui.QFont.Bold))
        # Se crea una comboBox para los valores de la amplitud
        self.combo2_CH2 = QComboBox()
        # Se permite que se pueda editar el texto de la caja de contenido
        self.combo2_CH2.setEditable(True)
        # Se crea una comboBox para las unidades de la amplitud
        self.combo2_0_CH2 = QComboBox()
        self.combo2_0_CH2.addItem('V')
        self.combo2_0_CH2.addItem('mV')
        self.combo2_0_CH2.setCurrentIndex(0)
        ####

        self.combo2_0_CH2.activated[str].connect(self.combo_unid_amp_ch2)
        grid_gen_CH2.addWidget(label2_CH2, 1, 0)
        grid_gen_CH2.addWidget(self.combo2_CH2, 1, 2)
        grid_gen_CH2.addWidget(self.combo2_0_CH2, 1, 4)
        
        label3_CH1 = QLabel('Frecuencia: ')
        label3_CH1.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un comboBox para los valores de la frecuencia
        self.combo3_CH1 = QComboBox()
        self.combo3_CH1.setEditable(True)
        # Se crea un comboBox para las unidades de la frecuencia
        self.combo3_0_CH1 = QComboBox()
        self.combo3_0_CH1.addItem('MHz')
        self.combo3_0_CH1.addItem('kHz')
        self.combo3_0_CH1.addItem('Hz')
        self.combo3_0_CH1.addItem('mHz')
        self.combo3_0_CH1.addItem('uHz')
        self.combo3_0_CH1.setCurrentIndex(1)
        
        #####
        self.combo3_0_CH1.activated[str].connect(self.combo_unid_frec_ch1)
        grid_gen_CH1.addWidget(label3_CH1, 3, 0)
        grid_gen_CH1.addWidget(self.combo3_CH1, 3, 2)
        grid_gen_CH1.addWidget(self.combo3_0_CH1, 3, 4) 
        
        label3_CH2 = QLabel('Frecuencia: ')
        label3_CH2.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un comboBox para los valores de la frecuencia
        self.combo3_CH2 = QComboBox()
        self.combo3_CH2.setEditable(True)
        # Se crea un comboBox para las unidades de la frecuencia
        self.combo3_0_CH2 = QComboBox()
        self.combo3_0_CH2.addItem('MHz')
        self.combo3_0_CH2.addItem('kHz')
        self.combo3_0_CH2.addItem('Hz')
        self.combo3_0_CH2.addItem('mHz')
        self.combo3_0_CH2.addItem('uHz')
        self.combo3_0_CH2.setCurrentIndex(1)
        
        #####
        self.combo3_0_CH2.activated[str].connect(self.combo_unid_frec_ch2)
        grid_gen_CH2.addWidget(label3_CH2, 3, 0)
        grid_gen_CH2.addWidget(self.combo3_CH2, 3, 2)
        grid_gen_CH2.addWidget(self.combo3_0_CH2, 3, 4)       

        label4_CH1 = QLabel('Fase: ')
        label4_CH1.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un comboBox para los valores del ángulo en la señal
        self.combo4_CH1 = QComboBox()
        self.combo4_CH1.setEditable(True)
        # Se crea un comboBox para las unidades del ángulo de la señal
        self.combo4_0_CH1 = QComboBox()
        self.combo4_0_CH1.addItem('°')
        
        ######
        self.combo4_0_CH1.activated[str].connect(self.combo_unid_fase_ch1)
        grid_gen_CH1.addWidget(label4_CH1, 4, 0)
        grid_gen_CH1.addWidget(self.combo4_CH1, 4, 2)
        grid_gen_CH1.addWidget(self.combo4_0_CH1, 4, 4)

        label4_CH2 = QLabel('Fase: ')
        label4_CH2.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un comboBox para los valores del ángulo en la señal
        self.combo4_CH2 = QComboBox()
        self.combo4_CH2.setEditable(True)
        # Se crea un comboBox para las unidades del ángulo de la señal
        self.combo4_0_CH2 = QComboBox()
        self.combo4_0_CH2.addItem('°')
        #####
        
        self.combo4_0_CH2.activated[str].connect(self.combo_unid_fase_ch2)
        grid_gen_CH2.addWidget(label4_CH2, 4, 0)
        grid_gen_CH2.addWidget(self.combo4_CH2, 4, 2)
        grid_gen_CH2.addWidget(self.combo4_0_CH2, 4, 4)
        
        label5_CH1 = QLabel('Offset: ')
        label5_CH1.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un objeto comboBox para los valores del offset
        self.combo5_CH1 = QComboBox()
        self.combo5_CH1.setEditable(True)
        # Se crea un objeto comboBox para las unidades de los valores del offset
        self.combo5_0_CH1 = QComboBox()
        self.combo5_0_CH1.addItem('V')
        self.combo5_0_CH1.addItem('mV')
        self.combo5_0_CH1.setCurrentIndex(0)
        #####
        self.combo5_0_CH1.activated[str].connect(self.combo_unid_off_ch1)
        grid_gen_CH1.addWidget(label5_CH1, 5, 0)
        grid_gen_CH1.addWidget(self.combo5_CH1, 5, 2)
        grid_gen_CH1.addWidget(self.combo5_0_CH1, 5, 4)
        # Se establece un ancho mínimo a la columna selecionada
        grid_gen_CH1.setColumnMinimumWidth(1, 5)
        grid_gen_CH1.setColumnMinimumWidth(3, 5)
        grid_gen_CH1.setRowMinimumHeight(6, 30)
        # Se dan valores iniciales
        self.combo_unid_amp_ch1('V')
        self.combo_unid_frec_ch1('kHz')
        self.combo_unid_fase_ch1()
        self.combo_unid_off_ch1('V')
        
        label5_CH2 = QLabel('Offset: ')
        label5_CH2.setFont(QtGui.QFont('Times New Roman', 11,
                                        weight=QtGui.QFont.Bold))
        # Se crea un objeto comboBox para los valores del offset
        self.combo5_CH2 = QComboBox()
        self.combo5_CH2.setEditable(True)
        # Se crea un objeto comboBox para las unidades de los valores del offset
        self.combo5_0_CH2 = QComboBox()
        self.combo5_0_CH2.addItem('V')
        self.combo5_0_CH2.addItem('mV')
        self.combo5_0_CH2.setCurrentIndex(0)
        #####
        self.combo5_0_CH2.activated[str].connect(self.combo_unid_off_ch2)
        grid_gen_CH2.addWidget(label5_CH2, 5, 0)
        grid_gen_CH2.addWidget(self.combo5_CH2, 5, 2)
        grid_gen_CH2.addWidget(self.combo5_0_CH2, 5, 4)
        # Se establece un ancho mínimo a la columna selecionada
        grid_gen_CH2.setColumnMinimumWidth(1, 5)
        grid_gen_CH2.setColumnMinimumWidth(3, 5)
        grid_gen_CH2.setRowMinimumHeight(6, 30)
        # Se dan valores iniciales
        self.combo_unid_amp_ch2('V')
        self.combo_unid_frec_ch2('kHz')
        self.combo_unid_fase_ch2()
        self.combo_unid_off_ch2('V')

        # Se instancia un objeto de tipo botón
        self.btn_inicio_CH1 = QPushButton('RUN')
        # Se cambia la fuente y su tamaño al texto del botón
        self.btn_inicio_CH1.setFont(QtGui.QFont('Times New Roman', 15,
                                       weight=QtGui.QFont.Bold))
        # Se cambia el color del botón usando el código de colores
        self.btn_inicio_CH1.setStyleSheet('background-color: #00F212;'
                                 'border: 1px solid black')
        
        #####
        # Se conecta con la función para mostrar un mensaje al usuario
        self.btn_inicio_CH1.clicked.connect(self.aviso_signal_gen_ch1)
        #####
        # Se conecta al botón de inicio con la función que dibuja a la gráfica
        # seleccionada por el usuario
        self.btn_inicio_CH1.clicked.connect(self.dibuja_ch1)

        # Se instancia un objeto de tipo botón
        self.btn_inicio_CH2 = QPushButton('RUN')
        # Se cambia la fuente y su tamaño al texto del botón
        self.btn_inicio_CH2.setFont(QtGui.QFont('Times New Roman', 15,
                                       weight=QtGui.QFont.Bold))
        # Se cambia el color del botón usando el código de colores
        self.btn_inicio_CH2.setStyleSheet('background-color: #00F212;'
                                 'border: 1px solid black')
        #####
        # Se conecta con la función para mostrar un mensaje al usuario
        self.btn_inicio_CH2.clicked.connect(self.aviso_signal_gen_ch2)
        #####
        # Se conecta al botón de inicio con la función que dibuja a la gráfica
        # seleccionada por el usuario
        self.btn_inicio_CH2.clicked.connect(self.dibuja_ch2)
        
        ##### 
        # Se conecta al botón de inicio con una función que guarda las muestras
        # de la señal en un archivo de texto .txt
        self.btn_inicio_CH1.clicked.connect(self.muestras_ch1)
        
        #####
        
        # Se conecta al botón de inicio con una función que guarda las muestras
        # de la señal en un archivo de texto .txt
        self.btn_inicio_CH2.clicked.connect(self.muestras_ch2)
        
        self.btn_parar_CH1 = QPushButton('STOP')
        self.btn_parar_CH1.setFont(QtGui.QFont('Times New Roman', 15,
                                           weight=QtGui.QFont.Bold))
        self.btn_parar_CH1.setStyleSheet('color: #FFFFFF; '
                                     'background-color: #FF0000;'
                                     'border: 1px solid black')
        
        #####
        # Se conecta al botón de terminar con una función que manda un texto de
        # aviso al usuario, porque se detuvo la señal
        self.btn_parar_CH1.clicked.connect(self.aviso_signal_gen_stop_ch1)
        #####
        # Se añaden los botones de inicio y parada, de la señal generada
        grid_gen_CH1.addWidget(self.btn_inicio_CH1, 7, 0)
        grid_gen_CH1.addWidget(self.btn_parar_CH1, 7, 2)
        
        self.btn_parar_CH2 = QPushButton('STOP')
        self.btn_parar_CH2.setFont(QtGui.QFont('Times New Roman', 15,
                                           weight=QtGui.QFont.Bold))
        self.btn_parar_CH2.setStyleSheet('color: #FFFFFF; '
                                     'background-color: #FF0000;'
                                     'border: 1px solid black')
        
        #####
        # Se conecta al botón de terminar con una función que manda un texto de
        # aviso al usuario, porque se detuvo la señal
        self.btn_parar_CH2.clicked.connect(self.aviso_signal_gen_stop_ch2)
        # Se añaden los botones de inicio y parada, de la señal generada
        grid_gen_CH2.addWidget(self.btn_inicio_CH2, 7, 0)
        grid_gen_CH2.addWidget(self.btn_parar_CH2, 7, 2)
        
        # Se crea un grupbox para contener a los botones de 'guardar señal' y
        # 'sacar señal'
        gB_CH2 = QGroupBox()
        # Se crea un grid para estos botones
        grid_gB_CH2 = QGridLayout()
        # Creamo un botón para guardar la señal
        btn_save = QPushButton('Guardar')
        btn_save.setFont(QtGui.QFont('Times New Roman', 14,
                                           weight=QtGui.QFont.Bold))
        btn_save.setStyleSheet('color: #FFFFFF;'
                                   'background-color: #4B9AFC;'
                                     'border: 1px solid black')
        
        #####
         # Se conecta con la función que guarda la señal
        btn_save.clicked.connect(self.save_graph)
        
        # Botón para sacar la señal a un medio físico
        btn_out_CH2 = QPushButton('Habilitar puerto')
        btn_out_CH2.setFont(QtGui.QFont('Times New Roman', 14,
                                           weight=QtGui.QFont.Bold))
        btn_out_CH2.setStyleSheet('background-color: #F88734;'
                                     'border: 1px solid black')
        #####
        btn_out_CH2.clicked.connect(self.out_graph_ch2)
        grid_gB_CH2.addWidget(btn_save, 0, 0, Qt.AlignBottom)
        grid_gB_CH2.addWidget(btn_ayuda, 0, 2, Qt.AlignBottom)
        grid_gB_CH2.addWidget(btn_out_CH2, 0, 4, Qt.AlignBottom)
        grid_gB_CH2.setColumnMinimumWidth(1, 15)
        grid_gB_CH2.setColumnMinimumWidth(3, 15)
        gB_CH2.setLayout(grid_gB_CH2)
        
        #####
        # La caja de grupo es puesta en la cuadrícula correspondiente
        groupBox_gen_CH1.setLayout(grid_gen_CH1)
        
        #####
        # La caja de grupo es puesta en la cuadrícula correspondiente
        groupBox_gen_CH2.setLayout(grid_gen_CH2)
        
        # Se crea un grid principal para incluir a todos los widgets de la
        # pestaña
        main_grid = QGridLayout()
        frame_CH1 = self.frame_graph_ch1()
        frame_CH2 = self.frame_graph_ch2()
        # Se añaden los widgets anteriormente creados
        main_grid.addWidget(frame_CH1, 0, 1, 2, 2, Qt.AlignCenter)
        main_grid.addWidget(frame_CH2, 2, 1, 2, 2, Qt.AlignCenter)
        # Este widget se alinea en el tope superior
        main_grid.addWidget(groupBox_gen_CH1, 0, 0, Qt.AlignLeft)
        main_grid.addWidget(groupBox_gen_CH2, 2, 0, Qt.AlignLeft)
        # Se alinea en el centro vertical
        main_grid.addWidget(self.aviso_gen_CH1, 1, 0, Qt.AlignTop)
        main_grid.addWidget(self.aviso_gen_CH2, 3, 0, Qt.AlignTop)
        # Se añade el groupBox que contiene a los botones de save y out
        main_grid.addWidget(gB_CH2, 4, 0, Qt.AlignCenter)
        
        # La caja de grupo que contiene a las características de la señal
        # es puesta en la pestaña
        tab_gen.setLayout(main_grid)
        
        return tab_gen
    #-----------------------------------------------------------------------------
    # Método para elegir la señal a generar, se para como argumento el
    # nombre de la señal elegida por el usuario
    def seleccion_signal_ch1(self, selsenal):
        # Se cambia el valor a false para poder graficar otra señal pero con 
        # los parámetros anteriores
        self.graph_key_CH1 = False      
        # Se pasa la cadena de texto de la señal elegida a un atributo de
        # la clase
        self.signal_generador_CH1 = selsenal
        # --- Se comprueba si la cadena de texto coincide con el texto dado
        if self.signal_generador_CH1 == 'Seno':
            # Se habilitaran o deshabilitaran botones, dependiendo de las
            # Características de la señal
            self.combo3_CH1.setDisabled(False)
            self.combo4_CH1.setDisabled(False)
            self.combo5_CH1.setDisabled(False)  # se deshabilita el combo5_CH2
            self.combo4_0_CH1.setDisabled(False)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Coseno':
            self.combo3_CH1.setDisabled(False)
            self.combo4_CH1.setDisabled(False)
            self.combo5_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(False)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Impulso':
            self.combo4_CH1.setDisabled(True)  # Se habilita el combo4_CH2
            self.combo5_CH1.setDisabled(True)
            self.combo4_0_CH1.setDisabled(True)
            self.combo3_0_CH1.setDisabled(False)
            self.combo5_0_CH1.setDisabled(True)
        elif self.signal_generador_CH1 == 'Cuadrada':
            self.combo4_CH1.setDisabled(True)
            self.combo5_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
            self.combo3_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Diente de sierra':
            self.combo4_CH1.setDisabled(True)
            self.combo5_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Escalón unitario':
            self.combo3_CH1.setDisabled(False)
            self.combo4_CH1.setDisabled(True)
            self.combo5_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
        elif self.signal_generador_CH1 == 'DC':
            self.combo4_CH1.setDisabled(True)
            self.combo3_CH1.setDisabled(True)
            self.combo5_CH1.setDisabled(False)
            self.combo5_0_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
            self.combo3_0_CH1.setDisabled(True)
        elif self.signal_generador_CH1 == 'Exponencial':
            self.combo4_CH1.setDisabled(True)
            self.combo3_CH1.setDisabled(False)
            self.combo5_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Bits aleatorios':
            self.combo4_CH1.setDisabled(True)
            self.combo3_CH1.setDisabled(False)
            self.combo5_CH1.setDisabled(True)
            self.combo4_0_CH1.setDisabled(True)
            self.combo5_0_CH1.setDisabled(True)
            self.combo3_0_CH1.setDisabled(False)
        elif self.signal_generador_CH1 == 'Triangular':
            self.combo4_CH1.setDisabled(True)
            self.combo3_CH1.setDisabled(False)
            self.combo5_CH1.setDisabled(False)
            self.combo4_0_CH1.setDisabled(True)
            self.combo5_0_CH1.setDisabled(False)
            self.combo3_0_CH1.setDisabled(False)
    #-----------------------------------------------------------------------------------------
    # Método para elegiar la señal a generar, se para como argumento el
    # nombre de la señal elegida por el usuario
    def seleccion_signal_ch2(self, selsenal):
        # Se cambia el valor a false para poder graficar otra señal pero con 
        # los parámetros anteriores
        self.graph_key_CH2 = False
        # Se pasa la cadena de texto de la señal elegida a un atributo de
        # la clase
        self.signal_generador_CH2 = selsenal
        # --- Se comprueba si la cadena de texto coincide con el texto dado
        if self.signal_generador_CH2 == 'Seno':
            # Se habilitaran o deshabilitaran botones, dependiendo de las
            # Características de la señal
            self.combo3_CH2.setDisabled(False)
            self.combo4_CH2.setDisabled(False)
            self.combo5_CH2.setDisabled(False)  # se deshabilita el combo5_CH2
            self.combo4_0_CH2.setDisabled(False)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False) 
        elif self.signal_generador_CH2 == 'Coseno':
            self.combo3_CH2.setDisabled(False)
            self.combo4_CH2.setDisabled(False)
            self.combo5_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(False)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
        elif self.signal_generador_CH2 == 'Impulso':
            self.combo4_CH2.setDisabled(True)  # Se habilita el combo4_CH2
            self.combo5_CH2.setDisabled(True)
            self.combo4_0_CH2.setDisabled(True)
            self.combo3_0_CH2.setDisabled(False)
            self.combo5_0_CH2.setDisabled(True)
        elif self.signal_generador_CH2 == 'Cuadrada':
            self.combo4_CH2.setDisabled(True)
            self.combo5_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
            self.combo3_CH2.setDisabled(False)
        elif self.signal_generador_CH2 == 'Diente de sierra':
            self.combo4_CH2.setDisabled(True)
            self.combo5_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
        elif self.signal_generador_CH2 == 'Escalón unitario':
            self.combo3_CH2.setDisabled(False)
            self.combo4_CH2.setDisabled(True)
            self.combo5_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
        elif self.signal_generador_CH2 == 'DC':
            self.combo4_CH2.setDisabled(True)
            self.combo3_CH2.setDisabled(True)
            self.combo5_CH2.setDisabled(False)
            self.combo5_0_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
            self.combo3_0_CH2.setDisabled(True)
        elif self.signal_generador_CH2 == 'Exponencial':
            self.combo4_CH2.setDisabled(True)
            self.combo3_CH2.setDisabled(False)
            self.combo5_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
        elif self.signal_generador_CH2 == 'Bits aleatorios':
            self.combo4_CH2.setDisabled(True)
            self.combo3_CH2.setDisabled(False)
            self.combo5_CH2.setDisabled(True)
            self.combo4_0_CH2.setDisabled(True)
            self.combo5_0_CH2.setDisabled(True)
            self.combo3_0_CH2.setDisabled(False)
        elif self.signal_generador_CH2 == 'Triangular':
            self.combo4_CH2.setDisabled(True)
            self.combo3_CH2.setDisabled(False)
            self.combo5_CH2.setDisabled(False)
            self.combo4_0_CH2.setDisabled(True)
            self.combo5_0_CH2.setDisabled(False)
            self.combo3_0_CH2.setDisabled(False)
    #----------------------------------------------------------------------------------------
        
    #-----------------------------------------------------------------
    # Metodo para añadir los valores de la amplitud al ComboBox
    def combo_unid_amp_ch1(self, unit):
        self.graph_key_CH1 = False
        # Función que asigna el valor de amplitud a la señal
        def sel_amp_ch1(amp):
            # Se determina si los valores elegidos están dentro del rango de
            # Selección disponible. Si no es así, se les asigna un valor automático
            if 3.0 >= float(amp) >= -3.0 and self.key0_CH1 is True:
                self.A_CH1 = float(amp)
            elif 500.0 >= float(amp) >= -500.0 and self.key0_CH1 is False:
                self.A_CH1 = float(amp) * 0.001
            else:
                self.A_CH1 = 1
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                  ' puede ser usado para generar'
                                  ' una señal.\nPrueba con un va'
                                  'lor dentro del intervalo per'
                                  'mitido.\nSe ha asignado '
                                  'un valor por defecto: 1 V')
        if unit == 'V':
            self.key0_CH1 = True
            # Se eliminan los items de la caja de contenido
            self.combo2_CH1.clear()
            self.combo2_CH1.addItem('3')  # Se añaden items a la caja de contenido
            self.combo2_CH1.addItem('2')
            self.combo2_CH1.addItem('1')
            self.combo2_CH1.addItem('-1')
            self.combo2_CH1.addItem('-2')
            self.combo2_CH1.addItem('-3')
            # Se asigna el lugar (índice) donde  va a comenzar la caja de
            # Contenido
            self.combo2_CH1.setCurrentIndex(2)
            # Se añade un separador a la caja de contenido, a partir de cierto
            # Indice
            self.combo2_CH1.insertSeparator(6)
            # Se manda a llamar al método que conecta con las características
            # De las señales
            self.combo2_CH1.activated[str].connect(sel_amp_ch1)
        elif unit == 'mV':
            self.key0_CH1 = False
            self.combo2_CH1.clear()
            self.combo2_CH1.addItem('Elige un valor')
            self.combo2_CH1.addItem('500')
            self.combo2_CH1.addItem('200')
            self.combo2_CH1.addItem('100')
            self.combo2_CH1.addItem('50')
            self.combo2_CH1.addItem('20')
            self.combo2_CH1.addItem('10')
            self.combo2_CH1.addItem('5')
            self.combo2_CH1.addItem('-5')
            self.combo2_CH1.addItem('-10')
            self.combo2_CH1.addItem('-20')
            self.combo2_CH1.addItem('-50')
            self.combo2_CH1.addItem('-100')
            self.combo2_CH1.addItem('-200')
            self.combo2_CH1.addItem('-500')
            self.combo2_CH1.setCurrentIndex(0)
            self.combo2_CH1.insertSeparator(14)
            self.combo2_CH1.activated[str].connect(sel_amp_ch1)
    #----------------------------------------------------------------------------
        
    #------------------------------------------------------------------------------------
    # Metodo para añadir los valores de la amplitud al ComboBox
    def combo_unid_amp_ch2(self, unit):
        self.graph_key_CH2 = False
        # Función que asigna el valor de amplitud a la señal
        def sel_amp_ch2(amp):
            # Se determina si los valores elegidos están dentro del rango de
            # Selección disponible. Si no es así, se les asigna un valor automático
            if 3.0 >= float(amp) >= -3.0 and self.key0_CH2 is True:
                self.A_CH2 = float(amp)
            elif 500.0 >= float(amp) >= -500.0 and self.key0_CH2 is False:
                self.A_CH2 = float(amp) * 0.001
            else:
                self.A_CH2 = 1
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                  ' puede ser usado para generar'
                                  ' una señal.\nPrueba con un va'
                                  'lor dentro del intervalo per'
                                  'mitido.\nSe ha asignado '
                                  'un valor por defecto: 1 V')
        if unit == 'V':
            self.key0_CH2 = True
            # Se eliminan los items de la caja de contenido
            self.combo2_CH2.clear()
            self.combo2_CH2.addItem('3')  # Se añaden items a la caja de contenido
            self.combo2_CH2.addItem('2')
            self.combo2_CH2.addItem('1')
            self.combo2_CH2.addItem('-1')
            self.combo2_CH2.addItem('-2')
            self.combo2_CH2.addItem('-3')
            # Se asigna el lugar (índice) donde  va a comenzar la caja de
            # Contenido
            self.combo2_CH2.setCurrentIndex(2)
            # Se añade un separador a la caja de contenido, a partir de cierto
            # Indice
            self.combo2_CH2.insertSeparator(6)
            # Se manda a llamar al método que conecta con las características
            # De las señales
            self.combo2_CH2.activated[str].connect(sel_amp_ch2)
        elif unit == 'mV':
            self.key0_CH2 = False
            self.combo2_CH2.clear()
            self.combo2_CH2.addItem('Elige un valor')
            self.combo2_CH2.addItem('500')
            self.combo2_CH2.addItem('200')
            self.combo2_CH2.addItem('100')
            self.combo2_CH2.addItem('50')
            self.combo2_CH2.addItem('20')
            self.combo2_CH2.addItem('10')
            self.combo2_CH2.addItem('5')
            self.combo2_CH2.addItem('-5')
            self.combo2_CH2.addItem('-10')
            self.combo2_CH2.addItem('-20')
            self.combo2_CH2.addItem('-50')
            self.combo2_CH2.addItem('-100')
            self.combo2_CH2.addItem('-200')
            self.combo2_CH2.addItem('-500')
            self.combo2_CH2.setCurrentIndex(0)
            self.combo2_CH2.insertSeparator(14)
            self.combo2_CH2.activated[str].connect(sel_amp_ch2)
    #------------------------------------------------------------------------
        
        
        
    #---------------------------------------------------------------------------
    # Metodo para llenar el comboBox con los valores de la frecuencia
    def combo_unid_frec_ch1(self, unit):
        self.graph_key_CH1 = False
        # Función para asignar el valor de la frecuencia seleccionada
        # por el usuario
        def sel_frec_ch1(frc):
            if 10.0 >= float(frc) >= 1.0 and unit == "MHz":
                self.f_CH1 = float(frc) * 1e6
            elif 500.0 >= float(frc) >= 1.0 and unit == "kHz":
                self.f_CH1 = float(frc) * 1e3
            elif 500.0 >= float(frc) >= 1.0 and unit == "Hz":
                self.f_CH1 = float(frc)
            elif 500.0 >= float(frc) >= 1.0 and unit == "mHz":
                self.f_CH1 = float(frc) * 0.001
            elif 500.0 >= float(frc) >= 1.0 and unit == "uHz":
                self.f_CH1 = float(frc) * 0.000001
            else:
                self.f_CH1 = 1000
                QMessageBox.about(self, "¡Atención!", 'El valor'
                                              ' que has elegido no'
                                             ' puede ser usado para generar'
                                             ' una señal.\nPrueba con un v'
                                             'alor dentro del intervalo pe'
                                             'rmitido.\nSe ha asignado '
                                             'un valor por defecto: 1 kHz')
        if unit == 'MHz':
            self.combo3_CH1.clear()
            self.combo3_CH1.addItem('Elige un valor')
            self.combo3_CH1.addItem('10')
            self.combo3_CH1.addItem('5')
            self.combo3_CH1.addItem('2')
            self.combo3_CH1.addItem('1')
            self.combo3_CH1.setCurrentIndex(0)
            self.combo3_CH1.insertSeparator(4)
            self.combo3_CH1.activated[str].connect(sel_frec_ch1)
        elif unit == 'kHz':
            self.combo3_CH1.clear()
            self.combo3_CH1.addItem('500')
            self.combo3_CH1.addItem('200')
            self.combo3_CH1.addItem('100')
            self.combo3_CH1.addItem('50')
            self.combo3_CH1.addItem('20')
            self.combo3_CH1.addItem('10')
            self.combo3_CH1.addItem('5')
            self.combo3_CH1.addItem('2')
            self.combo3_CH1.addItem('1')
            self.combo3_CH1.setCurrentIndex(8)
            self.combo3_CH1.insertSeparator(9)
            self.combo3_CH1.activated[str].connect(sel_frec_ch1)
        elif unit == 'Hz':
            self.combo3_CH1.clear()
            self.combo3_CH1.addItem('Elige un valor')
            self.combo3_CH1.addItem('500')
            self.combo3_CH1.addItem('200')
            self.combo3_CH1.addItem('100')
            self.combo3_CH1.addItem('50')
            self.combo3_CH1.addItem('20')
            self.combo3_CH1.addItem('10')
            self.combo3_CH1.addItem('5')
            self.combo3_CH1.addItem('2')
            self.combo3_CH1.addItem('1')
            self.combo3_CH1.setCurrentIndex(0)
            self.combo3_CH1.insertSeparator(9)
            self.combo3_CH1.activated[str].connect(sel_frec_ch1)
        elif unit == 'mHz':
            self.combo3_CH1.clear()
            self.combo3_CH1.addItem('Elige un valor')
            self.combo3_CH1.addItem('500')
            self.combo3_CH1.addItem('200')
            self.combo3_CH1.addItem('100')
            self.combo3_CH1.addItem('50')
            self.combo3_CH1.addItem('20')
            self.combo3_CH1.addItem('10')
            self.combo3_CH1.addItem('5')
            self.combo3_CH1.addItem('2')
            self.combo3_CH1.addItem('1')
            self.combo3_CH1.setCurrentIndex(0)
            self.combo3_CH1.insertSeparator(9)
            self.combo3_CH1.activated[str].connect(sel_frec_ch1)
        elif unit == 'uHz':
            self.combo3_CH1.clear()
            self.combo3_CH1.addItem('Elige un valor')
            self.combo3_CH1.addItem('500')
            self.combo3_CH1.addItem('200')
            self.combo3_CH1.addItem('100')
            self.combo3_CH1.addItem('50')
            self.combo3_CH1.addItem('20')
            self.combo3_CH1.addItem('10')
            self.combo3_CH1.addItem('5')
            self.combo3_CH1.addItem('2')
            self.combo3_CH1.addItem('1')
            self.combo3_CH1.setCurrentIndex(0)
            self.combo3_CH1.insertSeparator(9)
            self.combo3_CH1.activated[str].connect(sel_frec_ch1)
    #-----------------------------------------------------------------------------
               
    #---------------------------------------------------------------------------------
    # Metodo para llenar el comboBox con los valores de la frecuencia
    def combo_unid_frec_ch2(self,unit):
        self.graph_key_CH2 = False
        # Función para asignar el valor de la frecuencia seleccionada
        # por el usuario
        def sel_frec_ch2(frc):
            if 10.0 >= float(frc) >= 1.0 and unit == 'MHz':
                self.f_CH2 = float(frc) * 1e6
            elif 500.0 >= float(frc) >= 1.0 and unit == 'kHz':
                self.f_CH2 = float(frc) * 1e3
            elif 500.0 >= float(frc) >= 1.0 and unit == 'Hz':
                self.f_CH2 = float(frc)
            elif 500.0 >= float(frc) >= 1.0 and unit == 'mHZ':
                self.f_CH2 = float(frc) * 0.001
            elif 500.0 >= float(frc) >= 1.0 and unit == 'uHZ':
                self.f_CH2 = float(frc) * 0.000001
            else:
                self.f_CH2 = 1000
                QMessageBox.about(self, "¡Atención!", 'El valor'
                                              ' que has elegido no'
                                             ' puede ser usado para generar'
                                             ' una señal.\nPrueba con un v'
                                             'alor dentro del intervalo pe'
                                             'rmitido.\nSe ha asignado '
                                             'un valor por defecto: 1 kHz')
        if unit == 'MHz':
            self.combo3_CH2.clear()
            self.combo3_CH2.addItem('Elige un valor')
            self.combo3_CH2.addItem('10')
            self.combo3_CH2.addItem('5')
            self.combo3_CH2.addItem('2')
            self.combo3_CH2.addItem('1')
            self.combo3_CH2.setCurrentIndex(0)
            self.combo3_CH2.insertSeparator(4)
            self.combo3_CH2.activated[str].connect(sel_frec_ch2)
        elif unit == 'kHz':
            self.combo3_CH2.clear()
            self.combo3_CH2.addItem('500')
            self.combo3_CH2.addItem('200')
            self.combo3_CH2.addItem('100')
            self.combo3_CH2.addItem('50')
            self.combo3_CH2.addItem('20')
            self.combo3_CH2.addItem('10')
            self.combo3_CH2.addItem('5')
            self.combo3_CH2.addItem('2')
            self.combo3_CH2.addItem('1')
            self.combo3_CH2.setCurrentIndex(8)
            self.combo3_CH2.insertSeparator(9)
            self.combo3_CH2.activated[str].connect(sel_frec_ch2)
        elif unit == 'Hz':
            self.combo3_CH2.clear()
            self.combo3_CH2.addItem('Elige un valor')
            self.combo3_CH2.addItem('500')
            self.combo3_CH2.addItem('200')
            self.combo3_CH2.addItem('100')
            self.combo3_CH2.addItem('50')
            self.combo3_CH2.addItem('20')
            self.combo3_CH2.addItem('10')
            self.combo3_CH2.addItem('5')
            self.combo3_CH2.addItem('2')
            self.combo3_CH2.addItem('1')
            self.combo3_CH2.setCurrentIndex(0)
            self.combo3_CH2.insertSeparator(9)
            self.combo3_CH2.activated[str].connect(sel_frec_ch2)
        elif unit == 'mHz':
            self.combo3_CH2.clear()
            self.combo3_CH2.addItem('Elige un valor')
            self.combo3_CH2.addItem('500')
            self.combo3_CH2.addItem('200')
            self.combo3_CH2.addItem('100')
            self.combo3_CH2.addItem('50')
            self.combo3_CH2.addItem('20')
            self.combo3_CH2.addItem('10')
            self.combo3_CH2.addItem('5')
            self.combo3_CH2.addItem('2')
            self.combo3_CH2.addItem('1')
            self.combo3_CH2.setCurrentIndex(0)
            self.combo3_CH2.insertSeparator(9)
            self.combo3_CH2.activated[str].connect(sel_frec_ch2)
        elif unit == 'uHz':
            self.combo3_CH2.clear()
            self.combo3_CH2.addItem('Elige un valor')
            self.combo3_CH2.addItem('500')
            self.combo3_CH2.addItem('200')
            self.combo3_CH2.addItem('100')
            self.combo3_CH2.addItem('50')
            self.combo3_CH2.addItem('20')
            self.combo3_CH2.addItem('10')
            self.combo3_CH2.addItem('5')
            self.combo3_CH2.addItem('2')
            self.combo3_CH2.addItem('1')
            self.combo3_CH2.setCurrentIndex(0)
            self.combo3_CH2.insertSeparator(9)
            self.combo3_CH2.activated[str].connect(sel_frec_ch2)
    #------------------------------------------------------------------------------------       
        
    #---------------------------------------------------------------------------
    # Método para añadir los valores de frecuencia al comboBox
    def combo_unid_fase_ch1(self):
        self.graph_key_CH1 = False
        self.combo4_CH1.addItem('360')
        self.combo4_CH1.addItem('345')
        self.combo4_CH1.addItem('330')
        self.combo4_CH1.addItem('315')
        self.combo4_CH1.addItem('300')
        self.combo4_CH1.addItem('285')
        self.combo4_CH1.addItem('270')
        self.combo4_CH1.addItem('255')
        self.combo4_CH1.addItem('240')
        self.combo4_CH1.addItem('225')
        self.combo4_CH1.addItem('210')
        self.combo4_CH1.addItem('195')
        self.combo4_CH1.addItem('180')
        self.combo4_CH1.addItem('165')
        self.combo4_CH1.addItem('150')
        self.combo4_CH1.addItem('135')
        self.combo4_CH1.addItem('120')
        self.combo4_CH1.addItem('105')
        self.combo4_CH1.addItem('90')
        self.combo4_CH1.addItem('75')
        self.combo4_CH1.addItem('60')
        self.combo4_CH1.addItem('45')
        self.combo4_CH1.addItem('30')
        self.combo4_CH1.addItem('15')
        self.combo4_CH1.addItem('0')
        self.combo4_CH1.setCurrentIndex(24)
        self.combo4_CH1.insertSeparator(25)
        # Función para asignar el valor del ángulo a la señal
        def sel_fase_ch1(fe):
            if 360 >= float(fe) >= 0:
                # Se convierten los grados a radianes
                self.fase_CH1 = float(fe) * (np.pi / 180)
            else:
                self.fase_CH1 = 0
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                             ' puede ser usado para generar'
                                             ' una señal.\nPrueba con un v'
                                             'alor dentro del intervalor p'
                                             'ermitido\nSe ha asignado '
                                             'un valor por defecto: 0°')
        self.combo4_CH1.activated[str].connect(sel_fase_ch1)
    #--------------------------------------------------------------------------------
        
    #------------------------------------------------------------------------------
    # Metodo para añadir los valores de frecuencia al comboBox
    def combo_unid_fase_ch2(self):
        self.graph_key_CH2 = False
        self.combo4_CH2.addItem('360')
        self.combo4_CH2.addItem('345')
        self.combo4_CH2.addItem('330')
        self.combo4_CH2.addItem('315')
        self.combo4_CH2.addItem('300')
        self.combo4_CH2.addItem('285')
        self.combo4_CH2.addItem('270')
        self.combo4_CH2.addItem('255')
        self.combo4_CH2.addItem('240')
        self.combo4_CH2.addItem('225')
        self.combo4_CH2.addItem('210')
        self.combo4_CH2.addItem('195')
        self.combo4_CH2.addItem('180')
        self.combo4_CH2.addItem('165')
        self.combo4_CH2.addItem('150')
        self.combo4_CH2.addItem('135')
        self.combo4_CH2.addItem('120')
        self.combo4_CH2.addItem('105')
        self.combo4_CH2.addItem('90')
        self.combo4_CH2.addItem('75')
        self.combo4_CH2.addItem('60')
        self.combo4_CH2.addItem('45')
        self.combo4_CH2.addItem('30')
        self.combo4_CH2.addItem('15')
        self.combo4_CH2.addItem('0')
        self.combo4_CH2.setCurrentIndex(24)
        self.combo4_CH2.insertSeparator(25)
        # Función para asignar el valor del ángulo a la señal
        def sel_fase_ch2(fe):
            if 360 >= float(fe) >= 0:
                # Se convierten los grados a radianes
                self.fase_CH2 = float(fe) * (np.pi / 180)
            else:
                self.fase_CH2 = 0
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                             ' puede ser usado para generar'
                                             ' una señal.\nPrueba con un v'
                                             'alor dentro del intervalor p'
                                             'ermitido\nSe ha asignado '
                                             'un valor por defecto: 0°')
        self.combo4_CH2.activated[str].connect(sel_fase_ch2)
    
    #---------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------------------
    # Metodo que añade los valores del offset al comboBox
    def combo_unid_off_ch1(self, unit):
        self.graph_key_CH1 = False
        # Función para asignar el valor del offset a la señal
        def sel_off_ch1(offt):
            if 5 >= float(offt) >= -5 and self.key1_CH1 is True:
                self.ofs_CH1 = float(offt)
            elif 900 >= float(offt) >= -900 and self.key1_CH1 is False:
                self.ofs_CH1 = float(offt) * 0.001
            else:
                self.ofs_CH1 = 0
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                  ' puede ser usado para generar'
                                  ' una señal.\nPrueba con un v'
                                  'alor dentro del intervalo p'
                                  'ermitido.\nsSe ha asignado '
                                  'un valor por defecto: 0 V')
        if unit == 'V':
            self.key1_CH1 = True
            self.combo5_CH1.clear()
            self.combo5_CH1.addItem('5')
            self.combo5_CH1.addItem('4')
            self.combo5_CH1.addItem('3')
            self.combo5_CH1.addItem('2')
            self.combo5_CH1.addItem('1')
            self.combo5_CH1.addItem('0')
            self.combo5_CH1.addItem('-1')
            self.combo5_CH1.addItem('-2')
            self.combo5_CH1.addItem('-3')
            self.combo5_CH1.addItem('-4')
            self.combo5_CH1.addItem('-5')
            self.combo5_CH1.setCurrentIndex(5)
            self.combo5_CH1.insertSeparator(11)
            self.combo5_CH1.activated[str].connect(sel_off_ch1)
        elif unit == 'mV':
            self.key1_CH1 = False
            self.combo5_CH1.clear()
            self.combo5_CH1.addItem('Elige un valor')
            self.combo5_CH1.addItem('900')
            self.combo5_CH1.addItem('800')
            self.combo5_CH1.addItem('700')
            self.combo5_CH1.addItem('600')
            self.combo5_CH1.addItem('500')
            self.combo5_CH1.addItem('400')
            self.combo5_CH1.addItem('300')
            self.combo5_CH1.addItem('200')
            self.combo5_CH1.addItem('100')
            self.combo5_CH1.addItem('90')
            self.combo5_CH1.addItem('80')
            self.combo5_CH1.addItem('70')
            self.combo5_CH1.addItem('60')
            self.combo5_CH1.addItem('50')
            self.combo5_CH1.addItem('40')
            self.combo5_CH1.addItem('30')
            self.combo5_CH1.addItem('20')
            self.combo5_CH1.addItem('10')
            self.combo5_CH1.addItem('9')
            self.combo5_CH1.addItem('8')
            self.combo5_CH1.addItem('7')
            self.combo5_CH1.addItem('6')
            self.combo5_CH1.addItem('5')
            self.combo5_CH1.addItem('0')
            self.combo5_CH1.addItem('-5')
            self.combo5_CH1.addItem('-6')
            self.combo5_CH1.addItem('-7')
            self.combo5_CH1.addItem('-8')
            self.combo5_CH1.addItem('-9')
            self.combo5_CH1.addItem('-10')
            self.combo5_CH1.addItem('-20')
            self.combo5_CH1.addItem('-30')
            self.combo5_CH1.addItem('-40')
            self.combo5_CH1.addItem('-50')
            self.combo5_CH1.addItem('-60')
            self.combo5_CH1.addItem('-70')
            self.combo5_CH1.addItem('-80')
            self.combo5_CH1.addItem('-90')
            self.combo5_CH1.addItem('-100')
            self.combo5_CH1.addItem('-200')
            self.combo5_CH1.addItem('-300')
            self.combo5_CH1.addItem('-400')
            self.combo5_CH1.addItem('-500')
            self.combo5_CH1.addItem('-600')
            self.combo5_CH1.addItem('-700')
            self.combo5_CH1.addItem('-800')
            self.combo5_CH1.addItem('-900')
            self.combo5_CH1.setCurrentIndex(0)
            self.combo5_CH1.insertSeparator(48)
            self.combo5_CH1.activated[str].connect(sel_off_ch1)
    #----------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------------
    # Metodo que añade los valores del offset al comboBox
    def combo_unid_off_ch2(self,unit):
        self.graph_key_CH2 = False
        # Función para asignar el valor del offset a la señal
        def sel_off_ch2(offt):
            if 5 >= float(offt) >= -5 and self.key1_CH2 is True:
                self.ofs_CH2 = float(offt)
            elif 900 >= float(offt) >= -900 and self.key1_CH2 is False:
                self.ofs_CH2 = float(offt) * 0.001
            else:
                self.ofs_CH2 = 0
                QMessageBox.about(self, "¡Atención!", 'El valor que has elegido no'
                                  ' puede ser usado para generar'
                                  ' una señal.\nPrueba con un v'
                                  'alor dentro del intervalo p'
                                  'ermitido.\nsSe ha asignado '
                                  'un valor por defecto: 0 V')
        if unit == 'V':
            self.key1_CH2 = True
            self.combo5_CH2.clear()
            self.combo5_CH2.addItem('5')
            self.combo5_CH2.addItem('4')
            self.combo5_CH2.addItem('3')
            self.combo5_CH2.addItem('2')
            self.combo5_CH2.addItem('1')
            self.combo5_CH2.addItem('0')
            self.combo5_CH2.addItem('-1')
            self.combo5_CH2.addItem('-2')
            self.combo5_CH2.addItem('-3')
            self.combo5_CH2.addItem('-4')
            self.combo5_CH2.addItem('-5')
            self.combo5_CH2.setCurrentIndex(5)
            self.combo5_CH2.insertSeparator(11)
            self.combo5_CH2.activated[str].connect(sel_off_ch2)
        elif unit == 'mV':
            self.key1_CH2 = False
            self.combo5_CH2.clear()
            self.combo5_CH2.addItem('Elige un valor')
            self.combo5_CH2.addItem('900')
            self.combo5_CH2.addItem('800')
            self.combo5_CH2.addItem('700')
            self.combo5_CH2.addItem('600')
            self.combo5_CH2.addItem('500')
            self.combo5_CH2.addItem('400')
            self.combo5_CH2.addItem('300')
            self.combo5_CH2.addItem('200')
            self.combo5_CH2.addItem('100')
            self.combo5_CH2.addItem('90')
            self.combo5_CH2.addItem('80')
            self.combo5_CH2.addItem('70')
            self.combo5_CH2.addItem('60')
            self.combo5_CH2.addItem('50')
            self.combo5_CH2.addItem('40')
            self.combo5_CH2.addItem('30')
            self.combo5_CH2.addItem('20')
            self.combo5_CH2.addItem('10')
            self.combo5_CH2.addItem('9')
            self.combo5_CH2.addItem('8')
            self.combo5_CH2.addItem('7')
            self.combo5_CH2.addItem('6')
            self.combo5_CH2.addItem('5')
            self.combo5_CH2.addItem('0')
            self.combo5_CH2.addItem('-5')
            self.combo5_CH2.addItem('-6')
            self.combo5_CH2.addItem('-7')
            self.combo5_CH2.addItem('-8')
            self.combo5_CH2.addItem('-9')
            self.combo5_CH2.addItem('-10')
            self.combo5_CH2.addItem('-20')
            self.combo5_CH2.addItem('-30')
            self.combo5_CH2.addItem('-40')
            self.combo5_CH2.addItem('-50')
            self.combo5_CH2.addItem('-60')
            self.combo5_CH2.addItem('-70')
            self.combo5_CH2.addItem('-80')
            self.combo5_CH2.addItem('-90')
            self.combo5_CH2.addItem('-100')
            self.combo5_CH2.addItem('-200')
            self.combo5_CH2.addItem('-300')
            self.combo5_CH2.addItem('-400')
            self.combo5_CH2.addItem('-500')
            self.combo5_CH2.addItem('-600')
            self.combo5_CH2.addItem('-700')
            self.combo5_CH2.addItem('-800')
            self.combo5_CH2.addItem('-900')
            self.combo5_CH2.setCurrentIndex(0)
            self.combo5_CH2.insertSeparator(48)
            self.combo5_CH2.activated[str].connect(sel_off_ch2)
    #-----------------------------------------------------------------------------
        
    #------------------------------------------------------------------------------
    # Metodo para mostrar un mensaje de inicio de la señal al usuario
    def aviso_signal_gen_ch1(self):
        # Se desactiva el botón de GENERAR SEÑAL
        self.btn_inicio_CH1.setEnabled(False)
        # Texto que se muestra
        self.aviso_gen_CH1.setText('Tu señal está siendo generada')
    #-------------------------------------------------------------------------------
    
    #------------------------------------------------------------------------------
    # Función para generar la señal creada por el usuario
    def dibuja_ch1(self):
        # Se determina si se va a crear una nueva gráfica o solo se puso pausa
        if self.graph_key_CH1 is True:
            self.ani_CH1.event_source.start()  # vuelve a correr la animación
        else:
            # Parámetros de la señal simulada
            self.T_CH1 = 1 / self.f_CH1
            # Se da una frecuencia de muestro de 2000 veces la frecuencia con
            # que se crea la señal. Este valor presenta los puntos que se van
            # a tener para crear la gráfica
            self.fs_CH1 = 250. * self.f_CH1
            self.Ts_CH1 = 1. / self.fs_CH1      # Debe ponerse 1. con punto
            #Numero de muestras tomadas
            self.N_CH1=(4*self.T_CH1)/self.Ts_CH1
            self.cicloT_CH1 = 0.5

            # Se crea el arreglo de tiempo, mostrando tres períodos y con la
            self.x_CH1 = np.arange(0, 4 * self.T_CH1, self.Ts_CH1)
            # Si la señal a generar no involucra frecuencia, se le da un valor de
            # 1 a la frecuencia inicial. Esto es para mostrar a la señal, con
            # Frecuencia o sin ella.
            if self.signal_generador_CH1 == 'DC' or \
                self.signal_generador_CH1 == 'Exponencial':
                self.f_CH1 = 1e3
                self.fs_CH1 = 250. * self.f_CH1
                self.Ts_CH1 = 1. / self.fs_CH1      # Debe ponerse 1. con punto
                #Numero de muestras tomadas
                self.N_CH1=(4*self.T_CH1)/self.Ts_CH1
                self.x_CH1 = np.arange(0, 4 * self.T_CH1, self.Ts_CH1)
            else:
                self.omega_CH1 = 2 * np.pi * self.f_CH1
        
            # Se determina qué tipo de señal se va a generar
            if self.signal_generador_CH1 == 'Seno':
                self.ejes_CH1.clear() # Se preparan los ejes para una nueva gráfica
                self.tmp_CH1 = 0  # Variable para identificar a la señal a generar
                # Se crea la señal y se le asignan todas sus características
                self.onda_CH1 = (self.ofs_CH1 + (self.A_CH1 * np.sin((self.omega_CH1 *
                                                                      self.x_CH1) +
                                                                     self.fase_CH1)))
            elif self.signal_generador_CH1 == 'Coseno':
                self.ejes_CH1.clear()     
                self.tmp_CH1 = 1
                self.onda_CH1 = (self.ofs_CH1 + (self.A_CH1 * np.cos((self.omega_CH1 * 
                                                                      self.x_CH1) +
                                                                     self.fase_CH1)))
            elif self.signal_generador_CH1 == 'Impulso':
                self.ejes_CH1.clear()    
                self.tmp_CH1 = 2
                self.onda_CH1 = (self.A_CH1 * signal.unit_impulse(len(self.x_CH1), 'mid'))
            elif self.signal_generador_CH1 == 'Cuadrada':
                self.ejes_CH1.clear()    
                self.tmp_CH1 = 3
                self.onda_CH1 = (self.ofs_CH1 + (self.A_CH1 * signal.square(self.omega_CH1 *
                                                                            self.x_CH1,
                                                                            self.cicloT_CH1)))
            elif self.signal_generador_CH1 == 'Diente de sierra':
                self.ejes_CH1.clear()     
                self.tmp_CH1 = 4
                self.onda_CH1 = (self.ofs_CH1 + (self.A_CH1 *
                                 signal.sawtooth(self.omega_CH1 * self.x_CH1, 1)))
            elif self.signal_generador_CH1 == 'Escalón unitario':
                self.ejes_CH1.clear()    
                self.tmp_CH1 = 5
                xTr_CH1 = np.arange(-0.5, self.T_CH1, self.Ts_CH1)
                u_CH1 = lambda xTr_CH1: np.piecewise(xTr_CH1, xTr_CH1 >= 0, [1, 0])
                self.x_CH1 = xTr_CH1
                self.onda_CH1 = self.A_CH1 * u_CH1(self.x_CH1)
            elif self.signal_generador_CH1 == 'DC':
                self.ejes_CH1.clear()     
                self.tmp_CH1 = 6
                self.onda_CH1 = np.ones(len(self.x_CH1)) * self.A_CH1
            elif self.signal_generador_CH1 == 'Exponencial':
                self.ejes_CH1.clear()
                self.tmp_CH1 = 7
                self.onda_CH1 = self.A_CH1 * np.exp(-self.x_CH1)
            elif self.signal_generador_CH1 == 'Triangular':
                self.ejes_CH1.clear()    
                self.tmp_CH1 = 8
                self.onda_CH1 = (self.ofs_CH1 + (self.A_CH1 * signal.sawtooth(self.omega_CH1 *
                                                 self.x_CH1, 0.5)))
            elif self.signal_generador_CH1 == 'Bits aleatorios':
                self.tmp_CH1 = 1
                pass
            # Se gráfica la señal y se crea una lista con los valores de la señal
            # generada. Esta línea es para crear la imagen de la gráfica y 
            # guardar los valores en dos variable que después van a servir para
            # hacer la animación
            self.line_CH1, = self.ejes_CH1.plot(self.x_CH1, self.onda_CH1, color="#FC08EE")
            # Se le agrega título a la gráfica
            self.ejes_CH1.set_title('Muestra de la gráfica generada')
            # Se le dan características a la gráfica
            self.ejes_CH1.set_xlabel('Tiempo [ s ]')        # Se establece el eje x
            self.ejes_CH1.set_ylabel('Voltaje [ V ]')       # Se establece el eje y
            # Se da el formato científico a los ejes X y Y para poder apreciar
            # mejor los valores de la gráfica generada
            self.ejes_CH1.ticklabel_format(axis='both', style='sci',
                                           scilimits=(-3, 3))
            # Se establece el color de fondo de la gráfica
            self.ejes_CH1.set_facecolor('xkcd:white')
            self.ejes_CH1.grid(True)  # Se muestra una cuadrícula para la gráfica
            # Función para animar la gráfica
            def animate_ch1(i):
                # La variable de clase de actualiza con los valores de la 
                # señal que se está generando
                var1_CH1 = self.onda_CH1
                
                var2_CH1 = self.onda_CH1
                self.signal_osc_CH1 = var1_CH1
                self.signal_spc_CH1 = var2_CH1
                # Dependiendo de la variable para identificar a la gráfica, se escogerá
                # Una opción de las señales disponibles

                self.ejes_CH1.autoscale(True)    # Se da escala automática a la gráfica
                self.line_CH1.set_data(self.x_CH1[:i], self.onda_CH1[:i])
            
                # Regresa la tupla de la gráfica con los valores actualizados
                return self.line_CH1,
            # Función para iniciar la animación de la gráfica
            def init_graph_ch1():
                # Se establecen dos listas vacías que después van a ser cambiadas
                # por los valores de los arreglos para x e y. 
                self.line_CH1.set_data([], [])
                # Se regresa la tupla de la gráfica con los valores actualizados
                return self.line_CH1,
            # Se declara una atributo de tipo animación para que se pueda la
            # Gráfica que se generó. Los argumentos son: self.fig: figura que se
            # Va a animar; self.animate: variable para determinar la gráfica que
            # Se va animar; init_func: método para inicar la animación; frames
            # se usa para determinar el valor de frame o cuadros que va a mostras
            # la animación, y este valor coincide con el número de muestras que
            # se tienen en el eje x, lo cual hace que sólo se muestran esa
            # cantidad de valores; interval: Duración de la animación (en ms);
            # blit: mejora la calidad de Animación; y repeat: se repite o no la animación.
            self.ani_CH1 = animation.FuncAnimation(self.fig_CH1, animate_ch1,
                                                   init_func=init_graph_ch1,
                                                   frames=len(self.x_CH1),
                                                   interval=5, blit=True,
                                                   repeat=True)
            self.ejes_CH1.autoscale(True)    # Se da escala automática a la gráfica
            self.canvas_CH1.draw()           # Se dibuja la gráfica
        #----------------------------------------------------------------------
        
    #--------------------------------------------------------------------------
    # Metodo para mostrar un mensaje de inicio de la señal al usuario
    def aviso_signal_gen_ch2(self):
        # Se desactiva el botón de GENERAR SEÑAL
        self.btn_inicio_CH2.setEnabled(False)
        # Texto que se muestra
        self.aviso_gen_CH2.setText('Tu señal está siendo generada')
    #------------------------------------------------------------------------------------------
               
    #-----------------------------------------------------------------------------------------
    # Metodo para generar la señal creada por el usuario
    def dibuja_ch2(self):
        # Se determina si se va a crear una nueva gráfica o solo se puso pausa
       
        if self.graph_key_CH2 is True:
            self.ani_CH2.event_source.start()  # vuelve a correr la animación
        else:
            # Parámetros de la señal simulada
            self.T_CH2 = 1 / self.f_CH2
            # Se da una frecuencia de muestro de 2000 veces la frecuencia con
            # que se crea la señal. Este valor presenta los puntos que se van
            # a tener para crear la gráfica
            self.fs_CH2 = 250. * self.f_CH2
            self.Ts_CH2 = 1. / self.fs_CH2      # Debe ponerse 1. con punto
            #Numero de muestras tomadas
            self.N_CH2=(4*self.T_CH2)/self.Ts_CH2
            self.cicloT_CH2 = 0.5
            # Se crea el arreglo de tiempo, mostrando cuatro períodos
            self.x_CH2 = np.arange(0, 4 *self.T_CH2, self.Ts_CH2)
            # Si la señal a generar no involucra frecuencia, se le da un valor de
            # 0.1 a la frecuencia inicial. Esto es para mostrar a la señal, con
            # Frecuencia o sin ella.
            if self.signal_generador_CH2 == 'DC' or \
                self.signal_generador_CH2 == 'Exponencial':
                self.f_CH2 = 1e3
                self.fs_CH2 = 250. * self.f_CH2
                self.Ts_CH2 = 1. / self.fs_CH2      # Debe ponerse 1. con punto
                # Numero de muestras tomadas
                self.N_CH2=(4*self.T_CH2)/self.Ts_CH2
                self.x_CH2 = np.arange(0, 4 * self.T_CH2, self.Ts_CH2)
            else:
                self.omega_CH2 = 2 * np.pi * self.f_CH2
                # Se determina qué tipo de señal se va a generar
        
            if self.signal_generador_CH2 == 'Seno':
                self.ejes_CH2.clear() # Se preparan los ejes para una nueva gráfica
                self.tmp_CH2 = 0  # Variable para identificar a la señal a generar
                # Se crea la señal y se le asignan todas sus características
                self.onda_CH2 = (self.ofs_CH2 + (self.A_CH2 *
                                     np.sin((self.omega_CH2 * self.x_CH2) +
                                            self.fase_CH2)))
            elif self.signal_generador_CH2 == 'Coseno':
                self.ejes_CH2.clear()     
                self.tmp_CH2 = 1
                self.onda_CH2 = (self.ofs_CH2 + (self.A_CH2 *
                                 np.cos((self.omega_CH2 * self.x_CH2) +
                                        self.fase_CH2)))
            elif self.signal_generador_CH2 == 'Impulso':
                self.ejes_CH2.clear()    
                self.tmp_CH2 = 2
                self.onda_CH2 = (self.A_CH2 * signal.unit_impulse(len(self.x_CH2), 'mid'))
            elif self.signal_generador_CH2 == 'Cuadrada':
                self.ejes_CH2.clear()    
                self.tmp_CH2 = 3
                self.onda_CH2 = (self.ofs_CH2 + (self.A_CH2 *
                                 signal.square(self.omega_CH2* self.x_CH2,
                                               self.cicloT_CH2)))
            elif self.signal_generador_CH2 == 'Diente de sierra':
                self.ejes_CH2.clear()     
                self.tmp_CH2 = 4
                self.onda_CH2 = (self.ofs_CH2 + (self.A_CH2 *
                                 signal.sawtooth(self.omega_CH2 *
                                                 self.x_CH2, 1)))
            elif self.signal_generador_CH2 == 'Escalón unitario':
                self.ejes_CH2.clear()    
                self.tmp_CH2 = 5
                xTr_CH2 = np.arange(-0.5, self.T_CH2, self.Ts_CH2)
                u_CH2 = lambda xTr_CH2: np.piecewise(xTr_CH2, xTr_CH2 >= 0, [1, 0])
                self.x_CH2 = xTr_CH2
                self.onda_CH2 = self.A_CH2 * u_CH2(self.x_CH2)
            elif self.signal_generador_CH2 == 'DC':
                self.ejes_CH2.clear()     
                self.tmp_CH2 = 6
                self.onda_CH2 = np.ones(len(self.x_CH2)) * self.A_CH2
            elif self.signal_generador_CH2 == 'Exponencial':
                self.ejes_CH2.clear()
                self.tmp_CH2 = 7
                self.onda_CH2 = self.A_CH2 * np.exp(-self.x_CH2)
            elif self.signal_generador_CH2 == 'Triangular':
                self.ejes_CH2.clear()    
                self.tmp_CH2 = 8
                self.onda_CH2 = (self.ofs_CH2 + (self.A_CH2 *
                                         signal.sawtooth(self.omega_CH2 *
                                                 self.x_CH2, 0.5)))
            elif self.signal_generador_CH2 == 'Bits aleatorios':
                self.tmp_CH2 = 9
                pass
            # Se gráfica la señal y se crea una lista con los valores de la señal
            # generada
            self.line_CH2, = self.ejes_CH2.plot(self.x_CH2, self.onda_CH2, color="#FC08EE")
            # Se le agrega título a la gráfica
            # self.ejes_CH2.set_title('Muestra de la gráfica generada')
            # Se le dan características a la gráfica
            self.ejes_CH2.set_xlabel('Tiempo [ s ]')        # Se establece el eje x
            self.ejes_CH2.set_ylabel('Voltaje [ V ]')       # Se establece el eje y
            # Se da el formato científico a los ejes X y Y para poder apreciar
            # mejor los valores de la gráfica generada
            self.ejes_CH2.ticklabel_format(axis='both', style='sci',
                                           scilimits=(-3, 3))
            # Se establece el color de fondo de la gráfica
            self.ejes_CH2.set_facecolor('xkcd:white')
            self.ejes_CH2.grid(True)  # Se muestra una cuadrícula para la gráfica
            # Función para animar la gráfica
            def animate_ch2(i):
                # La variable de clase de actualiza con los valores de la 
                # señal que se está generando
                var1_CH2 = self.onda_CH2
                
                var2_CH2 = self.onda_CH2
                self.signal_osc_CH2 = var1_CH2
                self.signal_spc_CH2 = var2_CH2
                # Dependiendo de la variable para identificar a la gráfica, se escogerá
                # Una opción de las señales disponibles
                
                self.ejes_CH2.autoscale(True)    # Se da escala automática a la gráfica
                self.line_CH2.set_data(self.x_CH2[:i], self.onda_CH2[:i])
            
                # Regresa la tupla de la gráfica con los valores actualizados
                return self.line_CH2,
            # Función para iniciar la animación de la gráfica
            def init_graph_ch2():
                # Se establecen los valores que va a tomar la variable y de la gráfica
                # Cuando se esté haciendo la animación. El argumento comprueba que los
                # Valores sean números, con np.nan
                self.line_CH2.set_data([], [])
                # Se regresa la tupla de la gráfica con los valores actualizados
                return self.line_CH2,
            # Se declara una atributo de tipo animación para que se pueda la
            # Gráfica que se generó. Los argumentos son: self.fig: figura que se
            # Va a animar; self.animate: variable para determinar la gráfica que
            # Se va animar; init_func: método para inicar la animación; interval:
            # Duración de la animación (en ms); blit: mejora la calidad de
            # Animación; save_count: número de muestras que se van a tomar
            # Para realizar la animación; y repeat: se repite o no la animación.
            self.ani_CH2 = animation.FuncAnimation(self.fig_CH2, animate_ch2,
                                               init_func=init_graph_ch2,
                                               interval=5, blit=True,
                                               frames=len(self.x_CH2),
                                               repeat=True)
            self.ejes_CH2.autoscale(True)    # Se da escala automática a la gráfica
            self.canvas_CH2.draw()           # Se dibuja la gráfica
    #---------------------------------------------------------------------------------------
        
    #----------------------------------------------------------------------------------
    # Metodo para guardar las muestras de la señal generada en un archivo
    # de texto
    def muestras_ch1(self):
        cto_CH1 = 0         # Variable que cuenta las muestras
        lista_CH1 = []      # Lista para guardar las muestras
        # Se abre un archivo de texto en modo escritura 'w'
        f_CH1 = open('Aplicación_UAMI_Muestras_CH1.txt', 'w')
        # Se escribe en le archivo
        f_CH1.write('Valores de la señal generada: \n\n')
        # Se escriben en el archivo de texto las muestras de la señal
        for i in range(len(self.onda_CH1)):
            # Se convierten a cadenas de texto las muestras (números)
            num_CH1 = str(self.onda_CH1[i])
            # Se agregan las muestras una a una a la lista
            lista_CH1.append(num_CH1)
            # Aumenta la cuenta de las muestras
            cto_CH1 += 1
        f_CH1.write(str(lista_CH1))  # Se guarda la lista en el archivo de texto
        # Se escribe el conteo final de las muestras
        f_CH1.write('\nEl total de valores es: ' + str(cto_CH1))
        f_CH1.close()       # Se cierra el archivo de texto
    #-------------------------------------------------------------------------------------
                
    #---------------------------------------------------------------------------------------
    # Metodo para guardar las muestras de la señal generada en un archivo
    # de texto
    def muestras_ch2(self):
        cto_CH2 = 0         # Variable que cuenta las muestras
        lista_CH2 = []      # Lista para guardar las muestras
        # Se abre un archivo de texto en modo escritura 'w'
        f_CH2 = open('Aplicación_UAMI_Muestras_CH2.txt', 'w')
        # Se escribe en le archivo
        f_CH2.write('Valores de la señal generada: \n\n')
        # Se escriben en el archivo de texto las muestras de la señal
        for i in range(len(self.onda_CH2)):
            # Se convierten a cadenas de texto las muestras (números)
            num_CH2 = str(self.onda_CH2[i])
            # Se agregan las muestras una a una a la lista
            lista_CH2.append(num_CH2)
            # Aumenta la cuenta de las muestras
            cto_CH2 += 1
        f_CH2.write(str(lista_CH2))  # Se guarda la lista en el archivo de texto
        # Se escribe el conteo final de las muestras
        f_CH2.write('\nEl total de valores es: ' + str(cto_CH2))
        f_CH2.close()       # Se cierra el archivo de texto
    #-------------------------------------------------------------------------------------------
    
    #------------------------------------------------------------------------------------------------
    # Metodo para avisar al usuario que se ha detenido la generación de la
    # señal
    def aviso_signal_gen_stop_ch1(self):
        # Se habilita el botón de GENERAR SEÑAL
        self.btn_inicio_CH1.setEnabled(True)
        self.aviso_gen_CH1.setText('Tu señal se ha detenido.')
        # Se detiene la animación que muestra a la señales del generador
        self.ani_CH1.event_source.stop()
        self.graph_key_CH1 = True  # Variable para detener o comenzar la animación
    #------------------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------------------
    # Método para avisar al usuario que se ha detenido la generación de la
    # señal
    def aviso_signal_gen_stop_ch2(self):
        # Se habilita el botón de GENERAR SEÑAL
        self.btn_inicio_CH2.setEnabled(True)
        self.aviso_gen_CH2.setText('Tu señal se ha detenido.')
        # Se detiene la animación que muestra a la señales del generador
        self.ani_CH2.event_source.stop()
        self.graph_key_CH2 = True  # Variable para detener o comenzar la animación
    
    #---------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------------
    # Señal para guardar la señal en un archivo de imagen
    def save_graph(self):
        # Se crea un objeto QMessageBox para preguntar al usuario cuál es
        # la imagen que quiere guardar, si del canal 1 o del canal 2
        mj = QMessageBox()
        mj.setIcon(QMessageBox.Question)
        mj.setText('¿De cuál canal quieres guardar una imagen?')
        mj.setInformativeText('El archivo con formato .png será guardado'
                              ' en la carpeta donde está ejcutandose la'
                              ' aplicación')
        mj.addButton(QPushButton('Canal 1'), QMessageBox.YesRole)
        mj.addButton(QPushButton('Cancelar'), QMessageBox.NoRole)
        mj.addButton(QPushButton('Canal 2'), QMessageBox.DestructiveRole)
        
        rv = mj.exec()
        if rv == 0:
            try:
                self.fig_CH1.savefig('Wav-I_Señal_CH1 ('+str(self.ni_1)+').png')
                QMessageBox.about(self, '¡Éxito!', 'La imagen ha sido guardada')
                self.ni_1 += 1
            except:
                QMessageBox.about(self, 'Atención', 'No se ha podido guardar la imagen'
                                  ' vuelve a intentarlo') 
            finally:
                pass
        elif rv == 2:
            try:
                self.fig_CH2.savefig('Wav-I_Señal_CH2 ('+str(self.ni_2)+').png')
                QMessageBox.about(self, '¡Éxito!', 'La imagen ha sido guardada') 
                self.ni_2 += 1
            except:
                QMessageBox.about(self, 'Atención', 'No se ha podido guardar la imagen'
                                  ' vuelve a intentarlo') 
            finally:
                pass
    #-----------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    def out_graph_ch2(self):
        pass
    #---------------------------------------------------------------------------------
        
    #----------------------------------------------------------------------------------------
    # Método para crear el objeto widget de la gráfica principal
    def frame_graph_ch1(self):
        # Se instancia un atributo de tipo QWidget
        frame_principal_CH1 = QWidget()
        self.fig_CH1 = Figure()  # Se instancia un atributo de tipo Figure
        # Se instancia un atributo de tipo Canvas que contiene al tributo fig
        self.canvas_CH1 = FigureCanvas(self.fig_CH1)
        # Se establece como padre del atributo canvas al atributo frame
        self.canvas_CH1.setParent(frame_principal_CH1)
        # Un atributo se iguala al atributo fig para añadir una grafica [(111)
        # Son los parametros de la cuadrícula que va a contener a la grafica.
        # Es un entero que significa: cuadrícula de 1x1, 1er gráfica] Aspect
        # Hace referencia a la forma que va a tomar la gráfica por defecto o
        # Automaticamente, dependiendo de lo que se esté graficando
        self.ejes_CH1 = self.fig_CH1.add_subplot(1, 1, 1, aspect='auto')
        vbox_CH1 = QVBoxLayout()
        # Se crea un widget de tipo vbox para contener a la figura de Canvas
        vbox_CH1.addWidget(self.canvas_CH1)
        # El atributo frame muestra a la caja vbox
        frame_principal_CH1.setLayout(vbox_CH1)
        
        return frame_principal_CH1
    #---------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------
    # Metodo para crear el objeto widget de la gráfica principal
    def frame_graph_ch2(self):
        # Se instancia un atributo de tipo QWidget
        frame_principal_CH2 = QWidget()
        self.fig_CH2 = Figure()  # Se instancia un atributo de tipo Figure
        # Se instancia un atributo de tipo Canvas que contiene al tributo fig
        self.canvas_CH2 = FigureCanvas(self.fig_CH2)
        # Se establece como padre del atributo canvas al atributo frame
        self.canvas_CH2.setParent(frame_principal_CH2)
        # Un atributo se iguala al atributo fig para añadir una grafica [(111)
        # Son los parametros de la cuadrícula que va a contener a la grafica.
        # Es un entero que significa: cuadrícula de 1x1, 1er gráfica] Aspect
        # Hace referencia a la forma que va a tomar la gráfica por defecto o
        # Automaticamente, dependiendo de lo que se esté graficando
        self.ejes_CH2 = self.fig_CH2.add_subplot(1, 1, 1, aspect='auto')
        vbox_CH2 = QVBoxLayout()
        # Se crea un widget de tipo vbox para contener a la figura de Canvas
        vbox_CH2.addWidget(self.canvas_CH2)
        # El atributo frame muestra a la caja vbox
        frame_principal_CH2.setLayout(vbox_CH2)
        
        return frame_principal_CH2       
    #-------------------------------------------------------------------------------------------

# =============================================================================
# !!!OSCILOSCOPIO
# =============================================================================
    def tab_osc(self):
        
        tab_osc_ = QWidget()
        # Parámetros iniciales
        self.Sd = 1   # Valor inicial de Segundos por division
        self.Vd1 = 1  # valor inicial de V por division
        self.Vd2 = 1
        self.centro = 0
        # Límites para la vista que tiene el usuario al visualizar una gráfica
        self.xmax = 1
        self.xmin = -1

        # Variables para determinar el tiempo
        self.var_t = 0
        self.aux_t = 0

        # Objeto de clase Qwidget, widget es el widget que es la ventana 1
        widget = QWidget()
        widget.setObjectName("widget")  # De le da nombre
        # grid_layout es el grid princicpak que contiene todo en la ventana
        gridLayout = QGridLayout(widget)
        # ----------------------- WIDGET DE GRAFICA --------------------------
        self.graficaWidget1 = pg.PlotWidget()  # Gráfica de pyqtgraph
        # Objeto plotItem de graficaWidget1
        self.p1 = self.graficaWidget1.plotItem
        # Se esconde el botón por defecto de autorange para que no se mueva
        # La gráfica cada vez que se actualizan las muestras
        self.p1.hideButtons()  
        # Se bajan las muestras (resolución), pero mejora el rendimiento
        self.p1.setDownsampling(auto=True, mode='peak')
        # Sólo de dibujan los puntos dentro del rango de vista visible
        self.p1.setClipToView(True)
        # Se crea la curva para graficar los datos del canal 1
        self.curva = self.graficaWidget1.plot()
        # Se crea una nueva gráfica de pyqt para el canal 2
        self.graficaWidget2 = pg.PlotWidget()
        # Se crea una caja que tome la vista de la gráfica del canal 2
        self.graficaBox2 = self.graficaWidget2.getViewBox()
        # Se crea la curva para graficar los datos del canal 2
        self.curva2 = self.graficaWidget2.plot()
        # Se anañde a la caja del canal 2 la gráfica para este canal
        self.graficaBox2.addItem(self.curva2)
        # ----------------- Se configuran los canales y sus vistas ------------
        self.p1.showAxis('right')  # Se muestra en eje derecho vertical
        # Se añade al objeto p1 de clase plotItem el objeto graficaBox2
        self.p1.scene().addItem(self.graficaBox2)
        # Enlace este eje a un ViewBox, haciendo que su rango visualizado
        # coincida con el rango visible de la vista.
        self.p1.getAxis('right').linkToView(self.graficaBox2)
        # Enlace el eje X de esta vista a otra vista. (ver LinkView)
        self.graficaBox2.setXLink(self.p1)
        
        #####
        self.p1.vb.sigResized.connect(self.update_views)
        # Se establece la grafica en el gridLayout
        gridLayout.addWidget(self.graficaWidget1, 0, 3, 2, 1)
        # Muestra cuadricula de grafica(x,y,opacidad)
        self.graficaWidget1.showGrid(x=True, y=True, alpha=1.0)
        # Título y unidades de label, eje Y del canal 1
        self.graficaWidget1.setLabel('left', 'Amplitud', units='V',
                                    color='#ffff00')
        # Título y unidades de label, eje Y del canal 2
        self.graficaWidget1.setLabel('right', 'Amplitud', units='V',
                                    color='#33FFF3')
        # Título y unidades de label, eje x, ambos canales
        self.graficaWidget1.setLabel('bottom', 'Tiempo', units='s')
        # GraficaBox11 contiene a viewBox asociado a PLotWidget(graficaWidget1)
        self.graficaBox1 = self.graficaWidget1.getViewBox()
        # Evitan que se muevan los ejes 'y' para cada canal
        self.graficaBox1.setMouseEnabled(y=False)
        self.graficaBox2.setMouseEnabled(y=False)
        # Establece máximo y mínimo rango mostrado en la grafica, por defecto
        self.graficaBox1.setYRange(-1, 1)
        # Establezca el rango X visible de la vista en [ min , max ].
        self.graficaWidget1.setXRange(-0.05, 0.05)  # Valores por defecto
     
        # Se crea un objeto de tipo Timer para ambos canales
        # Esto debe ir desde la creacion del widget si no
        # No se detecta como atributo del objeto osciloscopio
        self.timer1 = pg.QtCore.QTimer()
        # Se trata de pasar el menor tiempo posible en el intervalo
        self.timer1.setInterval(0)
        # --------------------------------------------------------------------

        # ------------- Configuracion MCP3008 y SPI ----------------------
        # Start SPI connection
        # self.spi = spidev.SpiDev()  # Created an object
        # Se utiliza el bus del chip (10 bits) y se selecciona el dispositivo a
        # Utilizar
        # self.spi.open(0, 0)
        # Initializing LED pin as OUTPUT pin
        # led_pin = 20
        # GPIO.setmode(GPIO.BCM)
        # -----------------------------------------------------------------

        # ---------------------- CAJA SUPERIOR -------------------------------
        # groupBox_1 contiene los botones de la parte superior
        groupBox_1 = QGroupBox(widget)
        groupBox_1.setTitle("")
        # gridLayout1 que contiene a groupBox_1
        gridLayout1 = QGridLayout(groupBox_1)
        # Objeto boton RUN
        self.pushButton1 = QPushButton("RUN", groupBox_1)
        self.pushButton1.setStyleSheet('background-color: #00F212;'
                                      'border: 1px solid black')
        self.pushButton1.setFont(QtGui.QFont('Times New Roman', 15,
                                             weight=QtGui.QFont.Bold))
        #####
        # Botón RUN conectado con la función que mostrará la señal al usuario
        self.pushButton1.clicked.connect(self.correr_osc)
        # (fila,columna, hilera, tramo de columna)
        gridLayout1.addWidget(self.pushButton1, 3, 0, 1, 1)
        
        # Objeto boton STOP
        self.pushButton2_osc = QPushButton("STOP", groupBox_1)
        self.pushButton2_osc.setStyleSheet('color: #FFFFFF; '
                                       'background-color: #FF0000;'
                                       'border: 1px solid black')
        self.pushButton2_osc.setFont(QtGui.QFont('Times New Roman', 15,
                                             weight=QtGui.QFont.Bold))
        
        #####
        # Se conecta con el método que pone en pausa la gráfica
        self.pushButton2_osc.clicked.connect(self.pausa)
        gridLayout1.addWidget(self.pushButton2_osc, 3, 1, 1, 1)
        
        # Objeto boton MEASURE
        pushButton3 = QPushButton("MEDICIONES", groupBox_1)
        pushButton3.setFont(QtGui.QFont('Times New roman', 14))
        gridLayout1.addWidget(pushButton3, 4, 0, 2, 1)
        
        #####
        # Se conecta con la función que hace las mediciones de la señal
        # simulada
        pushButton3.clicked.connect(self.mediciones)
        
        # Se crea un botón para guardar la señal en un archivo de imagen
        btn_save_osc = QPushButton('Guardar')
        btn_save_osc.setFont(QtGui.QFont('Times New Roman', 14,
                                         weight=QtGui.QFont.Bold))
        btn_save_osc.setStyleSheet('color: #FFFFFF;'
                                   'background-color: #4B9AFC;'
                                     'border: 1px solid black')
        gridLayout1.addWidget(btn_save_osc, 5, 0)
        btn_save_osc.clicked.connect(self.save_graph_osc)
        
        # Objeto checkBox AUTOSET
        self.checkBox1 = QPushButton("AUTOSET", groupBox_1)
        self.checkBox1.setStyleSheet('color: #FFFFFF;'
                                       'background-color: #B775F8;'
                                       'border: 1px solid black')
        self.checkBox1.setFont(QtGui.QFont('Times New roman', 14,
                                            weight=QtGui.QFont.Bold))
       
        #####
        # Se conecta el boton de AUTOSET con su función correspondiente
        self.checkBox1.clicked.connect(self.autoset)
        # self.gridLayout1.addWidget(self.checkBox1, 4, 2, 2, 1)
        gridLayout1.addWidget(self.checkBox1, 4, 2, 2, 1)
        # Inicialmente se encuentra deshabilitado el autorango utilizado en
        # Funcion autoset
        self.auto1 = False
        # Se añade a gridLayout principal todo lo contenido en groupBox_1
        gridLayout.addWidget(groupBox_1, 0, 0, 1, 3)
        
        # --------------- CAJA INFERIOR IZQUIERDA ----------------------------
        groupBox_2 = QGroupBox(widget)
        groupBox_2.setTitle("VERTICAL")
        # Objeto qgridLayout_2
        gridLayout_2 = QGridLayout(groupBox_2)
        
        # Botón canal1
        self.checkBoxch1 = QCheckBox("CH1", groupBox_2)
        self.checkBoxch1.setStyleSheet("background-color: #FFF641")
        self.checkBoxch1.setFont(QtGui.QFont('Times New roman', 12, 
                                             weight=QtGui.QFont.Bold))
        
        #####
        # Conecta el boton CH1 con la función que manda un aviso al usuario
        self.checkBoxch1.clicked.connect(self.aviso_canal1)
        gridLayout_2.addWidget(self.checkBoxch1, 0, 0, 1, 1)
        
        self.checkBoxch2 = QCheckBox("CH2", groupBox_2)
        self.checkBoxch2.setStyleSheet("background-color: #2595FF")
        self.checkBoxch2.setFont(QtGui.QFont('Times New roman', 12,
                                             weight=QtGui.QFont.Bold))
        
        ######
        # Conecta el boton CH2 con la función que manda un aviso al usuario
        self.checkBoxch2.clicked.connect(self.aviso_canal2)
        gridLayout_2.addWidget(self.checkBoxch2, 0, 1, 1, 1)
        
        self.spin1 = QSpinBox(groupBox_2)  # Spin posicion de canal1
        # Establece el rango que contendra el dial -1 a 1
        self.spin1.setRange(-1, 1)
        
        #####
        # Se conecta con la función que actualiza la posición del CH1
        self.spin1.valueChanged.connect(self.actualiza_vpos1)
        # Evitar que aparezca el cuadro completo de la spinBox
        self.spin1.setMaximumWidth(18)
        self.spin1.setFixedHeight(40)  # Alto del widget
        gridLayout_2.addWidget(self.spin1, 2, 0, 1, 1, Qt.AlignCenter)
        
        # Spin posicion canal 2
        self.spin2 = QSpinBox(groupBox_2)
        self.spin2.setRange(-1, 1)
        
        #####
        self.spin2.valueChanged.connect(self.actualiza_vpos2)
        self.spin2.setMaximumWidth(18)
        self.spin2.setFixedHeight(40)
        gridLayout_2.addWidget(self.spin2, 2, 1, 1, 1, Qt.AlignCenter)
        
        # Label de "posicion" de canal 1
        label2_osc = QLabel("POSICION", groupBox_2)
        label2_osc.setFont(QtGui.QFont('Times New roman', 10))
        gridLayout_2.addWidget(label2_osc, 1, 0, Qt.AlignCenter)

        # Label posicion de canal 2
        label3_osc = QLabel("POSICION", groupBox_2)
        label3_osc.setFont(QtGui.QFont('Times New roman', 10))
        gridLayout_2.addWidget(label3_osc, 1, 1, Qt.AlignCenter)
        
        # Se tiene una resolucion de 3.3/1024= 3.22 mV
        # Esto se tomo en cuenta para los valores de Volts/Div dados
        
        # Propiedad combo3 instanciada a QComboBox
        combo3_osc = QComboBox(groupBox_2)
        combo3_osc.addItem('500 uV/div')  # Añade items al combo 3
        combo3_osc.addItem('1 mV/div')
        combo3_osc.addItem('2 mV/div')
        combo3_osc.addItem('5 mV/div')
        combo3_osc.addItem('10 mV/div')
        combo3_osc.addItem('20 mV/div')
        combo3_osc.addItem('50 mV/div')
        combo3_osc.addItem('100 mV/div')
        combo3_osc.addItem('500 mV/div')
        combo3_osc.addItem('1 V/div')
        combo3_osc.addItem('2 V/div')
        combo3_osc.addItem('5 V/div')
        combo3_osc.setCurrentIndex(1)
        
        #####
        # Conecta comportamiento del combo1_CH2 a lo establecido en metodo Vdiv
        combo3_osc.activated[str].connect(self.actualiza_vdiv1)
        gridLayout_2.addWidget(combo3_osc, 3, 0, Qt.AlignTop)
        
            # Dial volts/div de cnal 2
        combo4_osc = QComboBox(groupBox_2)
        combo4_osc.addItem('500 uV/div')  # Añade items al combo 4
        combo4_osc.addItem('1 mV/div')
        combo4_osc.addItem('2 mV/div')
        combo4_osc.addItem('5 mV/div')
        combo4_osc.addItem('10 mV/div')
        combo4_osc.addItem('20 mV/div')
        combo4_osc.addItem('50 mV/div')
        combo4_osc.addItem('100 mV/div')
        combo4_osc.addItem('500 mV/div')
        combo4_osc.addItem('1 V/div')
        combo4_osc.addItem('2 V/div')
        combo4_osc.addItem('5 V/div')
        combo4_osc.setCurrentIndex(1)
        
        #####
        # Conecta comportamiento del combo1_CH2 a lo establecido en metodo Vdiv
        combo4_osc.activated[str].connect(self.actualiza_vdiv2)
        gridLayout_2.addWidget(combo4_osc, 3, 1, Qt.AlignTop)
            
        # Label v/div canal 1
        label4_osc = QLabel("VOLTS/DIV", groupBox_2)
        label4_osc.setFont(QtGui.QFont('Times New roman', 9))
        gridLayout_2.addWidget(label4_osc, 4, 0, Qt.AlignCenter)
        # Label v/div canal2
        label5_osc = QLabel("VOLTS/DIV", groupBox_2)
        label5_osc.setFont(QtGui.QFont('Times New roman', 9))
        gridLayout_2.addWidget(label5_osc, 4, 1, Qt.AlignCenter)
        # ----------------- Avisos del canal----------------------------------
        self.avisoCh = QLabel(groupBox_2)
        # Establece tipo de letra
        self.avisoCh.setFont(QtGui.QFont('Times New Roman', 10))
        self.avisoCh.setStyleSheet('color:DeepPink')
        gridLayout_2.addWidget(self.avisoCh, 5, 0, 1, 0)
        # ---------------------------------------------------------------------
        # Se añade a gridLayout principal todo lo contenido en groupBox_2
        gridLayout.addWidget(groupBox_2, 1, 0, 1, 1)
        
        # -------------------- CAJA INFERIOR DERECHA--------------------------
        groupBox_3 = QGroupBox(widget)
        groupBox_3.setTitle("HORIZONTAL")
        # Objeto gridLayout_3 que contiene al groupBox_3
        gridLayout_3 = QGridLayout(groupBox_3)
        # Spin posicion horizontal
        self.spin5 = QSpinBox(groupBox_3)
        self.spin5.setRange(-1, 1)
        
        #####
        # Se conecta con la función para actualizar la posición en el tiempo de
        # la gráfica
        self.spin5.valueChanged.connect(self.actualiza_spos)
        self.spin5.setMaximumWidth(18)
        self.spin5.setFixedHeight(40)
        gridLayout_3.addWidget(self.spin5, 1, 1, Qt.AlignCenter)
        # La selección de la division del tiempo esta relacionada a la inversa
        # Con la tasa de muestreo teniendo en el MCP3008 una frecuencia de
        # Muestreo de 200ksps (kilo simbolos por segundo 200 kilomuestras de la
        # Señal por segundo) y basados en que en la aplicacion waveforms, a una
        # Tasa de 200 ksps se tiene 4ms/div
        
        # Se eligieron los sisguientes valores
        combo6_osc = QComboBox(groupBox_3)  # Combo sec/div
        combo6_osc.addItem('500 us/div')          # Añade items al combo 6
        combo6_osc.addItem('1 ms/div')
        combo6_osc.addItem('2 ms/div')
        combo6_osc.addItem('5 ms/div')
        combo6_osc.addItem('10 ms/div')
        combo6_osc.addItem('20 ms/div')
        combo6_osc.addItem('50 ms/div')
        combo6_osc.addItem('100 ms/div')
        combo6_osc.addItem('200 ms/div')
        combo6_osc.addItem('500 ms/div')
        combo6_osc.addItem('1 s/div')
        combo6_osc.addItem('2 s/div')
        combo6_osc.addItem('5 s/div')
        combo6_osc.addItem('6 s/div')
        combo6_osc.addItem('12 s/div')
        combo6_osc.addItem('30 s/div')
        combo6_osc.addItem('1 min/div')
        combo6_osc.setCurrentIndex(3)
        
        #####
        # Conecta comportamiento del combo6 a lo establecido en la función
        # actualiza_sdiv
        combo6_osc.activated[str].connect(self.actualiza_sdiv)
        gridLayout_3.addWidget(combo6_osc, 4, 0, 2, 1, Qt.AlignTop)
    
        # Combo para posicion central
        combo7_osc = QComboBox(groupBox_3)
        combo7_osc.addItem('1 min')  # Añade items al combo 6
        combo7_osc.addItem('20 s')
        combo7_osc.addItem('10 s')
        combo7_osc.addItem('5 s')
        combo7_osc.addItem('2 s')
        combo7_osc.addItem('1 s')
        combo7_osc.addItem('500 ms')
        combo7_osc.addItem('200 ms')
        combo7_osc.addItem('100 ms')
        combo7_osc.addItem('50 ms')
        combo7_osc.addItem('20 ms')
        combo7_osc.addItem('10 ms')
        combo7_osc.addItem('5 ms')
        combo7_osc.addItem('2 ms')
        combo7_osc.addItem('1 ms')
        combo7_osc.addItem('500 us')
        combo7_osc.addItem('0 s')
        combo7_osc.addItem('-500 us')
        combo7_osc.addItem('-1 ms')
        combo7_osc.addItem('-2 ms')
        combo7_osc.addItem('-5 ms')
        combo7_osc.addItem('-10 ms')
        combo7_osc.addItem('-20 ms')
        combo7_osc.addItem('-50 ms')
        combo7_osc.addItem('-100 ms')
        combo7_osc.addItem('-200 ms')
        combo7_osc.addItem('-500 ms')
        combo7_osc.addItem('-1 s')
        combo7_osc.addItem('-2 s')
        combo7_osc.addItem('-5 s')
        combo7_osc.addItem('-10 s')
        combo7_osc.addItem('-20 s')
        combo7_osc.addItem('-1 min')
        combo7_osc.setCurrentIndex(16)
        
        #####
        # Conecta comportamiento del combo1_CH2 a lo establecido con la función
        # actualiza_centro. Spos(usaremos trabslateby)
        combo7_osc.activated[str].connect(self.actualiza_centro)
        gridLayout_3.addWidget(combo7_osc, 6, 0, 2, 1, Qt.AlignTop)
        label6_osc = QLabel("POSICION", groupBox_3)
        label6_osc.setFont(QtGui.QFont('Times New roman', 10))
        gridLayout_3.addWidget(label6_osc, 1, 0)
        label7_osc = QLabel("SEC/DIV", groupBox_3)
        label7_osc.setFont(QtGui.QFont('Times New roman', 9))
        gridLayout_3.addWidget(label7_osc, 3, 0, Qt.AlignBottom)
        label8_osc = QLabel("POSICION CENTRO", groupBox_3)
        label8_osc.setFont(QtGui.QFont('Times New roman', 9))
        gridLayout_3.addWidget(label8_osc, 5, 0, Qt.AlignBottom)
        # Se añade a gridLayout principal lo contenido en groubBox_3
        gridLayout.addWidget(groupBox_3, 1, 1, 1, 2)
        
        # Se establece todo en la ventana
        tab_osc_.setLayout(gridLayout)
        
        return tab_osc_
    #----------------------------------------------------------------------------------

    # Método para actualizar la vista de las gráficas
    def update_views(self):
        # Como la vista ha cambiado de tamaño; hay actualizar vistas auxiliares
        # Para que coincidan
        self.graficaBox2.setGeometry(self.p1.vb.sceneBoundingRect())
        # Se necesita volver a actualizar los ejes vinculados ya que éstos se
        # Llamaron incorrectamente mientras que las vistas tenían diferentes
        # Formas.
        self.graficaBox2.linkedViewChanged(self.p1.vb, self.graficaBox2.XAxis)
    #-------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------
    # Método para mostrar la gráfica al usuario
    def correr_osc(self):
        # A el objeto que crea las pestañas se le aplica el método para
        # habilitar o deshabilitar las pestañas seleccionadas. 
        self.crea_tab.setTabEnabled(2, True)  # Habilita Oscoloscopio
        self.crea_tab.setTabEnabled(3, False) # Deshabilita Espectro
        # Se activa el botón de STOP para poner detener la señal
        self.pushButton2_osc.setEnabled(True)
        # Función para graficar la señal
        def grafica_muestras():
            # Variables utilizadas para medir tiempo en el metodo
            global time1
            global time2
            # Sólo corre si se ha selecionado un canal(CH1). Para valores reales
            if self.checkBoxch1.isChecked():
                """
                Parte de código que se utiliza para la conversión de analógica
                a digital para pequeñas frecuencias. Fue probado con el chip
                MCP3008. 
                
                self.spi.max_speed_hz = 1350000
                adc = self.spi.xfer2([1, (8+0) << 4, 0])
                data = ((adc[1] & 3) << 8) + adc[2]
                valor = data
                valor = interp(valor, [0, 1023], [0, 3.3])
                self.arreglo1.append(valor)
                # Se toma el tiempo para la muestra añadida.
                self.dt1 = (pg.ptime.time() - self.xmax) - self.Te1
                self.tiemp1.append(self.dt1)
                # Grafica en pantalla la señal leida
                self.curva.setData(self.tiemp1, self.arreglo1, pen='y')
                """
                self.curva.setData(self.x_CH1, self.signal_osc_CH1, pen='y')
                
            # Sólo corre si se ha selecionado un canal(CH2). Para simulación.
            if self.checkBoxch2.isChecked():
                self.curva2.setData(self.x_CH2, self.signal_osc_CH2, pen='#00FFFF')

            """
            Comentado por error en time1
            
            if self.var_t == self.aux_t:
                time1 = time.time()
            elif self.var_t == self.aux_t + 1:
                time2 = time.time()
                self.tiempo_t = time2 - time1
                # tiempotx = str(self.tiempo_t)
                # self.avisoCh.setText(tiempotx)
                self.aux_t = self.var_t + 1
                #return tiempo
            self.var_t = self.var_t + 1"""
        # Se inicia (o reinicia) el timer1 para el canal 1 del osciloscopio
        self.timer1.start()
        self.timer1.timeout.connect(grafica_muestras)
        # Se desactiva el botón RUN para que no se inicie repetidamente el
        # El timer de ambos canales y se acelere la gráfica
        self.pushButton1.setEnabled(False)
        
    #-------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------
    # Método para pausar la gráfica que se muestra en el osciloscopio
    def pausa(self):
        # Se habilita la pestaña del espectro en caso de querer usarlo
        self.crea_tab.setTabEnabled(3, True)  
        # Ambos timers de los canales del osciloscopio se detienen obedeciendo
        # A la pausa puesta por el usuario
        self.timer1.stop()
        # Se hace que ambos timers se desconecten para que no se haga un cambio
        # En la velocidad de la gráfica
        self.timer1.disconnect()
        # Se activa el botón RUN para volver a correr las gráficas de los
        # Canales
        self.pushButton1.setEnabled(True)
        # Se deshabilita el botón de STOP para que no tenga error el
        # Timer de cada canal
        self.pushButton2_osc.setEnabled(False)
    #-----------------------------------------------------------------------------------------
    
    # Método para guardar una imagen de la gráfica generada
    def save_graph_osc(self):
         # Se crea un objeto QMessageBox para preguntar al usuario cuál es
         # la imagen que quiere guardar, si del canal 1 o del canal 2
         mj_osc = QMessageBox()
         mj_osc.setIcon(QMessageBox.Question)
         mj_osc.setText('¿Deseas guardar una imagen de la gráfica mostrada?')
         mj_osc.setInformativeText('El archivo con formato .png será guardado'
                                   ' en la carpeta donde está ejcutandose la'
                                   ' aplicación.')
         mj_osc.addButton(QPushButton('Guardar'), QMessageBox.YesRole)
         mj_osc.addButton(QPushButton('Cancelar'), QMessageBox.NoRole)
            
         rv_osc = mj_osc.exec()
         if rv_osc == 0:
            # Se usa una condición en caso de qe no se pueda guardar la imagen
            try:
                # Se utiliza una instancia expoter para exportar la imagen que
                # se va a guardar
                exporter = pg.exporters.ImageExporter(self.graficaWidget1.plotItem)
                # Se agregan estos parámetros ya que la librería tiene un bug
                # al reportar los valores 'width' y 'height' con valores
                # flotantes. Por eso se le asignan valores fijos
                exporter.params.param('width').setValue(720, blockSignal=exporter.widthChanged)
                exporter.params.param('height').setValue(550, blockSignal=exporter.heightChanged)
                # Se exporta la imagen en formato .png y se guarda en la carpeta
                # donde se está ejecutando la aplicación
                exporter.export('Grafica_osciloscopio_Wav_I ('+str(self.ni_osc)+').png')
                QMessageBox.about(self, '¡Éxito!', 'La imagen ha sido guardada')
                self.ni_osc += 1
            except:
                QMessageBox.about(self, 'Atención', 'No se ha podido guardar la imagen,'
                                  ' vuelve a intentarlo') 
            finally:
                pass

    #--------------------------------------------------------------------------------------------
    #Método para hacer mediciones en la señal que se muestra
    def mediciones(self):
        msgo1 = QMessageBox()
        msgo1.setIcon(QMessageBox.Information)
        msgo1.setWindowTitle('Características de la señal')
        msgo1.setText('Los principales paramétros de la señal (CH1) simulada son:')
        bmo1 = str('Amplitud: ' + str(self.A_CH1) + ' V' + '\nFrecuencia: ' + str(round(self.f_CH1, 0)) + ' Hz' +
                 '\nPeriodo: ' + str(round(self.T_CH1, 8)) + ' s\n')
        msgo1.setInformativeText(bmo1)
        
        msgo1.addButton(QPushButton('Aceptar'), QMessageBox.YesRole)
        msgo1.addButton(QPushButton('Cerrar'), QMessageBox.RejectRole)
        # Se crea una cadena para poder incluir toda la información dentro del
        # Mensaje a mostrar
        amo1 = str('Los detalles de la simulación son los siguientes:\n'
        'Frecuencia de muestreo: ' + str(round(self.fs_CH1, 0)) + ' muestras/s' + 
        '\nNúmero de muestras tomadas: ' + str(round(self.N_CH1, 0)) + 
        ' ' + '\nFrecuencia de la señal simulada: ' + str(round(self.f_CH1, 0))
        + ' Hz')
        msgo1.setDetailedText(amo1)
        msgo1.exec_()  # Se ejecuta el mensaje
        
        
        msgo2 = QMessageBox()
        msgo2.setIcon(QMessageBox.Information)
        msgo2.setWindowTitle('Características de la señal')
        msgo2.setText('Los principales paramétros de la señal (CH2) simulada son:')
        bmo2 = str('Amplitud: ' + str(self.A_CH2) + ' V' + '\nFrecuencia: ' + str(round(self.f_CH2, 0)) + ' Hz' +
                 '\nPeriodo: ' + str(round(self.T_CH2, 8)) + ' s\n')
        msgo2.setInformativeText(bmo2)
    
        msgo2.addButton(QPushButton('Aceptar'), QMessageBox.YesRole)
        msgo2.addButton(QPushButton('Cerrar'), QMessageBox.RejectRole)
        # Se crea una cadena para poder incluir toda la información dentro del
        # Mensaje a mostrar
        amo2 = str('Los detalles de la simulación son los siguientes:\n'
        'Frecuencia de muestreo: ' + str(round(self.fs_CH2, 0)) + ' muestras/s' + 
        '\nNúmero de muestras tomadas: ' + str(round(self.N_CH2, 0)) + 
        ' ' + '\nFrecuencia de la señal simulada: ' + str(round(self.f_CH2, 0))
        + ' Hz')
        msgo2.setDetailedText(amo2)
        msgo2.exec_()  # Se ejecuta el mensaje
        
    #-------------------------------------------------------------------------------
        
    #---------------------------------------------------------------------------
    # Método para aplicar un auto ajuste a la gráfica mostrada
    def autoset(self):
        # isCheced verifica si el checkBox1 esta seleccionado
        if self.checkBox1.isChecked:
            self.auto1 = True
            self.auto2 = True
        else:
            self.auto1 = False
            self.auto2 = False
        # Se habilida el autorango para ajustar la gráfica a la vista del
        # Usuario. Inmediatamente se desactiva para que no quede en
        # Movimiento la gráfica
        self.graficaWidget1.enableAutoRange(axis='xy', enable=self.auto1)
        self.graficaWidget1.disableAutoRange(axis='xy')
        self.graficaWidget2.enableAutoRange(axis='xy', enable=self.auto2)
        self.graficaWidget2.disableAutoRange(axis='xy')
    #------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------
    # Método que manda un aviso al usuario
    def aviso_canal1(self):
        if self.checkBoxch1.isChecked():
            self.avisoCh.setText("Has seleccionado el canal 1")
            self.p1.getAxis('left').setGrid(200)
        elif self.checkBoxch1.isChecked() is False:
            self.curva.clear()
            self.p1.getAxis('left').setGrid(False)
    #-------------------------------------------------------------------------
           
    #-----------------------------------------------------------------------------
    # Método que manda un aviso relacionado al canal 2
    def aviso_canal2(self):
        if self.checkBoxch2.isChecked():
            self.avisoCh.setText("Has seleccionado el canal 2")
            self.p1.getAxis('right').setGrid(100)
        elif self.checkBoxch2.isChecked() is False:
            self.curva2.clear()
            self.p1.getAxis('right').setGrid(False)
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método para actualizar la posición de voltaje del CH1
    def actualiza_vpos1(self):
        self.posicionV1 = self.spin1.value()
        self.graficaBox1.translateBy(y=self.posicionV1*self.Vd1)
        self.spin1.setValue(0)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    #Método para actualizar la posicion de voltaje del CH2
    def actualiza_vpos2(self):
        self.posicionV2 = self.spin2.value()
        # graficaBox2 es el objeto viewbox del eje derecho vinculado
        self.graficaBox2.translateBy(y=self.posicionV2*self.Vd2)
        self.spin2.setValue(0)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para añadir los valores de los voltajes por división
    def actualiza_vdiv1(self,Vdiv):
        if Vdiv == '500 uV/div':
            self.Vd1 = 500e-6
        elif Vdiv == '1 mV/div':
            self.Vd1 = 1e-3
        elif Vdiv == '2 mV/div':
            self.Vd1 = 2e-3
        elif Vdiv == '5 mV/div':
            self.Vd1 = 5e-3
        elif Vdiv == '10 mV/div':
            self.Vd1 = 10e-3
        elif Vdiv == '20 mV/div':
            self.Vd1 = 20e-3
        elif Vdiv == '50 mV/div':
            self.Vd1 = 50e-3
        elif Vdiv == '100 mV/div':
            self.Vd1 = 100e-3
        elif Vdiv == '500 mV/div':
            self.Vd1 = 500e-3
        elif Vdiv == '1 V/div':
            self.Vd1 = 1
        elif Vdiv == '2 V/div':
            self.Vd1 = 2
        elif Vdiv == '5 V/div':
            self.Vd1 = 5
        # Mínimos y máximos en eje Y
        y1min = -5 * self.Vd1
        y1max = 5 * self.Vd1
        may = y1max  # Espaciado mayor en los ejes
        # Establece máximo y mínimo rango mostrado en la grafica
        self.graficaBox1.setYRange(y1min, y1max)
        # Si el voltaje seleccionado es menor o igual que 500mV may sera el
        # entero del maximo valor del rango mas 1
        if self.Vd1 <= 500e-3:
            may = round(y1max + 1)  # Guarda el valor entero
        ay1 = self.p1.getAxis('left')  # Obtiene el eje de la grafica
        ay1.setTickSpacing(may, y1max/5)
    
    #----------------------------------------------------------------------
        
    #---------------------------------------------------------------------
    # Método para añadir los valores de voltajes por division CH2
    def actualiza_vdiv2(self,Vdiv):
        if Vdiv == '500 uV/div':
            self.Vd2 = 500e-6
        elif Vdiv == '1 mV/div':
            self.Vd2 = 1e-3
        elif Vdiv == '2 mV/div':
            self.Vd2 = 2e-3
        elif Vdiv == '5 mV/div':
            self.Vd2 = 5e-3
        elif Vdiv == '10 mV/div':
            self.Vd2 = 10e-3
        elif Vdiv == '20 mV/div':
            self.Vd2 = 20e-3
        elif Vdiv == '50 mV/div':
            self.Vd2 = 50e-3
        elif Vdiv == '100 mV/div':
            self.Vd2 = 100e-3
        elif Vdiv == '500 mV/div':
            self.Vd2 = 500e-3
        elif Vdiv == '1 V/div':
            self.Vd2 = 1
        elif Vdiv == '2 V/div':
            self.Vd2 = 2
        elif Vdiv == '5 V/div':
            self.Vd2 = 5
        # Mínimos y máximos en eje Y
        y2min = -5 * self.Vd2
        y2max = 5 * self.Vd2
        may = y2max  # Espaciado mayor en los ejes
        # Establece el máximo y mínimo rango mostrado en la grafica
        self.graficaBox2.setYRange(y2min, y2max)    
        # Si el voltaje seleccionado es menor o igual que 500mV may sera el
        # Entero del maximo valor del rango mas 1
        if self.Vd2 <= 500e-3:
            may = round(y2max + 1)  # Guarda el valor entero
        ay2 = self.p1.getAxis('right')  # Obtiene el eje derecho de la grafica
        # Se usa p1 ya que es el plotItem principal que se vincula con el
        # ViewBox graficaBox2
        ay2.setTickSpacing(may, self.Vd2)
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método para actualizar la gráfica del osciloscopio, en el tiempo
    def actualiza_spos(self):
        self.posicion = self.spin5.value()
        self.graficaBox1.translateBy(x=self.posicion*self.Sd)
        self.spin5.setValue(0)
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método que actualiza las divisiones por tiempo del osciloscopio
    def actualiza_sdiv(self,Sdiv):
        if Sdiv == '500 us/div':
            self.Sd = 500e-6
        elif Sdiv == '1 ms/div':
            self.Sd = 1e-3
        elif Sdiv == '2 ms/div':
            self.Sd = 2e-3
        elif Sdiv == '5 ms/div':
            self.Sd = 5e-3
        elif Sdiv == '10 ms/div':
            self.Sd = 10e-3
        elif Sdiv == '20 ms/div':
            self.Sd = 20e-3
        elif Sdiv == '50 ms/div':
            self.Sd = 50e-3
        elif Sdiv == '100 ms/div':
            self.Sd = 100e-3
        elif Sdiv == '200 ms/div':
            self.Sd = 200e-3
        elif Sdiv == '500 ms/div':
            self.Sd = 500e-3
        elif Sdiv == '1 s/div':
            self.Sd = 1
        elif Sdiv == '2 s/div':
            self.Sd = 2
        elif Sdiv == '5 s/div':
            self.Sd = 5
        elif Sdiv == '6 s/div':
            self.Sd = 6
        elif Sdiv == '12 s/div':
            self.Sd = 12
        elif Sdiv == '30 s/div':
            self.Sd = 30
        elif Sdiv == '1 min/div':
            self.Sd = 60
        # Mínimos y máximos en eje X
        self.xmin = -5*self.Sd
        self.xmax = 5*self.Sd
        mayx = self.xmax
        # Establezca el rango X visible de la vista en [ min , max ].
        self.graficaWidget1.setXRange(self.centro+self.xmin,
                                      self.centro+self.xmax)
        # Si el tiempo seleccionado es menor o igual que 500ms may sera el
        # Entero del maximo valor del rango mas 1
        # Esto para establecer el mayor espaciamiento, ya que en valores 
        # Intermedios no tiene un buen comportamiento
        # Repite valores en el espaciamiento mayor
        if self.Sd <= 500e-3:
            # Guarda el valor entero
            mayx = round(self.xmax + 1)
        # Obtiene el eje de la grafica
        ax = self.graficaWidget1.getAxis('bottom')
        # Determinar explícitamente el espaciado de las garrapatas mayores y 
        # Menores.
        ax.setTickSpacing(mayx, self.Sd)  # (mayor,menor)
        # Límites de escala. Estos argumentos evitan que la vista se acerque o
        # Se aleje demasiado.
        self.graficaBox1.setLimits(minXRange=self.xmax, maxXRange=2*mayx)
        self.graficaBox2.setLimits(minXRange=self.xmax, maxXRange=2*mayx) 
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para actualizar la posición central de la gráfica
    def actualiza_centro(self,cent):
        # cent contiene a la cadena seleccionada en el combo del centro
        # Guarda el valor numerico contenido en la cadena
        numero = re.sub("\D", "", cent)
        # Variables que cuentan si aparecen ciertas unidades en la cadena
        cus = cent.count('us')
        cms = cent.count('ms')
        cs = cent.count('s')
        cmin = cent.count('min')
        cmenos = cent.count('-')
    
        # Primero se determina si hubo signo menos
        # Despues se multiplica al numero por el valor correspondiente segun 
        # Unidades
        if cmenos == 0:
            if cus == 1:
                numero = float(numero) * 1e-6
            elif cms == 1:
                numero = float(numero) * 1e-3
            elif cs == 1:
                numero = float(numero)
            elif cmin == 1:
                numero = float(numero) * 60
        elif cmenos == 1:
            if cus == 1:
                numero = float(numero) * -1e-6
            elif cms == 1:
                numero = float(numero) * -1e-3
            elif cs == 1:
                numero = float(numero) * -1
            elif cmin == 1:
                numero = float(numero) * -60
        self.centro = numero
        # Actualizacion en la grafica
        self.xmin = -5*self.Sd
        self.xmax = 5*self.Sd
        mayx = self.xmax
        self.graficaWidget1.setXRange(self.centro+self.xmin,
                                      self.centro+self.xmax)
        # Si el tiempo seleccionado es menor o igual que 500ms may sera el
        # Entero del maximo valor del rango mas 1
        if self.Sd <= 500e-3:
            # Guarda el valor entero
            mayx = round(self.xmax + 1)
        # Obtiene el eje de la grafica
        ax = self.graficaWidget1.getAxis('bottom')
        # (major,menor)
        ax.setTickSpacing(mayx, self.Sd)
        # Límites de escala . Estos argumentos evitan que la vista se acerque o
        # se aleje demasiado.
        self.graficaBox1.setLimits(minXRange=self.xmax, maxXRange=2*mayx)
        self.graficaBox2.setLimits(minXRange=self.xmax, maxXRange=2*mayx)
    #----------------------------------------------------------------------
        
# =============================================================================
#!!! ANALIZADOR DE ESPECTROS
# =============================================================================
    # Método para la pestaña analizador de espectro
    def tab_esp(self):

        tab_esp_ = QWidget()
        # Parámetros iniciales para al analizador de espectros
        self.Fd = 1     # Valor inicial de frecuencia por division
        self.Ad = 1     # valor inicial de amplitud por division
        # Parámetros iniciales para graficar un espectro
        self.opc = 0
        # Rangos de visualización por defecto para el eje y
        self.rangeymin = 1e-3
        self.rangeymax = 100e-3
        # Rangos de visuzalicación por defecto para el eje x
        self.rangexmin = -1e2
        self.rangexmax = 1e2
        # Variables para determinar el tiempo
        self.var = 0
        self.aux = 0
        # Ventana por defecto
        self.ventana_spc = 'hamming'
        # Valor de nfft por defecto 
        self.nfft_spc = 1024
        
        # Arreglos de frecuencia para las señales DC e impulso
        self.xan_CH1 = np.arange(-1.0, 1.0, 0.0001)
        self.xan_CH2 = np.arange(-1.0, 1.0, 0.0001)
        
        # Objeto de clase Qwidget, widget es el widget que es la ventana 1
        widget_spc = QWidget()
        # Se crea un objeto grid que será el principal para esta pestaña
        widget_spc.setObjectName("widget")
        # Grid_layout es el grid princicpal que contiene toodo en la ventana
        gridLayout_spc = QGridLayout(widget_spc)

        # -------------- Construcción del gráfico -----------------------------
        self.graficaWidget1_spc = pg.PlotWidget()  # Grafica de pyqtgraph
        """
        Se establecen los límites para la visualización del espectro. El
        valor más pequeño desde donde se visualiza el espectro es cero, es
        decir, no se podrá ver el espectro en el lado negativo. Funciona para
        ambos canales.
        """
        # Objeto plotItem de graficaWidget1
        self.p1_spc = self.graficaWidget1_spc.plotItem
        # Se esconde el botón por defecto de autorange para que no se mueva
        # La gráfica cada vez que se actualizan las muestras
        self.p1_spc.hideButtons()  
        
        # ---- Hay que revisar estas instrucciones con señales reales ----
        self.p1_spc.setDownsampling(auto=True, mode='peak')
        self.p1_spc.setClipToView(True)
        # ----------------------------------------------------------------
        
        # Se le da título a la gráfica del espectro
        self.p1_spc.setTitle('ESPECTRO DE POTENCIA')
        # self.p1.setLogMode(False, True)
        # Se crea un objeto que será la gráfica de los datos
        self.curva1 = self.graficaWidget1_spc.plot()
        # Se crea un nuevo objeto de pyqt para la gráfica del canal 2
        self.graficaWidget2_spc = pg.PlotWidget()
        
        # self.p2 = self.graficaWidget2_spc.plotItem
        # Se crea una caja que tome la vista de la gráfica del canal 2
        self.graficaBox2_spc = self.graficaWidget2_spc.getViewBox()
        # Se crea la curva para graficar los datos del canal 2
        self.curva2_spc = self.graficaWidget2_spc.plot()
        # Se anañde a la caja del canal 2 la gráfica para este canal
        self.graficaBox2_spc.addItem(self.curva2_spc)
        # ---------- Se configuran los canales y sus vistas ------------
        self.p1_spc.showAxis('right')  # Se muestra en eje derecho vertical
        # Se añade al objeto p1 de clase plotItem el objeto p2
        self.p1_spc.scene().addItem(self.graficaBox2_spc)
        # Se enlaze este eje a un ViewBox, haciendo que su rango visualizado
        # Coincida con el rango visible de la vista.
        self.p1_spc.getAxis('right').linkToView(self.graficaBox2_spc)
        # Se enlaza el eje X de esta vista a otra vista
        self.graficaBox2_spc.setXLink(self.p1_spc)
        
        #####
        self.update_views_spc()
        self.p1_spc.vb.sigResized.connect(self.update_views_spc)
        # Se establece la grafica en el gridLayout
        gridLayout_spc.addWidget(self.graficaWidget1_spc, 0, 3, 2, 1)
        # Muestra la cuadricula de la grafica(x, y, opacidad)
        self.graficaWidget1_spc.showGrid(x=True, y=True, alpha=1.0)
        # Título y unidades de label del eje y, izquierdo (canal 2)
        self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='V',
                                    color='#ffff00')
        # Título y unidades de label del eje y, derecho (canal 1)
        self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='V',
                                    color='#33FFF3')
        # Título y unidades de label del eje x
        self.graficaWidget1_spc.setLabel('bottom', 'Frecuencia', units='Hz')
        # graficaBox1 contiene a viewBox asociado a PLotWidget(graficaWidget1)
        self.graficaBox1_spc = self.graficaWidget1_spc.getViewBox()
        # Se deshabilita que se pueda mover el eje y de la gráfica con el ratón
        # Para el canal 1 y canal 2
        self.graficaBox1_spc.setMouseEnabled(y=False)
        self.graficaBox2_spc.setMouseEnabled(y=False)
        self.graficaBox1_spc.setXRange(self.rangexmin, self.rangexmax)
        
        # Se de lan características para que la señal muestreada sea
        # De tipo seno o coseno
        """
        (quereos Parametros obtenidos de genreador)
        self.fc = 2000     # Frecuencia de la señal
        self.fss = 30000.0  # Frecuencia de muestreo. Debe ser float
        self.Ts = 0.1     # Tiempo que se hace el muestreo
        self.N = self.fss * self.Ts   # Número de puntos de la señal
        self.omg = 2 * np.pi * self.fc
        # Instantes discretos de tiempo donde va a estar definida la señal
        self.TIME = np.linspace(0, self.Ts, int(self.fss * self.Ts),
                                endpoint=False)"""
        
        # Factor de corrección de la amplitud para la ventana. Con esto se 
        # Obtiene el valor de amplitud correcto
        self.corrt = 1.5  
 
        # Se crea un objeto de Timer que actualizará a las gráficas
        self.timer1_spc = pg.QtCore.QTimer()
        self.timer1_spc.setInterval(0)
        # ---------------------------------------------------------------------
        # ---------------- CAJA DE LA PARTE SUPERIOR --------------------------
        # groupBox_1 contiene los botones de la parte superior
        groupBox_1_spc = QGroupBox(widget_spc)
        groupBox_1_spc.setTitle("")
        # gridLayout1 que contiene a groupBox_1
        gridLayout1_spc = QGridLayout(groupBox_1_spc)
        
        # Objeto botón RUN
        self.pushButton1_spc = QPushButton("RUN", groupBox_1_spc)
        self.pushButton1_spc.setFont(QtGui.QFont('Times New Roman', 14,
                                             weight=QtGui.QFont.Bold))
        self.pushButton1_spc.setStyleSheet('background-color: #00F212;'
                                      'border: 1px solid black')
        gridLayout1_spc.addWidget(self.pushButton1_spc, 1, 0)
        
        #####
        #----------------------------------------------------------------------
        # Se conecta con la función que grafica al espectro de la gráfica
        self.pushButton1_spc.clicked.connect(self.run_espectro)
        
        # Objeto boton STOP
        self.pushButton2_spc = QPushButton("STOP", groupBox_1_spc)
        self.pushButton2_spc.setFont(QtGui.QFont('Times New Roman', 14,
                                             weight=QtGui.QFont.Bold))
        self.pushButton2_spc.setStyleSheet('color:#FFFFFF')
        self.pushButton2_spc.setStyleSheet('color: #FFFFFF; '
                                       'background-color: #FF0000;'
                                       'border: 1px solid black')
        gridLayout1_spc.addWidget(self.pushButton2_spc, 1, 1)
        
        #####
        # Se conecta con la función que detiene el espectro graficado y limpia
        # el grafico además
        self.pushButton2_spc.clicked.connect(self.stop_espectro)

        # Objeto boton MEASURE
        pushButton3_spc = QPushButton("MEDICIONES", groupBox_1_spc)
        pushButton3_spc.setFont(QtGui.QFont('Times New Roman', 14))
       
        gridLayout1_spc.addWidget(pushButton3_spc, 1, 3)
        pushButton3_spc.clicked.connect(self.mediciones_spc)

        # Se crea un botón para guardar la señal
        btn_save_psd = QPushButton('Guardar')
        btn_save_psd.setFont(QtGui.QFont('Times New Roman', 14,
                                           weight=QtGui.QFont.Bold))
        btn_save_psd.setStyleSheet('color: #FFFFFF;'
                                   'background-color: #4B9AFC;'
                                     'border: 1px solid black')
        btn_save_psd.clicked.connect(self.save_graph_psd)
        gridLayout1_spc.addWidget(btn_save_psd, 3, 3, Qt.AlignTop)
        
        # Objeto checkBox AUTOSET
        checkBox1_spc = QPushButton("AUTOSET", groupBox_1_spc)
        checkBox1_spc.setStyleSheet('color: #FFFFFF;'
                                       'background-color: #B775F8;'
                                       'border: 1px solid black')
        checkBox1_spc.setFont(QtGui.QFont('Times New Roman', 14,
                                           weight=QtGui.QFont.Bold))
        
        #####
        # Se conecta con la función para auto ajustar el espectro de la señal
        checkBox1_spc.clicked.connect(self.autosetsp)
        gridLayout1_spc.addWidget(checkBox1_spc, 2, 0)
        
        label_spc = QLabel("RANGO FRECUENCIA", groupBox_1_spc)
        label_spc.setFont(QtGui.QFont('Times New Roman', 13,
                                       weight=QtGui.QFont.Bold))
        gridLayout1_spc.addWidget(label_spc, 3, 0, 1, 2, Qt.AlignLeft)

        combo1_spc = QComboBox(groupBox_1_spc)
        # Se habilita que se pueda editar el combo por el usuario
        combo1_spc.setEditable(True)
        combo1_spc.addItem('0 Hz')
        combo1_spc.addItem('50 mHz')
        combo1_spc.addItem('100 mHz')
        combo1_spc.addItem('200 mHz')
        combo1_spc.addItem('500 mHz')
        combo1_spc.addItem('1 Hz')
        combo1_spc.addItem('2 Hz')
        combo1_spc.addItem('5 Hz')
        combo1_spc.addItem('10 Hz')
        combo1_spc.addItem('20 Hz')
        combo1_spc.addItem('50 Hz')
        combo1_spc.addItem('100 Hz')
        combo1_spc.addItem('200 Hz')
        combo1_spc.addItem('500 Hz')
        combo1_spc.addItem('1 kHz')
        combo1_spc.addItem('2 kHz')
        combo1_spc.addItem('5 kHz')
        combo1_spc.addItem('10 kHz')
        combo1_spc.addItem('20 kHz')
        combo1_spc.addItem('50 kHz')
        combo1_spc.addItem('100 kHz')
        combo1_spc.addItem('200 kHz')
        combo1_spc.addItem('500 kHz')
        combo1_spc.addItem('1 MHz')
        combo1_spc.addItem('2 MHz')
        combo1_spc.addItem('5 MHz')
        combo1_spc.addItem('10 MHz')
        combo1_spc.addItem('20 MHz')
        combo1_spc.setCurrentIndex(0)
        
        #####
        # Se conecta con la función que establece el rango mínimo de frecuencia
        # que se va a mostrar en la gráfica del espectro
        combo1_spc.activated[str].connect(self.rangox_fmin)
        gridLayout1_spc.addWidget(combo1_spc, 4, 1, Qt.AlignLeft)

        combo2_spc = QComboBox(groupBox_1_spc)
        combo2_spc.setEditable(True)
        combo2_spc.addItem('50 mHz')
        combo2_spc.addItem('100 mHz')
        combo2_spc.addItem('200 mHz')
        combo2_spc.addItem('500 mHz')
        combo2_spc.addItem('1 Hz')
        combo2_spc.addItem('2 Hz')
        combo2_spc.addItem('5 Hz')
        combo2_spc.addItem('10 Hz')
        combo2_spc.addItem('20 Hz')
        combo2_spc.addItem('50 Hz')
        combo2_spc.addItem('100 Hz')
        combo2_spc.addItem('200 Hz')
        combo2_spc.addItem('500 Hz')
        combo2_spc.addItem('1 kHz')
        combo2_spc.addItem('2 kHz')
        combo2_spc.addItem('5 kHz')
        combo2_spc.addItem('10 kHz')
        combo2_spc.addItem('20 kHz')
        combo2_spc.addItem('50 kHz')
        combo2_spc.addItem('100 kHz')
        combo2_spc.addItem('200 kHz')
        combo2_spc.addItem('500 kHz')
        combo2_spc.addItem('1 MHz')
        combo2_spc.addItem('2 MHz')
        combo2_spc.addItem('5 MHz')
        combo2_spc.addItem('10 MHz')
        combo2_spc.addItem('20 MHz')
        combo2_spc.addItem('50 MHz')
        combo2_spc.setCurrentIndex(0)
        
        #####
        # Se conecta con la función que establece el rango máximo de frecuencia
        # Que se va a mostrar en la gráfica del espectro
        combo2_spc.activated[str].connect(self.rangox_fmax)
        gridLayout1_spc.addWidget(combo2_spc, 4, 3, Qt.AlignLeft)
        
        label1_spc = QLabel("Inicio: ", groupBox_1_spc)
        label1_spc.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(label1_spc, 4, 0, Qt.AlignRight)

        label01_spc = QLabel("Fin: ", groupBox_1_spc)
        label01_spc.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(label01_spc, 4, 2, Qt.AlignRight)
        
        labelM_spc = QLabel("MAGNITUD", groupBox_1_spc)
        labelM_spc.setFont(QtGui.QFont('Times New Roman', 13,
                                        weight=QtGui.QFont.Bold))
        gridLayout1_spc.addWidget(labelM_spc, 5, 0, 1, 2, Qt.AlignLeft)
        
        # Combo para guardar los nombres de las distintas ventanas que se pueden
        # elegir
        comboty = QComboBox(groupBox_1_spc)
        comboty.addItem('Triangular')
        comboty.addItem('Blackman')
        comboty.addItem('Hamming')
        comboty.addItem('Hann')
        comboty.addItem('Bartlett')
        comboty.addItem('Flattop')
        comboty.setCurrentIndex(2)
        # Se conecta con la función que cambia la ventana que se aplica al 
        # espectro de potencia
        comboty.activated[str].connect(self.ventana)
        gridLayout1_spc.addWidget(comboty, 7, 1)
        
        # Combo para guardar los valores que puede tomar la nfft
        combot_nfft = QComboBox(groupBox_1_spc)
        combot_nfft.addItem('512')
        combot_nfft.addItem('1024')
        combot_nfft.addItem('2048')
        combot_nfft.addItem('4096')
        combot_nfft.addItem('8192')
        combot_nfft.setCurrentIndex(1)
        # Se hace la conexión con el método que cambia los valores de la nfft
        combot_nfft.activated[str].connect(self.p_nfft)
        gridLayout1_spc.addWidget(combot_nfft, 8, 1)
        
        combou = QComboBox(groupBox_1_spc)
        combou.addItem('Pico [V]')
        combou.addItem('RMS [V]')
        combou.addItem('Pico [dB]')
        combou.addItem('RMS [dB]')
        combou.addItem('Pico [dBm]')
        combou.addItem('dBV')
        combou.setCurrentIndex(0)
        gridLayout1_spc.addWidget(combou, 6, 1)
        
        #####
        # Se conecta con la función que define las unidades que se van a
        # Utilizar en la gráfica del espectro
        combou.activated[str].connect(self.actualiza_unid_v)
        
        self.comboi = QComboBox(groupBox_1_spc)
        self.comboi.addItem('Valor superior')
        self.comboi.setEditable(True)
        
        #####
        # Se conecta con la función que establece el valor máximo de amplitud
        # Que va a mostrar la gráfica del espectro
        self.comboi.activated[str].connect(self.rangoy_valormax)
        gridLayout1_spc.addWidget(self.comboi, 6, 3)

        self.combof = QComboBox(groupBox_1_spc)
        self.combof.addItem('Valor inferior')
        self.combof.setEditable(True)
        
        #####
        # Se conecta con la función que establece el valor mínimo de amplitud
        # Que se va a mostrar en el gráfico del espectro
        self.combof.activated[str].connect(self.rangoy_valormin)
        gridLayout1_spc.addWidget(self.combof, 7, 3)
        
        labelty = QLabel("Ventana: ", groupBox_1_spc)
        labelty.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(labelty, 7, 0, Qt.AlignCenter)
        
        labelnfft = QLabel('Puntos nfft: ', groupBox_1_spc)
        labelnfft.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(labelnfft, 8, 0, Qt.AlignCenter)

        labelu = QLabel("Unidades: ", groupBox_1_spc)
        labelu.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(labelu, 6, 0, Qt.AlignCenter)

        labeli = QLabel("Máximo: ", groupBox_1_spc)
        labeli.setFont(QtGui.QFont('Times New Roman', 12, Qt.AlignRight))
        gridLayout1_spc.addWidget(labeli, 6, 2)

        labelf = QLabel("Mínimo: ", groupBox_1_spc)
        labelf.setFont(QtGui.QFont('Times New Roman', 12,))
        gridLayout1_spc.addWidget(labelf, 7, 2, Qt.AlignRight)
        # Se añade a gridLayout principal toodo lo contenido en groupBox_1
        gridLayout_spc.addWidget(groupBox_1_spc, 0, 0, 1, 3)
                # ------------------ CAJA INFERIOR IZQUIERDA --------------------------
        groupBox_2_spc = QGroupBox(widget_spc)
        groupBox_2_spc.setTitle("CONTROL VERTICAL")
        gridLayout_2_spc = QGridLayout(groupBox_2_spc)

        # Boton canal1
        self.checkBoxch1_spc = QCheckBox("CH1", groupBox_2_spc)
        self.checkBoxch1_spc.setFont(QtGui.QFont('Times New Roman', 12,
                                             weight=QtGui.QFont.Bold))
        self.checkBoxch1_spc.setStyleSheet('background-color: #FFF641')
        
        #####
        # Se conecta con la función que avisa cuando se ha elegido el canal 1
        self.checkBoxch1_spc.clicked.connect(self.aviso_canal1sp)
        gridLayout_2_spc.addWidget(self.checkBoxch1_spc, 0, 0)
        gridLayout_2_spc.setColumnMinimumWidth(1, 20)

        # Boton canal 2
        self.checkBoxch2_spc = QCheckBox("CH2", groupBox_2_spc)
        self.checkBoxch2_spc.setFont(QtGui.QFont('Times New Roman', 12,
                                             weight=QtGui.QFont.Bold))
        self.checkBoxch2_spc.setStyleSheet('Background-color: #2595FF')
        
        #####
        # Se conecta con la función que avisa cuando se ha elegifo el canal 2
        self.checkBoxch2_spc.clicked.connect(self.aviso_canal2sp)
        gridLayout_2_spc.addWidget(self.checkBoxch2_spc, 0, 2)
        
        # Spin, posicion vertical de canal1
        self.spin1_spc = QSpinBox(groupBox_2_spc)
        # Establece el rango que contendra el dial -1 a 1
        self.spin1_spc.setRange(-1, 1)
        
        #####
        # Se conecta con la función que actualiza la posición de la gráfica
        # Respecto a la amplitud, con referencia al canal 1
        self.spin1_spc.valueChanged.connect(self.actualiza_vpos1sp)
        # Se evita que aparezca el cuadro completo de la spinBox
        self.spin1_spc.setMaximumWidth(18)
        self.spin1_spc.setFixedHeight(40)  # Alto del widget
        gridLayout_2_spc.addWidget(self.spin1_spc, 2, 0, Qt.AlignCenter)
        
        # Spin, posicion vertical del canal 2
        self.spin2_spc = QSpinBox(groupBox_2_spc)
        self.spin2_spc.setRange(-1, 1)
        
        #####
        # Se conecta con la función que actualiza la posición de la gráfica
        # Respecto a la amplitud, con referencia al canal 2
        self.spin2_spc.valueChanged.connect(self.actualiza_vpos2sp)
        self.spin2_spc.setMaximumWidth(18)
        self.spin2_spc.setFixedHeight(40)
        gridLayout_2_spc.addWidget(self.spin2_spc, 2, 2, Qt.AlignCenter)
        
        label2_spc = QLabel("POSICIÓN", groupBox_2_spc)
        label2_spc.setFont(QtGui.QFont('Times New Roman', 12))
        gridLayout_2_spc.addWidget(label2_spc, 1, 0, Qt.AlignBottom)
        label3_spc = QLabel("POSICIÓN", groupBox_2_spc)
        label3_spc.setFont(QtGui.QFont('Times New Roman', 12))
        gridLayout_2_spc.addWidget(label3_spc, 1, 2, Qt.AlignBottom)
        
        # Label para mostrar el aviso del canal elegido
        self.avisoCh1 = QLabel(groupBox_2_spc)
        self.avisoCh1.setFont(QtGui.QFont('Times New Roman', 10))
        self.avisoCh1.setStyleSheet('color:DeepPink')
        gridLayout_2_spc.addWidget(self.avisoCh1, 3, 0, Qt.AlignCenter)

        self.avisoCh2 = QLabel(groupBox_2_spc)
        self.avisoCh2.setFont(QtGui.QFont('Times New Roman', 10))
        self.avisoCh2.setStyleSheet('color:DeepPink')
        gridLayout_2_spc.addWidget(self.avisoCh2, 3, 2, Qt.AlignCenter)
        # ---------------------------------------------------------------------
        # Se añade a gridLayout principal toodo lo contenido en groupBox_2
        gridLayout_spc.addWidget(groupBox_2_spc, 1, 0, 1, 1)
        
        # ----------------------- CAJA INFERIOR DERECHA -----------------------
        groupBox_3_spc = QGroupBox(widget_spc)
        groupBox_3_spc.setTitle("CONTROL HORIZONTAL")
        # Objeto gridLayout_3 que contiene al groupBox_3
        gridLayout_3_spc = QGridLayout(groupBox_3_spc)

        # Spin que maneja la posicion horizontal, frecuencia
        self.spin5_spc = QSpinBox(groupBox_3_spc)
        self.spin5_spc.setRange(-1, 1)
        
        #####
        # Se conecta con la función que actualiza la posición horizontal de la
        # Gráfica del espectro
        self.spin5_spc.valueChanged.connect(self.actualiza_fpos)
        self.spin5_spc.setMaximumWidth(18)
        self.spin5_spc.setFixedHeight(40)
        gridLayout_3_spc.addWidget(self.spin5_spc, 1, 0, Qt.AlignCenter)
        
        label6_spc = QLabel("POSICIÓN", groupBox_3_spc)
        label6_spc.setFont(QtGui.QFont('Times New Roman', 11))
        gridLayout_3_spc.addWidget(label6_spc, 0, 0, Qt.AlignCenter)
        # --------------------------------------------------------------------
        # Se añade a gridLayout principal lo contenido en groubBox_3
        gridLayout_spc.addWidget(groupBox_3_spc, 1, 1, 1, 2)
        
        # Se establecen todos los child widgets al grid principal
        tab_esp_.setLayout(gridLayout_spc)
        
        return tab_esp_
    #----------------------------------------------------------------------
    # Método para actualizar la vista de las gráficas
    def update_views_spc(self):
        # Como la vista ha cambiado de tamaño; se hacen actualizar las
        # Vistas auxiliares para que coincidan
        self.graficaBox2_spc.setGeometry(self.p1_spc.vb.sceneBoundingRect())
        # Se necesita volver a actualizar los ejes vinculados ya que éstos
        # se llamaron incorrectamente mientras que las vistas tenían
        # diferentes formas
        self.graficaBox2_spc.linkedViewChanged(self.p1_spc.vb, self.graficaBox2_spc.XAxis)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para iniciar el espectro de la señal
    def run_espectro(self):
        self.crea_tab.setTabEnabled(3, True)  # Habilita Espectro
        self.crea_tab.setTabEnabled(2, False) # Deshabilita Osciloscopio
        # Se activa el botón de STOP para poder detener el espectro
        self.pushButton2_spc.setEnabled(True)
        # Función para graficar el espectro de la señal
        def grafica_mu_spc():
            """
            
            Cada vez que vuelve a iniciar el Timer que actualiza los valores de
            Cada señal, se le suma un valor de una distribución normal con una
            desviación estándar de 5 y un tamaño 
            (número de muestras regresadas) de 10e3 para que coincida con las 
            Muestras que tiene la señal simulada
            """
            # Variables utilizadas para medir tiempo en el metodo
            global time1
            global time2
            # Se obtienen dos listas con los valores de la amplitud y la
            # frecuencia de la señal: su espectro
            self.spc1, self.pxx1 = signal.welch(self.signal_spc_CH1, self.fs_CH1,
                                                self.ventana_spc, nperseg=512,
                                                noverlap=128,
                                                nfft=self.nfft_spc, return_onesided=False,
                                                scaling='spectrum')

            self.spc2, self.pxx2 = signal.welch(self.signal_spc_CH2, self.fs_CH2,
                                                self.ventana_spc, nperseg=512,
                                                noverlap=128,
                                                nfft=self.nfft_spc, return_onesided=False,
                                                scaling='spectrum')
                
            self.spc1 = fftshift(self.spc1)
            self.pxx1 = fftshift(self.pxx1)/self.corrt
            
            self.spc2 = fftshift(self.spc2)
            self.pxx2 = fftshift(self.pxx2)/self.corrt


            if self.signal_generador_CH1 == 'Impulso':
                self.spc1 = self.xan_CH1
                self.pxx1 = np.ones(len(self.spc1)) * self.A_CH1

            if self.signal_generador_CH2 == 'Impulso':
                self.spc2 = self.xan_CH2
                self.pxx2 = np.ones(len(self.spc2)) * self.A_CH2
                
            if self.signal_generador_CH1 == 'DC':
                self.spc1=self.xan_CH1
                self.pxx1=self.A_CH1 * signal.unit_impulse(len(self.spc1), 'mid')
                
            if self.signal_generador_CH2 == 'DC':
                self.spc2=self.xan_CH2
                self.pxx2=self.A_CH2 * signal.unit_impulse(len(self.spc2), 'mid')

            
            # Se verifica que sólo el canal 1 ha sido elegido
            if self.checkBoxch1_spc.isChecked():
                # Se grafica el espectro con los valores obtenidos anteriormente
                # Se utiliza el identificador del método actualiza_unidades para
                # definir las unidades de la gráfica a mostrar
                if self.opc == 0:
                    # Se limpia la gráfica del canal 1
                    self.curva1.clear()
                    # Se obtiene la raíz cuadrada para tene real valor en V
                    if self.signal_generador_CH1 == 'Impulso' or self.signal_generador_CH1 == 'DC':
                        self.vpxx1 = self.pxx1
                        self.curva1.setData(self.vpxx1, pen='y', clear=True)
                    else:
                        self.vpxx1 = np.sqrt(self.pxx1)
                        
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='V')
                    self.curva1.setData(self.spc1, self.vpxx1, pen='y', clear=True)
                
                elif self.opc == 1:
                    self.curva1.clear()
                    # Se calculan los valores RMS de la amplitud, del espectro de
                    # la señal elegida
                    self.uRMS = np.sqrt(self.pxx1)/np.sqrt(2)
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='V')
                    self.curva1.setData(self.spc1, self.uRMS, pen='y',
                                        clear=True)
                elif self.opc == 2:
                    self.curva1.clear()
                    # Se calculan los valores en decibelios
                    self.udB = 10 * np.log10(self.pxx1)
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='dB')
                    self.curva1.setData(self.spc1, self.udB, pen='y',
                                        clear=True)
                elif self.opc == 3:
                    self.curva1.clear()
                    # se calculan los valores en RMSdB
                    self.uRMSdB = 10 * np.log10(self.pxx1/np.sqrt(2))
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='dB')
                    self.curva1.setData(self.spc1, self.uRMSdB, pen='y',
                                        clear=True)
                elif self.opc == 4:
                    self.curva1.clear()
                    # Se calcualn los valores en dBV
                    self.udBV = 10 * np.log10((self.pxx1/np.sqrt(2))/1)
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='dBV')
                    self.curva1.setData(self.spc1, self.udBV, pen='y',
                                        clear=True)
                elif self.opc == 5:
                    self.curva1.clear()
                    # Se calculan los valores en dBu
                    self.dBm = 10 * np.log10(self.pxx1/0.001)
                    self.graficaWidget1_spc.setLabel('left', 'Amplitud', units='dBm')
                    self.curva1.setData(self.spc1, self.dBm, pen='y',
                                        clear=True)
            # Se verifica que sólo el canal 2 ha sido elegido
            if self.checkBoxch2_spc.isChecked():
                if self.opc == 0:
                    self.curva2_spc.clear()
                    if self.signal_generador_CH2 == 'Impulso' or self.signal_generador_CH2 == 'DC':
                        self.vpxx2 = self.pxx2
                        self.curva2_spc.setData(self.vpxx2, pen='#00FFFF', clear=True)
                    else:
                        self.vpxx2 = np.sqrt(self.pxx2)
                    
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='V')
                    self.curva2_spc.setData(self.spc2, self.vpxx2, pen='#00FFFF')
                elif self.opc == 1:
                    self.curva2_spc.clear()
                    self.uRMS = np.sqrt(self.pxx2)/np.sqrt(2)
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='V')
                    self.curva2_spc.setData(self.spc2, self.uRMS,
                                            pen='#00FFFF', clear=True)
                elif self.opc == 2:
                    self.curva2_spc.clear()
                    self.udB = 10 * np.log10(self.pxx2)
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='dB')
                    self.curva2_spc.setData(self.spc2, self.udB,
                                            pen='#00FFFF', clear=True)
                elif self.opc == 3:
                    self.curva2_spc.clear()
                    self.uRMSdB = 10 * np.log10(self.pxx2/np.sqrt(2))
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='dB')
                    self.curva2_spc.setData(self.spc2, self.uRMSdB,
                                            pen='#00FFFF', clear=True)
                elif self.opc == 4:
                    self.curva2_spc.clear()
                    self.udBV = 10 * np.log10((self.pxx2/np.sqrt(2))/1)
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='dBV')
                    self.curva2_spc.setData(self.spc2, self.udBV,
                                            pen='#00FFFF', clear=True)
                elif self.opc == 5:
                    self.curva2_spc.clear()
                    self.dBm = 10 * np.log10(self.pxx2/0.001)
                    self.graficaWidget1_spc.setLabel('right', 'Amplitud', units='dBm')
                    self.curva2_spc.setData(self.spc2, self.dBm,
                                            pen='#00FFFF', clear=True)
            
            #Esta seccion de codigo se uso para monitoreo de tiempos de ejecucion de la aplicación 
            if self.var == self.aux:
                time1 = time.time()
            elif self.var == self.aux + 1:
                time2 = time.time()
                # tiempo = time2 - time1
                # tiempotx = str(tiempo)
                # tiempotx = str(np.array(self.pxx2[self.picos]))
                # self.avisoCh1.setText(tiempotx)
                self.aux = self.var + 1
                #return tiempo
            self.var = self.var + 1
            
        # Se inicia (o reinicia) el timer1 para el canal 1 del osciloscopio
        self.timer1_spc.start()
        # Se conecta con el canal1 el timer 1 y se grafica la señal
        self.timer1_spc.timeout.connect(grafica_mu_spc)
        # Se desactiva el botón RUN para que no se inicie repetidamente el
        # El timer de ambos canales y se acelere la gráfica
        self.pushButton1_spc.setEnabled(False)
    #----------------------------------------------------------------------
        
    # Método para guardar una imagen de la gráfica generada
    def save_graph_psd(self):
         # Se crea un objeto QMessageBox para preguntar al usuario cuál es
         # la imagen que quiere guardar, si del canal 1 o del canal 2
         mj_psd = QMessageBox()
         mj_psd.setIcon(QMessageBox.Question)
         mj_psd.setText('¿Deseas guardar una imagen de la gráfica mostrada?')
         mj_psd.setInformativeText('El archivo con formato .png será guardado'
                                   ' en la carpeta donde está ejcutandose la'
                                   ' aplicación.')
         mj_psd.addButton(QPushButton('Guardar'), QMessageBox.YesRole)
         mj_psd.addButton(QPushButton('Cancelar'), QMessageBox.NoRole)
            
         rv_psd = mj_psd.exec()
         if rv_psd == 0:
            # Se usa una condición en caso de qe no se pueda guardar la imagen
            try:
                # Se utiliza una instancia expoter para exportar la imagen que
                # se va a guardar
                exporter_psd = pg.exporters.ImageExporter(self.graficaWidget1_spc.plotItem)
                # Se agregan estos parámetros ya que la librería tiene un bug
                # al reportar los valores 'width' y 'height' con valores
                # flotantes. Por eso se le asignan valores fijos
                exporter_psd.params.param('width').setValue(720, blockSignal=exporter_psd.widthChanged)
                exporter_psd.params.param('height').setValue(550, blockSignal=exporter_psd.heightChanged)
                # Se exporta la imagen en formato .png y se guarda en la carpeta
                # donde se está ejecutando la aplicación
                exporter_psd.export('Grafica_espectro_Wav_I ('+str(self.ni_spc)+').png')
                QMessageBox.about(self, '¡Éxito!', 'La imagen ha sido guardada')
                self.ni_spc += 1
            except:
                QMessageBox.about(self, 'Atención', 'No se ha podido guardar la imagen,'
                                  ' vuelve a intentarlo') 
            finally:
                pass
    #Método para hacer mediciones del espectro que se muestra
    def mediciones_spc(self):
        msge1 = QMessageBox()
        msge1.setIcon(QMessageBox.Information)
        msge1.setWindowTitle('Características de la señal')
        msge1.setText('Los principales paramétros de la señal (CH1) simulada son:')
        bme1 = str('Frecuencia: ' + str(round(self.f_CH1, 0)) + ' Hz\n')
        msge1.setInformativeText(bme1)
        
        msge1.addButton(QPushButton('Aceptar'), QMessageBox.YesRole)
        msge1.addButton(QPushButton('Cerrar'), QMessageBox.RejectRole)
        # Se crea una cadena para poder incluir toda la información dentro del
        # Mensaje a mostrar
        ame1 = str('Los detalles de la simulación son los siguientes:\n'
        'Frecuencia de muestreo: ' + str(round(self.fs_CH1, 0)) + ' muestras/s' + 
        '\nNúmero de muestras tomadas: ' + str(round(self.nfft_spc, 0)) + 
        ' ' + '\nFrecuencia de la señal simulada: ' + str(round(self.f_CH1, 0))
        + ' Hz')
        msge1.setDetailedText(ame1)
        msge1.exec_()  # Se ejecuta el mensaje
        
        
        msge2 = QMessageBox()
        msge2.setIcon(QMessageBox.Information)
        msge2.setWindowTitle('Características de la señal')
        msge2.setText('Los principales paramétros de la señal (CH2) simulada son:')
        bme2 = str('Frecuencia: ' + str(round(self.f_CH2, 0)) + ' Hz\n')
        msge2.setInformativeText(bme2)
    
        msge2.addButton(QPushButton('Aceptar'), QMessageBox.YesRole)
        msge2.addButton(QPushButton('Cerrar'), QMessageBox.RejectRole)
        # Se crea una cadena para poder incluir toda la información dentro del
        # Mensaje a mostrar
        ame2 = str('Los detalles de la simulación son los siguientes:\n'
        'Frecuencia de muestreo: ' + str(round(self.fs_CH2, 0)) + ' muestras/s' + 
        '\nNúmero de muestras tomadas: ' + str(round(self.nfft_spc, 0)) + 
        ' ' + '\nFrecuencia de la señal simulada: ' + str(round(self.f_CH2, 0))
        + ' Hz')
        msge2.setDetailedText(ame2)
        msge2.exec_()  # Se ejecuta el mensaje
        
    #-------------------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método para detener el espectro
    def stop_espectro(self):
        self.crea_tab.setTabEnabled(2, True)  # Habilita Osciloscopio
        # El timer de los dos canales se pone en pause
        self.timer1_spc.stop()
        # Se desconecta el objeto Timer para que cuando reinicie o inicie su
        # Cuenta de nuevo, no acumule valores pasado y haga más rápida la 
        # Actualización de valores
        self.timer1_spc.disconnect()
        # Se activa el botón RUN para volver a correr las gráficas de los
        # Canales
        self.pushButton1_spc.setEnabled(True)
        # Se desactiva el botón STOP paraevitar un error en el Timer de cada
        # Canal
        self.pushButton2_spc.setEnabled(False)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para autoset de la gráfica
    def autosetsp(self):
        # Se verifica si ha sido seleccionada la casilla del autoset
        if self.checkBox1.isChecked:
            # Se cambia de estado la variable que activa el autoset
            auto1_spc = True
            auto2_spc = True
        else:
            auto1_spc = False
            auto2_spc = False
        # Se da autoset a las gráficas de los dos canales. Se desactiva después
        # Para evitar movimiento de la gráfica
        self.graficaWidget1_spc.enableAutoRange(axis='xy', enable=auto1_spc)
        self.graficaWidget1_spc.disableAutoRange(axis='xy')
        self.graficaWidget2_spc.enableAutoRange(axis='xy', enable=auto2_spc)
        self.graficaWidget2_spc.disableAutoRange(axis='xy')
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método para actualizar los valores del rango x en la gráfica
    def rangox_fmin(self,R):
        # Se comprueba que el valor elegido, guardado en la variable R, sea el
        # Que coincide con las unidades seleccionadas para la frecuencia
        if R == '0 Hz':
            # Se le da un valor al valor mínimo
            self.rangexmin = 0
        elif R == '50 mHz':
            self.rangexmin = 50e-3
        elif R == '100 mHz':
            self.rangexmin = 100e-3
        elif R == '500 mHz':
            self.rangexmin = 500e-3
        elif R == '1 Hz':
            self.rangexmin = 1
        elif R == '2 Hz':
            self.rangexmin = 2
        elif R == '5 Hz':
            self.rangexmin = 5
        elif R == '10 Hz':
            self.rangexmin = 10
        elif R == '20 Hz':
            self.rangexmin = 20
        elif R == '50 Hz':
            self.rangexmin = 50
        elif R == '100 Hz':
            self.rangexmin = 100
        elif R == '200 Hz':
            self.rangexmin = 200
        elif R == '500 Hz':
            self.rangexmin = 500
        elif R == '1 kHz':
            self.rangexmin = 1e3
        elif R == '2 kHz':
            self.rangexmin = 2e3
        elif R == '5 kHz':
            self.rangexmin = 5e3
        elif R == '10 kHz':
            self.rangexmin = 10e3
        elif R == '20 kHz':
            self.rangexmin = 20e3
        elif R == '50 kHz':
            self.rangexmin = 50e3
        elif R == '100 kHz':
            self.rangexmin = 100e3
        elif R == '200 kHz':
            self.rangexmin = 200e3
        elif R == '500 kHz':
            self.rangexmin = 500e3
        elif R == '1 MHz':
            self.rangexmin = 1e6
        elif R == '2 MHz':
            self.rangexmin = 2e6
        elif R == '5 MHz':
            self.rangexmin = 5e6
        elif R == '10 MHz':
            self.rangexmin = 10e6
        elif R == '20 MHz':
            self.rangexmin = 20e6
        # Se definen los límites, para el eje x,  de la gráfica del
        # Espectro con los valores elegidos por el usuario
        self.graficaWidget1_spc.setXRange(self.rangexmin,
                                          self.rangexmax, padding=None, update=True)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para establacer el rango de la frecuencia que se muestra
    def rangox_fmax(self,R):
        if R == '50 mHz':
             # Se le asigna una constante al valor máximo de frecuencia
            self.rangexmax = 50e-3
        elif R == '100 mHz':
            self.rangexmax = 100e-3
        elif R == '500 mHz':
            self.rangexmax = 500e-3
        elif R == '1 Hz':
            self.rangexmax = 1
        elif R == '2 Hz':
            self.rangexmax = 2
        elif R == '5 Hz':
            self.rangexmax = 5
        elif R == '10 Hz':
            self.rangexmax = 10
        elif R == '20 Hz':
            self.rangexmax = 20
        elif R == '50 Hz':
            self.rangexmax = 50
        elif R == '100 Hz':
            self.rangexmax = 100
        elif R == '200 Hz':
            self.rangexmax = 200
        elif R == '500 Hz':
            self.rangexmax = 500
        elif R == '1 kHz':
            self.rangexmax = 1e3
        elif R == '2 kHz':
            self.rangexmax = 2e3
        elif R == '5 kHz':
            self.rangexmax = 5e3
        elif R == '10 kHz':
            self.rangexmax = 10e3
        elif R == '20 kHz':
            self.rangexmax = 20e3
        elif R == '50 kHz':
            self.rangexmax = 50e3
        elif R == '100 kHz':
            self.rangexmax = 100e3
        elif R == '200 kHz':
            self.rangexmax = 200e3
        elif R == '500 kHz':
            self.rangexmax = 500e3
        elif R == '1 MHz':
            self.rangexmax = 1e6
        elif R == '2 MHz':
            self.rangexmax = 2e6
        elif R == '5 MHz':
            self.rangexmax = 5e6
        elif R == '10 MHz':
            self.rangexmax = 10e6
        elif R == '20 MHz':
            self.rangexmax = 20e6
        elif R == '50 MHz':
            self.rangexmax = 50e6
        # Se definen los límites, para el eje x,  de la gráfica del
        # Espectro con los valores elegidos por el usuario
        self.graficaWidget1_spc.setXRange(self.rangexmin,
                                          self.rangexmax, padding=None, update=True)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para cambiar la ventana que se aplica al espectro
    def ventana(self,w):
        if w == 'Triangular':
            self.ventana_spc = 'triang'
        elif w == 'Blackman':
            self.ventana_spc = 'blackman'
        elif w == 'Hamming':
            self.ventana_spc = 'hamming'
        elif w == 'Hann':
            self.ventana_spc = 'hann'
        elif w == 'Bartlett':
            self.ventana_spc = 'bartlett'
        elif w == 'Flattop':
            self.ventana_spc = 'flattop'
    #----------------------------------------------------------------------
    
    #---------------------------------------------------------------------
    # Método para cambiar el número de puntos con el que se está representando
    # la trasnformadas discreta de Fourier
    def p_nfft(self, p):
        if p == '512':
            self.nfft_spc = 512
        elif p == '1024':
            self.nfft_spc = 1024
        elif p == '2048':
            self.nfft_spc = 2048
        elif p == '4096':
            self.nfft_spc = 4096
        elif p == '8192':
            self.nfft_spc = 8192
    #--------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para definir las unidades de V del espectro
    def actualiza_unid_v(self,unidad):
        if unidad == 'Pico [V]' or unidad == 'RMS [V]':
            # Se crea una variable que va a indentificar el tipo de unidad que
            # Se utilizará para la gráfica del espectro
            if unidad == 'Pico [V]':
                self.opc = 0
            elif unidad == 'RMS [V]':
                self.opc = 1
                # Se quitan todos los elementos del combo para mostrar unas nuevas
                # Unidades
            self.combof.clear()
            self.combof.addItem('25 V')
            self.combof.addItem('10 V')
            self.combof.addItem('5 V')
            self.combof.addItem('2 V')
            self.combof.addItem('1 V')
            self.combof.addItem('500 mV')
            self.combof.addItem('200 mV')
            self.combof.addItem('100 mV')
            self.combof.addItem('50 mV')
            self.combof.addItem('20 mV')
            self.combof.addItem('10 mV')
            self.combof.addItem('5 mV')
            self.combof.addItem('2 mV')
            self.combof.addItem('1 mV')
            self.combof.addItem('500 uV')
            self.combof.addItem('200 uV')
            self.combof.addItem('100 uV')
            self.combof.addItem('50 uV')
            self.combof.addItem('20 uV')
            self.combof.addItem('10 uV')
            self.combof.addItem('5 uV')
            self.combof.addItem('2 uV')
            self.combof.addItem('1 uV')
            self.combof.addItem('500 nV')
            self.combof.addItem('200 nV')
            self.combof.addItem('100 nV')
            self.combof.addItem('50 nV')
            self.combof.addItem('20 nV')
            self.combof.addItem('10 nV')
            self.combof.addItem('5 nV')
            self.combof.addItem('2 nV')
            self.combof.addItem('1 nV')
            # Se establece el índice del item que se va a mostrar cuando se
            # Seleccionen dichas unidades
            self.combof.setCurrentIndex(13)
                
            self.comboi.clear()
            self.comboi.addItem('25 V')
            self.comboi.addItem('10 V')
            self.comboi.addItem('5 V')
            self.comboi.addItem('2 V')
            self.comboi.addItem('1 V')
            self.comboi.addItem('500 mV')
            self.comboi.addItem('200 mV')
            self.comboi.addItem('100 mV')
            self.comboi.addItem('50 mV')
            self.comboi.addItem('20 mV')
            self.comboi.addItem('10 mV')
            self.comboi.addItem('5 mV')
            self.comboi.addItem('2 mV')
            self.comboi.addItem('1 mV')
            self.comboi.addItem('500 uV')
            self.comboi.addItem('200 uV')
            self.comboi.addItem('100 uV')
            self.comboi.addItem('50 uV')
            self.comboi.addItem('20 uV')
            self.comboi.addItem('10 uV')
            self.comboi.addItem('5 uV')
            self.comboi.addItem('2 uV')
            self.comboi.addItem('1 uV')
            self.comboi.addItem('500 nV')
            self.comboi.addItem('200 nV')
            self.comboi.addItem('100 nV')
            self.comboi.addItem('50 nV')
            self.comboi.addItem('20 nV')
            self.comboi.addItem('10 nV')
            self.comboi.addItem('5 nV')
            self.comboi.addItem('2 nV')
            self.comboi.addItem('1 nV')
            self.comboi.setCurrentIndex(11)
        elif unidad == 'Pico [dB]' or unidad == 'RMS [dB]' or \
                    unidad == 'dBV' or unidad == 'Pico [dBm]':
            if unidad == 'Pico [dB]':
                self.opc = 2
            elif unidad == 'RMS [dB]':
                self.opc = 3
            elif unidad == 'dBV':
                self.opc = 4
            elif unidad == 'Pico [dBm]':
                self.opc = 5
            self.combof.clear()
            self.combof.addItem('400 dB')
            self.combof.addItem('390 dB')
            self.combof.addItem('380 dB')
            self.combof.addItem('370 dB')
            self.combof.addItem('360 dB')
            self.combof.addItem('350 dB')
            self.combof.addItem('340 dB')
            self.combof.addItem('330 dB')
            self.combof.addItem('320 dB')
            self.combof.addItem('310 dB')
            self.combof.addItem('300 dB')
            self.combof.addItem('290 dB')
            self.combof.addItem('280 dB')
            self.combof.addItem('270 dB')
            self.combof.addItem('260 dB')
            self.combof.addItem('250 dB')
            self.combof.addItem('240 dB')
            self.combof.addItem('230 dB')
            self.combof.addItem('220 dB')
            self.combof.addItem('210 dB')
            self.combof.addItem('200 dB')
            self.combof.addItem('190 dB')
            self.combof.addItem('180 dB')
            self.combof.addItem('170 dB')
            self.combof.addItem('160 dB')
            self.combof.addItem('150 dB')
            self.combof.addItem('140 dB')
            self.combof.addItem('130 dB')
            self.combof.addItem('120 dB')
            self.combof.addItem('110 dB')
            self.combof.addItem('100 dB')
            self.combof.addItem('90 dB')
            self.combof.addItem('80 dB')
            self.combof.addItem('70 dB')
            self.combof.addItem('60 dB')
            self.combof.addItem('50 dB')
            self.combof.addItem('40 dB')
            self.combof.addItem('30 dB')
            self.combof.addItem('20 dB')
            self.combof.addItem('10 dB')
            self.combof.addItem('0 dB')
            self.combof.addItem('-10 dB')
            self.combof.addItem('-20 dB')
            self.combof.addItem('-30 dB')
            self.combof.addItem('-40 dB')
            self.combof.addItem('-50 dB')
            self.combof.addItem('-60 dB')
            self.combof.addItem('-70 dB')
            self.combof.addItem('-80 dB')
            self.combof.addItem('-90 dB')
            self.combof.addItem('-100 dB')
            self.combof.addItem('-110 dB')
            self.combof.addItem('-120 dB')
            self.combof.addItem('-130 dB')
            self.combof.addItem('-140 dB')
            self.combof.addItem('-150 dB')
            self.combof.addItem('-160 dB')
            self.combof.addItem('-170 dB')
            self.combof.addItem('-180 dB')
            self.combof.addItem('-190 dB')
            self.combof.addItem('-200 dB')
            self.combof.addItem('-210 dB')
            self.combof.addItem('-220 dB')
            self.combof.addItem('-230 dB')
            self.combof.addItem('-240 dB')
            self.combof.addItem('-250 dB')
            self.combof.addItem('-260 dB')
            self.combof.addItem('-270 dB')
            self.combof.addItem('-280 dB')
            self.combof.addItem('-290 dB')
            self.combof.addItem('-300 dB')
            self.combof.addItem('-310 dB')
            self.combof.addItem('-320 dB')
            self.combof.addItem('-330 dB')
            self.combof.addItem('-340 dB')
            self.combof.addItem('-350 dB')
            self.combof.addItem('-360 dB')
            self.combof.addItem('-370 dB')
            self.combof.addItem('-380 dB')
            self.combof.addItem('-390 dB')
            self.combof.addItem('-400 dB')
            self.combof.setCurrentIndex(49)
            
            self.comboi.clear()
            self.comboi.addItem('400 dB')
            self.comboi.addItem('390 dB')
            self.comboi.addItem('380 dB')
            self.comboi.addItem('370 dB')
            self.comboi.addItem('360 dB')
            self.comboi.addItem('350 dB')
            self.comboi.addItem('340 dB')
            self.comboi.addItem('330 dB')
            self.comboi.addItem('320 dB')
            self.comboi.addItem('310 dB')
            self.comboi.addItem('300 dB')
            self.comboi.addItem('290 dB')
            self.comboi.addItem('280 dB')
            self.comboi.addItem('270 dB')
            self.comboi.addItem('260 dB')
            self.comboi.addItem('250 dB')
            self.comboi.addItem('240 dB')
            self.comboi.addItem('230 dB')
            self.comboi.addItem('220 dB')
            self.comboi.addItem('210 dB')
            self.comboi.addItem('200 dB')
            self.comboi.addItem('190 dB')
            self.comboi.addItem('180 dB')
            self.comboi.addItem('170 dB')
            self.comboi.addItem('160 dB')
            self.comboi.addItem('150 dB')
            self.comboi.addItem('140 dB')
            self.comboi.addItem('130 dB')
            self.comboi.addItem('120 dB')
            self.comboi.addItem('110 dB')
            self.comboi.addItem('100 dB')
            self.comboi.addItem('90 dB')
            self.comboi.addItem('80 dB')
            self.comboi.addItem('70 dB')
            self.comboi.addItem('60 dB')
            self.comboi.addItem('50 dB')
            self.comboi.addItem('40 dB')
            self.comboi.addItem('30 dB')
            self.comboi.addItem('20 dB')
            self.comboi.addItem('10 dB')
            self.comboi.addItem('0 dB')
            self.comboi.addItem('-10 dB')
            self.comboi.addItem('-20 dB')
            self.comboi.addItem('-30 dB')
            self.comboi.addItem('-40 dB')
            self.comboi.addItem('-50 dB')
            self.comboi.addItem('-60 dB')
            self.comboi.addItem('-70 dB')
            self.comboi.addItem('-80 dB')
            self.comboi.addItem('-90 dB')
            self.comboi.addItem('-100 dB')
            self.comboi.addItem('-110 dB')
            self.comboi.addItem('-120 dB')
            self.comboi.addItem('-130 dB')
            self.comboi.addItem('-140 dB')
            self.comboi.addItem('-150 dB')
            self.comboi.addItem('-160 dB')
            self.comboi.addItem('-170 dB')
            self.comboi.addItem('-180 dB')
            self.comboi.addItem('-190 dB')
            self.comboi.addItem('-200 dB')
            self.comboi.addItem('-210 dB')
            self.comboi.addItem('-220 dB')
            self.comboi.addItem('-230 dB')
            self.comboi.addItem('-240 dB')
            self.comboi.addItem('-250 dB')
            self.comboi.addItem('-260 dB')
            self.comboi.addItem('-270 dB')
            self.comboi.addItem('-280 dB')
            self.comboi.addItem('-290 dB')
            self.comboi.addItem('-300 dB')
            self.comboi.addItem('-310 dB')
            self.comboi.addItem('-320 dB')
            self.comboi.addItem('-330 dB')
            self.comboi.addItem('-340 dB')
            self.comboi.addItem('-350 dB')
            self.comboi.addItem('-360 dB')
            self.comboi.addItem('-370 dB')
            self.comboi.addItem('-380 dB')
            self.comboi.addItem('-390 dB')
            self.comboi.addItem('-400 dB')
            self.comboi.setCurrentIndex(38)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método que añade el valor máximo de amplitud
    def rangoy_valormax(self,R):
        if R == '25 V':
            # Se le asigna una constante al valor máximo de amplitud
            self.rangeymax = 25
        elif R == '10 V':
            self.rangeymax = 10
        elif R == '5 V':
            self.rangeymax = 5
        elif R == '2 V':
            self.rangeymax = 2
        elif R == '1 V':
            self.rangeymax = 1
        elif R == '500 mV':
            self.rangeymax = 500e-3
        elif R == '200 mV':
            self.rangeymax = 200e-3
        elif R == '100 mV':
            self.rangeymax = 100e-3
        elif R == '50 mV':
            self.rangeymax = 50e-3
        elif R == '20 mV':
            self.rangeymax = 20e-3
        elif R == '10 mV':
            self.rangeymax = 10e-3
        elif R == '5 mV':
            self.rangeymax = 5e-3
        elif R == '2 mV':
            self.rangeymax = 5e-3
        elif R == '1 mV':
            self.rangeymax = 1e-3
        elif R == '500 uV':
            self.rangeymax = 500e-6
        elif R == '200 uV':
            self.rangeymax = 200e-6
        elif R == '100 uV':
            self.rangeymax = 100e-6
        elif R == '50 uV':
            self.rangeymax = 50e-6
        elif R == '20 uV':
            self.rangeymax = 20e-6
        elif R == '10 uV':
            self.rangeymax = 10e-6
        elif R == '5 uV':
            self.rangeymax = 5e-6
        elif R == '2 uV':
            self.rangeymax = 2e-6
        elif R == '1 uV':
            self.rangeymax = 1e-6
        elif R == '500 nV':
            self.rangeymax = 500e-9
        elif R == '200 nV':
            self.rangeymax = 200e-9
        elif R == '100 nV':
            self.rangeymax = 100e-9
        elif R == '50 nV':
            self.rangeymax = 50e-9
        elif R == '20 nV':
            self.rangeymax = 20e-9
        elif R == '10 nV':
            self.rangeymax = 10e-9
        elif R == '5 nV':
            self.rangeymax = 5e-9
        elif R == '2 nV':
            self.rangeymax = 2e-9
        elif R == '1 nV':
            self.rangeymax = 1e-9
        
        if R == '400 dB':
            self.rangeymax = 400
        elif R == '390 dB':
            self.rangeymax = 390
        elif R == '380 dB':
            self.rangeymax = 380
        elif R == '370 dB':
            self.rangeymax = 370
        elif R == '360 dB':
            self.rangeymax = 360
        elif R == '350 dB':
            self.rangeymax = 350
        elif R == '340 dB':
            self.rangeymax = 340
        elif R == '330 dB':
            self.rangeymax = 330
        elif R == '320 dB':
            self.rangeymax = 320
        elif R == '310 dB':
            self.rangeymax = 310
        elif R == '300 dB':
            self.rangeymax = 320
        elif R == '290 dB':
            self.rangeymax = 290
        elif R == '280 dB':
            self.rangeymax = 280
        elif R == '270 dB':
            self.rangeymax = 270
        elif R == '260 dB':
            self.rangeymax = 260
        elif R == '250 dB':
            self.rangeymax = 250
        elif R == '240 dB':
            self.rangeymax = 240
        elif R == '230 dB':
            self.rangeymax = 230
        elif R == '220 dB':
            self.rangeymax = 220
        elif R == '210 dB':
            self.rangeymax = 210
        elif R == '200 dB':
            self.rangeymax = 200
        elif R == '190 dB':
            self.rangeymax = 190
        elif R == '180 dB':
            self.rangeymax = 180
        elif R == '170 dB':
            self.rangeymax = 170
        elif R == '160 dB':
            self.rangeymax = 160
        elif R == '150 dB':
            self.rangeymax = 150
        elif R == '140 dB':
            self.rangeymax = 140
        elif R == '130 dB':
            self.rangeymax = 130
        elif R == '120 dB':
            self.rangeymax = 120
        elif R == '110 dB':
            self.rangeymax = 110
        elif R == '100 dB':
            self.rangeymax = 100
        elif R == '90 dB':
            self.rangeymax = 90
        elif R == '80 dB':
            self.rangeymax = 80
        elif R == '70 dB':
            self.rangeymax = 70
        elif R == '60 dB':
            self.rangeymax = 60
        elif R == '50 dB':
            self.rangeymax = 50
        elif R == '40 dB':
            self.rangeymax = 40
        elif R == '30 dB':
            self.rangeymax = 30
        elif R == '20 dB':
            self.rangeymax = 20
        elif R == '10 dB':
            self.rangeymax = 10
        elif R == '0 dB':
            self.rangeymax = 0
        elif R == '-10 dB':
            self.rangeymax = -10
        elif R == '-20 dB':
            self.rangeymax = -20
        elif R == '-30 dB':
            self.rangeymax = -30
        elif R == '-40 dB':
            self.rangeymax = -40
        elif R == '-50 dB':
            self.rangeymax = -50
        elif R == '-60 dB':
            self.rangeymax = -60
        elif R == '-70 dB':
            self.rangeymax = -70
        elif R == '-80 dB':
            self.rangeymax = -80
        elif R == '-90 dB':
            self.rangeymax = -90
        elif R == '-100 dB':
            self.rangeymax = -100
        elif R == '-110 dB':
            self.rangeymax = -110
        elif R == '-120 dB':
            self.rangeymax = -120
        elif R == '-130 dB':
            self.rangeymax = -130
        elif R == '-140 dB':
            self.rangeymax = -140
        elif R == '-150 dB':
            self.rangeymax = -150
        elif R == '-160 dB':
            self.rangeymax = -160
        elif R == '-170 dB':
            self.rangeymax = -170
        elif R == '-180 dB':
            self.rangeymax = -180
        elif R == '-190 dB':
            self.rangeymax = -190
        elif R == '-200 dB':
            self.rangeymax = -200
        elif R == '-210 dB':
            self.rangeymax = -210
        elif R == '-220 dB':
            self.rangeymax = -220
        elif R == '-230 dB':
            self.rangeymax = -230
        elif R == '-240 dB':
            self.rangeymax = -240
        elif R == '-250 dB':
            self.rangeymax = -250
        elif R == '-260 dB':
            self.rangeymax = -260
        elif R == '-270 dB':
            self.rangeymax = -270
        elif R == '-280 dB':
            self.rangeymax = -280
        elif R == '-290 dB':
            self.rangeymax = -290
        elif R == '-300 dB':
            self.rangeymax = -300
        elif R == '-310 dB':
            self.rangeymax = -310
        elif R == '-320 dB':
            self.rangeymax = -320
        elif R == '-330 dB':
            self.rangeymax = -330
        elif R == '-340 dB':
            self.rangeymax = -340
        elif R == '-350 dB':
            self.rangeymax = -350
        elif R == '-360 dB':
            self.rangeymax = -360
        elif R == '-370 dB':
            self.rangeymax = -370
        elif R == '-380 dB':
            self.rangeymax = -380
        elif R == '-390 dB':
            self.rangeymax = -390
        elif R == '-400 dB':
            self.rangeymax = -400
        # Se define el rango para el eje y
        self.graficaBox1_spc.setYRange(self.rangeymin, self.rangeymax,
                                       padding=None, update=True)
        self.graficaBox2_spc.setYRange(self.rangeymin, self.rangeymax,
                                       padding=None, update=True)
    #-----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Método para dar el valor mínimo de voltaje al espectro
    def rangoy_valormin(self,R):
        # Se comprueba que el valor elegido, guardado en la variable R, sea el
        # Que coincide con las unidades seleccionadas para la amplitud
        if R == '25 V':
            # Se le asigna una constante al valor mínimo
            self.rangeymin = 25
        elif R == '10 V':
            self.rangeymin = 10
        elif R == '5 V':
            self.rangeymin = 5
        elif R == '2 V':
            self.rangeymin = 2
        elif R == '1 V':
            self.rangeymin = 1
        elif R == '500 mV':
            self.rangeymin = 500e-3
        elif R == '200 mV':
            self.rangeymin = 200e-3
        elif R == '100 mV':
            self.rangeymin = 100e-3
        elif R == '50 mV':
            self.rangeymin = 50e-3
        elif R == '20 mV':
            self.rangeymin = 20e-3
        elif R == '10 mV':
            self.rangeymin = 10e-3
        elif R == '5 mV':
            self.rangeymin = 5e-3
        elif R == '2 mV':
            self.rangeymin = 5e-3
        elif R == '1 mV':
            self.rangeymin = 1e-3
        elif R == '500 uV':
            self.rangeymin = 500e-6
        elif R == '200 uV':
            self.rangeymin = 200e-6
        elif R == '100 uV':
            self.rangeymin = 100e-6
        elif R == '50 uV':
            self.rangeymin = 50e-6
        elif R == '20 uV':
            self.rangeymin = 20e-6
        elif R == '10 uV':
            self.rangeymin = 10e-6
        elif R == '5 uV':
            self.rangeymin = 5e-6
        elif R == '2 uV':
            self.rangeymin = 2e-6
        elif R == '1 uV':
            self.rangeymin = 1e-6
        elif R == '500 nV':
            self.rangeymin = 500e-9
        elif R == '200 nV':
            self.rangeymin = 200e-9
        elif R == '100 nV':
            self.rangeymin = 100e-9
        elif R == '50 nV':
            self.rangeymin = 50e-9
        elif R == '20 nV':
            self.rangeymin = 20e-9
        elif R == '10 nV':
            self.rangeymin = 10e-9
        elif R == '5 nV':
            self.rangeymin = 5e-9
        elif R == '2 nV':
            self.rangeymin = 2e-9
        elif R == '1 nV':
            self.rangeymin = 1e-9
        
        if R == '400 dB':
            self.rangeymin = 400
        elif R == '390 dB':
            self.rangeymin = 390
        elif R == '380 dB':
            self.rangeymin = 380
        elif R == '370 dB':
            self.rangeymin = 370
        elif R == '360 dB':
            self.rangeymin = 360
        elif R == '350 dB':
            self.rangeymin = 350
        elif R == '340 dB':
            self.rangeymin = 340
        elif R == '330 dB':
            self.rangeymin = 330
        elif R == '320 dB':
            self.rangeymin = 320
        elif R == '310 dB':
            self.rangeymin = 310
        elif R == '300 dB':
            self.rangeymin = 320
        elif R == '290 dB':
            self.rangeymin = 290
        elif R == '280 dB':
            self.rangeymin = 280
        elif R == '270 dB':
            self.rangeymin = 270
        elif R == '260 dB':
            self.rangeymin = 260
        elif R == '250 dB':
            self.rangeymin = 250
        elif R == '240 dB':
            self.rangeymin = 240
        elif R == '230 dB':
            self.rangeymin = 230
        elif R == '220 dB':
            self.rangeymin = 220
        elif R == '210 dB':
            self.rangeymin = 210
        elif R == '200 dB':
            self.rangeymin = 200
        elif R == '190 dB':
            self.rangeymin = 190
        elif R == '180 dB':
            self.rangeymin = 180
        elif R == '170 dB':
            self.rangeymin = 170
        elif R == '160 dB':
            self.rangeymin = 160
        elif R == '150 dB':
            self.rangeymin = 150
        elif R == '140 dB':
            self.rangeymin = 140
        elif R == '130 dB':
            self.rangeymin = 130
        elif R == '120 dB':
            self.rangeymin = 120
        elif R == '110 dB':
            self.rangeymin = 110
        elif R == '100 dB':
            self.rangeymin = 100
        elif R == '90 dB':
            self.rangeymin = 90
        elif R == '80 dB':
            self.rangeymin = 80
        elif R == '70 dB':
            self.rangeymin = 70
        elif R == '60 dB':
            self.rangeymin = 60
        elif R == '50 dB':
            self.rangeymin = 50
        elif R == '40 dB':
            self.rangeymin = 40
        elif R == '30 dB':
            self.rangeymin = 30
        elif R == '20 dB':
            self.rangeymin = 20
        elif R == '10 dB':
            self.rangeymin = 10
        elif R == '0 dB':
            self.rangeymin = 0
        elif R == '-10 dB':
            self.rangeymin = -10
        elif R == '-20 dB':
            self.rangeymin = -20
        elif R == '-30 dB':
            self.rangeymin = -30
        elif R == '-40 dB':
            self.rangeymin = -40
        elif R == '-50 dB':
            self.rangeymin = -50
        elif R == '-60 dB':
            self.rangeymin = -60
        elif R == '-70 dB':
            self.rangeymin = -70
        elif R == '-80 dB':
            self.rangeymin = -80
        elif R == '-90 dB':
            self.rangeymin = -90
        elif R == '-100 dB':
            self.rangeymin = -100
        elif R == '-110 dB':
            self.rangeymin = -110
        elif R == '-120 dB':
            self.rangeymin = -120
        elif R == '-130 dB':
            self.rangeymin = -130
        elif R == '-140 dB':
            self.rangeymin = -140
        elif R == '-150 dB':
            self.rangeymin = -150
        elif R == '-160 dB':
            self.rangeymin = -160
        elif R == '-170 dB':
            self.rangeymin = -170
        elif R == '-180 dB':
            self.rangeymin = -180
        elif R == '-190 dB':
            self.rangeymin = -190
        elif R == '-200 dB':
            self.rangeymin = -200
        elif R == '-210 dB':
            self.rangeymin = -210
        elif R == '-220 dB':
            self.rangeymin = -220
        elif R == '-230 dB':
            self.rangeymin = -230
        elif R == '-240 dB':
            self.rangeymin = -240
        elif R == '-250 dB':
            self.rangeymin = -250
        elif R == '-260 dB':
            self.rangeymin = -260
        elif R == '-270 dB':
            self.rangeymin = -270
        elif R == '-280 dB':
            self.rangeymin = -280
        elif R == '-290 dB':
            self.rangeymin = -290
        elif R == '-300 dB':
            self.rangeymin = -300
        elif R == '-310 dB':
            self.rangeymin = -310
        elif R == '-320 dB':
            self.rangeymin = -320
        elif R == '-330 dB':
            self.rangeymin = -330
        elif R == '-340 dB':
            self.rangeymin = -340
        elif R == '-350 dB':
            self.rangeymin = -350
        elif R == '-360 dB':
            self.rangeymin = -360
        elif R == '-370 dB':
            self.rangeymin = -370
        elif R == '-380 dB':
            self.rangeymin = -380
        elif R == '-390 dB':
            self.rangeymin = -390
        elif R == '-400 dB':
            self.rangeymin = -400
        # Se define el rango para el eje y
        self.graficaBox1_spc.setYRange(self.rangeymin, self.rangeymax,
                                       padding=None, update=True)
        self.graficaBox2_spc.setYRange(self.rangeymin, self.rangeymax,
                                       padding=None, update=True)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Función para mandar un aviso al usurio
    def aviso_canal1sp(self):
        # Se comprueba que está seleccionado el canal 1
        if self.checkBoxch1_spc.isChecked():
            # Se manda texto de aviso
            self.avisoCh1.setText('Canal 1\nActivo')
            # Se muestra la cuadrícula del eje Y del canal 1
            self.p1_spc.getAxis('left').setGrid(200)
        # Si no se ha seleccionado el canal 1, se limpia la gráfica
        elif self.checkBoxch1_spc.isChecked() is False:
            self.curva1.clear()
            self.avisoCh1.setText('')
            # Cuando no se selecciona el canal 1, se quita la cuadrícula also
            self.p1_spc.getAxis('left').setGrid(False)
    #----------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Método que manda un aviso relacionado con el canal 2
    def aviso_canal2sp(self):
        if self.checkBoxch2_spc.isChecked():
            self.avisoCh2.setText('Canal 2\nActivo')
            # Se muestra la cuadrícula del eje Y del canal 2
            self.p1_spc.getAxis('right').setGrid(100)
        elif self.checkBoxch2_spc.isChecked() is False:
            self.curva2_spc.clear()
            self.avisoCh2.setText('')
            # Cu↨ando no se selecciona el canal 2, se quita la cuadrícula also
            self.p1_spc.getAxis('right').setGrid(False)
    #---------------------------------------------------------------------
    
    #----------------------------------------------------------------------
    # Metodo para actualizar el valor de la posición CH1
    def actualiza_vpos1sp(self):
        # Se toma el valor del spin, para la amplitud
        self.posicionV1 = self.spin1_spc.value()
        # Se desplaza la gráfica del canal 1 por un factor de 1 mV
        self.graficaBox1_spc.translateBy(y=self.posicionV1*2)
        # Vuelve a cero el valor del spin
        self.spin1_spc.setValue(0)
        #----------------------------------------------------------------------
        
    #-----------------------------------------------------------------------
    #Metodo para actualizar la posición del CH2
    def actualiza_vpos2sp(self):
        self.posicionV2 = self.spin2_spc.value()
        # Se desplaza la gráfica del canal 2 por un factor de 1 mV
        self.graficaBox2_spc.translateBy(y=self.posicionV2*2)
        self.spin2_spc.setValue(0)
    #----------------------------------------------------------------------
        
    #----------------------------------------------------------------------
    # Metdo para posición del espectro, en la frecuencia
    def actualiza_fpos(self):
        # Se toma el valor del spin, para la frecuencia
        self.posicion = self.spin5_spc.value()
        # Se traslada el espectro, de ambos canales, en frecuencia por x100
        self.graficaBox1_spc.translateBy(x=self.posicion * 100)
        # Se fija el valor en cero para poder hacer otro movimiento
        self.spin5_spc.setValue(0)
    #----------------------------------------------------------------------
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = VentanaPrincipal()
    GUI.show()
    # Esta instrucción hace que el código también funcione en Ubuntu
    sys.exit(app.exec())  