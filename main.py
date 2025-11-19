
import sys

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import QSizePolicy

from creacion_grafo_v2 import LectorFichero



class PintarMapa(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()


class CajasTexto(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.estaciones = LectorFichero.obtener_estaciones_163()
        self.textos = []
        for estacion in self.estaciones:
            self.textos.append(estacion)

        self.completador = QtWidgets.QCompleter(self.textos)
        self.completador.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox.setSpacing(3)
        self.vbox.setContentsMargins(0,50,0,0)
        self.vbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.boton1 = QtWidgets.QPushButton("Buscar")
        self.boton2 = QtWidgets.QPushButton("Limpiar")
        self.texto = QtWidgets.QLineEdit()
        self.texto2 = QtWidgets.QLineEdit()

        self.texto.setCompleter(self.completador)
        self.texto2.setCompleter(self.completador)

        self.boton2.clicked.connect(self.limpiar)

        self.vbox.addWidget(self.texto)
        self.vbox.addWidget(self.texto2)
        self.hbox.addWidget(self.boton1)
        self.hbox.addWidget(self.boton2)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

    @QtCore.Slot()
    def limpiar(self):
        self.texto.clear()
        self.texto2.clear()

class MainScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.mapa = QSvgWidget("data/Mexico_City_metro.svg")
        self.mapa.setFixedSize(530,600)
        self.mapa.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.textos = CajasTexto()

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.mapa)
        self.hbox.addWidget(self.textos)


        self.setLayout(self.hbox)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainScreen()
    widget.resize(1024, 720)
    widget.show()

    sys.exit(app.exec_())