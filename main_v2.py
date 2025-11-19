
import sys

import networkx as nx
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import QSizePolicy

from creacion_grafo_v2 import LectorFichero, TablaEstaciones, GrafoMetro
import math

class GetCoordenadas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ESTACIONES = {}
        with open(file="data/163CoordInterfaz.txt", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    self.ESTACIONES[parts[0]] = (float(parts[1]), float(parts[2]))

    def getc(self, nombre: str) -> tuple[float, float]:
        return self.ESTACIONES[nombre]

    def distancia_menor(self, estacion1:str, estacion2:str) -> float:
        """ Devulve la distancia en línea recta entre dos estaciones en METROS
            usando la fórmula de Haversine sobre una Tierra esférica"""
        lat1_deg, lon1_deg = self.getc(estacion1)
        lat2_deg, lon2_deg = self.getc(estacion2)

        # Pasar a radianes
        lat1 = math.radians(lat1_deg)
        lon1 = math.radians(lon1_deg)
        lat2 = math.radians(lat2_deg)
        lon2 = math.radians(lon2_deg)

        dlat = lat2-lat1
        dlon = lon2-lon1

        # Haversine

        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        R = 6371000 # radio de la Tierra en metros
        distancia_metros = R*c
        return distancia_metros

class CajasTexto(QtWidgets.QWidget):
    def __init__(self, mapa):
        super().__init__()

        self.mapa = mapa
        self.estaciones = LectorFichero.obtener_estaciones_163()
        self.textos = []
        for estacion in self.estaciones:
            self.textos.append(estacion)

        # Sección autocompletardor
        self.completador = QtWidgets.QCompleter(self.textos)
        self.completador.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        # CONSTRUCCIÓN DEL GRAFO DEL METRO
        ficheros = LectorFichero()  # ficheros para leer estaciones y conexiones
        estaciones_grafo = ficheros.obtener_estaciones()  # lista de tuplas de estaciones. Ej: ("Observatorio","1")
        conexiones = ficheros.obtener_conexiones()  # lista de tuplas de conexiones
        self.tabla_estaciones = TablaEstaciones(estaciones_grafo)  # diccionarios para trabajar con estaciones
        self.grafo_metro = GrafoMetro(self.tabla_estaciones, estaciones_grafo, conexiones)
        # -----

        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox.setSpacing(3)
        self.vbox.setContentsMargins(0,50,0,0)
        self.vbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # cajas de texto y botones
        self.boton1 = QtWidgets.QPushButton("Buscar")
        self.boton2 = QtWidgets.QPushButton("Limpiar")
        self.texto = QtWidgets.QLineEdit()
        self.texto2 = QtWidgets.QLineEdit()
        self.origenTexto = QtWidgets.QLabel("Origen: ")
        self.destinoTexto = QtWidgets.QLabel("Destino: ")

        # asociamos el autocompletador
        self.texto.setCompleter(self.completador)
        self.texto2.setCompleter(self.completador)

        self.texto.setPlaceholderText("Introduce el origen")
        self.texto2.setPlaceholderText("Introduce el destino")

        # QLabel para mensajes de estado
        self.label_estado = QtWidgets.QLabel("")
        self.label_estado.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # conectamos los botones
        self.boton1.clicked.connect(self.buscar)
        self.boton2.clicked.connect(self.limpiar)

        # añade widgets al layout
        self.vbox.addWidget(self.origenTexto)
        self.vbox.addWidget(self.texto)
        self.vbox.addWidget(self.destinoTexto)
        self.vbox.addWidget(self.texto2)
        self.hbox.addWidget(self.boton1)
        self.hbox.addWidget(self.boton2)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

    @staticmethod
    def heuristica_dummy(origen, destino):
        return 0

    @QtCore.Slot()
    def limpiar(self):
        self.texto.clear()
        self.texto2.clear()

        # Resetear cajas y label
        self.texto.setStyleSheet("")
        self.texto2.setStyleSheet("")
        self.texto.setPlaceholderText("Origen")
        self.texto2.setPlaceholderText("Destino")

        # limpiar mensaje de estado
        self.label_estado.clear()
        self.label_estado.setStyleSheet("")

        # limpiamos el mapa
        self.mapa.limpiar_rutas()


    def buscar(self):
        origen = self.texto.text().strip() # cojo el texto de la caja (origen)
        destino = self.texto2.text().strip()

        # Reseteamos cajas y label
        self.texto.setStyleSheet("")
        self.texto2.setStyleSheet("")
        self.texto.setPlaceholderText("Origen")
        self.texto2.setPlaceholderText("Destino")
        self.label_estado.clear()
        self.label_estado.setStyleSheet("")
        #Limpiamos el mapa
        self.mapa.limpiar_rutas()

        error = False
        mensajes_error = []

        # 1. Comprobamos que no están vacíos
        if not origen:
            self.texto.setStyleSheet("border: 2px solid red;")
            mensajes_error.append("Es necesario rellenar el campo origen.")
            error = True

        if not destino:
            self.texto2.setStyleSheet("border: 2px solid red;")
            mensajes_error.append("Es necesario rellenar el campo destino.")
            error = True

        # Comprobar que existen en la lista de estaciones válidas
        if origen and origen not in self.estaciones:
            self.texto.setStyleSheet("border: 2px solid red;")
            mensajes_error.append("Estación de origen no válida.")
            error = True

        if destino and destino not in self.estaciones:
            self.texto2.setStyleSheet("border: 2px solid red;")
            mensajes_error.append("Estación de destino no válida.")
            error = True

        if not error and origen == destino:
            self.texto.setStyleSheet("border: 2px solid red;")
            self.texto2.setStyleSheet("border: 2px solid red;")
            mensajes_error.append("Origen y destino no pueden ser iguales.")
            self.label_estado.setStyleSheet("color: red;")
            error = True

        if error:
            self.label_estado.setText("\n".join(mensajes_error))
            self.label_estado.setStyleSheet("color: red;")
            return

        # ====== FUNCIÓN A* ========

        # Obtenemos líneas
        lineas_origen = self.tabla_estaciones.obtener_lineas(origen)
        lineas_destino = self.tabla_estaciones.obtener_lineas(destino)

        mejor_camino = None
        mejor_coste = None

        for linea_o in lineas_origen:
            for linea_d in lineas_destino:
                id_origen = self.tabla_estaciones.obtener_id((origen,linea_o))
                id_destino = self.tabla_estaciones.obtener_id((destino,linea_d))
                camino_ids = nx.astar_path(
                    self.grafo_metro.grafo,
                    id_origen,
                    id_destino,
                    heuristic =self.heuristica_dummy,
                    weight = "weight"
                )
                coste_total = nx.astar_path_length(
                    self.grafo_metro.grafo,
                    id_origen,
                    id_destino,
                    heuristic =self.heuristica_dummy,
                    weight = "weight"
                )
                if mejor_coste is None or coste_total < mejor_coste:
                    mejor_coste = coste_total
                    mejor_camino = camino_ids


        # Convertimos IDs a nombres (para mostrarlo)
        estaciones_camino_optimo = []
        for nodo_id in mejor_camino:
            nombre_est, linea_est = self.tabla_estaciones.obtener_estacion(nodo_id)
            estaciones_camino_optimo.append((nombre_est, linea_est))

        # Código necesario para mostrar el trayecto con las estaciones y los transbordos necesarios
        lineas_salida=[]
        prev_nombre = None
        prev_linea = None

        for nombre, linea in estaciones_camino_optimo:
            if prev_nombre is None:
                lineas_salida.append(nombre) # Metes la primera estación
            else: #si no esla primera estación, compruebas si es transbordo. Si no lo es, es la siguiente parada
                if nombre == prev_nombre and linea != prev_linea:
                    #transbordo
                    lineas_salida.append(f"Transbordo de la línea {prev_linea} a la línea {linea}")
                elif nombre != prev_nombre:
                    # Siguiente estacion
                    lineas_salida.append(nombre)
            prev_nombre,prev_linea = nombre,linea # para la siguiente iteración

        texto_camino = "\n".join(lineas_salida)

        # Calculamos el Tiempo Estimado
        vel_m_h = 25000 # promedio del tren es de 25km/h
        tiempo_min_totales = (mejor_coste/vel_m_h) * 60
        minutos_totales = int(round(tiempo_min_totales))

        if minutos_totales < 60:
            texto_tiempo = f"{minutos_totales} minutos."
        else:
            horas = minutos_totales // 60
            minutos = minutos_totales % 60
            if minutos == 0:
                texto_tiempo = f"{horas} horas."
            else:
                texto_tiempo = f"{horas} horas {minutos} minutos."

        num_estaciones = len(mejor_camino) - 1
        # Mostrar resultado
        self.label_estado.setText(f"Camino más rápido entre {origen} y {destino}:\n\n"
                                  f"{texto_camino}\n\n"
                                  f"El número total de estaciones son: {num_estaciones}\n"
                                  f"Tiempo estimado de tu trayecto: {texto_tiempo}\n"
        )
        self.label_estado.setStyleSheet("color: green;")

        # Dibujar en el mapa
        nombres_camino = [nombre for (nombre,linea) in estaciones_camino_optimo]
        self.mapa.add_ruta(nombres_camino, color=QtCore.Qt.red)

class RutasWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label_estado=None):
        super().__init__(parent)
        self.rutas = []
        self.label_estado = label_estado  # referencia al label de MainScreen
        # transparente (pero SIN WA_TransparentForMouseEvents para poder recibir clics)
        self.setStyleSheet("background: transparent;")

    def add_ruta(self, nombres_estaciones, color=QtCore.Qt.red):
        """Recibe una lista de nombres de estaciones y construye (nombre, (x,y))."""
        gc = GetCoordenadas()
        coords = [(nombre, gc.getc(nombre)) for nombre in nombres_estaciones if nombre in gc.ESTACIONES]
        self.rutas.append((color, coords))
        self.update()

    def limpiar_rutas(self):
        self.rutas.clear()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for color, estaciones in self.rutas:
            # líneas entre estaciones consecutivas
            painter.setPen(QtGui.QPen(color, 2))
            for i in range(len(estaciones) - 1):
                _, (x1, y1) = estaciones[i]
                _, (x2, y2) = estaciones[i + 1]
                painter.drawLine(x1, y1, x2, y2)

            # círculos en cada estación (excepto nombres 'aux')
            painter.setPen(QtGui.QPen(color, 1))#borde
            painter.setBrush(QtGui.QBrush(color))#relleno
            for nombre, (x, y) in estaciones:
                if not nombre.lower().startswith("aux"):
                    painter.drawEllipse(QtCore.QPointF(x, y), 5, 5)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        # Coordenadas del clic relativas al overlay (coinciden con el mapa)
        x = event.position().x()
        y = event.position().y()
        print(f"Clic en (,{x:.1f},{y:.1f})")
        if self.label_estado is not None:
            self.label_estado.setText(f"Clic en coordenadas: ({x:.1f}, {y:.1f})")
        # No llamar a super().mousePressEvent para evitar propagación si no quieres


class MainScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
        self.CajaInicio = QtWidgets.QVBoxLayout()
        self.CajaInicio.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # Título
        self.Titulo = QtWidgets.QLabel(
            "<html><img src='data/Logo.svg' width='30' height='30'></html> Buscador Metro CDMX"
        )
        self.Titulo.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Bold))
        self.CajaInicio.addWidget(self.Titulo)

        # Mapa SVG (widget hijo)
        self.mapa = QSvgWidget("data/Mexico_City_metro.svg")
        self.mapa.setFixedSize(530, 600)
        self.mapa.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Mensajes de estado
        self.label_estado = QtWidgets.QLabel("")
        self.label_estado.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Overlay transparente encima del mapa
        self.overlay = RutasWidget(self.mapa, label_estado=self.label_estado)
        self.overlay.setGeometry(self.mapa.rect())  # mismo tamaño que el mapa
        self.overlay.raise_()  # subir en el eje Z por encima del mapa

        # Cajas de texto (pasamos overlay porque es quien tiene add_ruta/limpiar_rutas)
        self.textos = CajasTexto(self.overlay)

        # Layout horizontal: mapa + panel de textos
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.mapa)
        self.hbox.addWidget(self.textos)

        # Añadir todo al layout principal
        self.CajaInicio.addLayout(self.hbox)
        self.CajaInicio.addWidget(self.label_estado)

        self.setLayout(self.CajaInicio)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("Buscador Metro CDMX")
    app.setWindowIcon(QtGui.QIcon("data/logo.svg"))
    widget = MainScreen()
    widget.resize(1024, 720)
    widget.setWindowFlag(QtCore.Qt.WindowType.MSWindowsFixedSizeDialogHint)
    widget.show()
    sys.exit(app.exec_())
