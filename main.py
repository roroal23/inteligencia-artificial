import sys

from PySide6 import QtWidgets, QtCore, QtGui
from creacion_grafo_v2 import LectorFichero

class getCoordenadas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ESTACIONES = {}
        with open(file="data/163CoordInterfaz.txt", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    self.ESTACIONES[parts[0]] = (float(parts[1]), float(parts[2]))

        #self.ESTACIONES = {
         #   "Observatorio": (55.200000000000045, 332.8),
          #  "Tacubaya": (73.0, 312.8),
           # "Constituyentes": (72.20000000000005, 285.6),
            #"Auditorio": (72.80000000000001, 254.4000000000001),
        #}

    def getC(self, nombre: str) -> tuple[float, float]:
        return self.ESTACIONES[nombre]


class MapaWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QtGui.QPixmap("data/Mexico_City_metro.png")
        if self.pixmap.isNull():
            self.pixmap = QtGui.QPixmap(800, 600)
            self.pixmap.fill(QtCore.Qt.white)
        else:
            self.pixmap = self.pixmap.scaled(
                800, 600,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
        #############################self.rutas = [(QtCore.Qt.red, [ESTACIONES[nombre] for nombre in ESTACIONES.keys()])]
        self.rutas = []
        self.setFixedSize(self.pixmap.size())

    def mousePressEvent(self, event):
        # Obtener coordenadas del clic dentro del widget
        x = event.position().x()
        y = event.position().y()
        print(f"Clic en ({x},{y})")

    def add_ruta(self, nombres_estaciones, color=QtCore.Qt.red):
        gc = getCoordenadas()
        coords = []
        for nombre in nombres_estaciones:
            if nombre in gc.ESTACIONES:  # tanto normales como aux deben estar en el fichero
                coords.append((nombre, gc.getC(nombre)))
        self.rutas.append((color, coords))
        self.update()

    def limpiar_rutas(self):
        self.rutas.clear()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        for color, estaciones in self.rutas:
            painter.setPen(QtGui.QPen(color, 2))
            painter.setBrush(QtGui.QBrush(color))
            # dibujar círculos solo si no empieza por "aux"
            for nombre, (x, y) in estaciones:
                if not nombre.lower().startswith("aux"):
                    painter.drawEllipse(QtCore.QPoint(x, y), 5, 5)
            # dibujar líneas entre todas las estaciones (incluyendo aux)
            painter.setPen(QtGui.QPen(color, 5))
            for i in range(len(estaciones) - 1):
                _, (x1, y1) = estaciones[i]
                _, (x2, y2) = estaciones[i + 1]
                painter.drawLine(x1, y1, x2, y2)


class CajasTexto(QtWidgets.QWidget):
    def __init__(self, mapa: MapaWidget):
        super().__init__()

        self.mapa = mapa
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

        self.boton1.clicked.connect(self.buscar)
        self.boton2.clicked.connect(self.limpiar)

        self.vbox.addWidget(self.texto)
        self.vbox.addWidget(self.texto2)
        self.hbox.addWidget(self.boton1)
        self.hbox.addWidget(self.boton2)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

    def buscar(self):
        origen = self.texto.text()
        destino = self.texto2.text()

        ##Posteriormente hay que calcular la ruta con la función-> p.e.: ruta = obtenerRuta(origen, destino)

        #ruta = [origen, destino]

        ruta = ["Observatorio", "Tacubaya", "Juanacatlán", "Chapultepec", "Sevilla", "Insurgentes","aux1", "Cuauhtémoc", "Balderas", "Salto del Agua",
                "Isabel la Católica", "Pino Suárez", "aux2", "Merced", "Candelaria", "San Lázaro", "Moctezuma", "Balbuena", "aux3", "Boulevard Puerto Aéreo",
                "aux4", "Gómez Farías", "Zaragoza", "aux5", "Pantitlán"]

        self.mapa.add_ruta(ruta, color=QtCore.Qt.red)


    @QtCore.Slot()
    def limpiar(self):
        self.texto.clear()
        self.texto2.clear()
        self.mapa.limpiar_rutas()

class MainScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.mapa = MapaWidget()
        self.textos = CajasTexto(self.mapa)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.insertWidget(0, self.mapa)
        self.hbox.addWidget(self.textos)


        self.setLayout(self.hbox)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainScreen()
    widget.resize(1024, 720)
    widget.show()

    sys.exit(app.exec_())