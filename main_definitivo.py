
import sys
from sys import flags

import PySide6
import networkx as nx
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPalette, QPixmap, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import QSizePolicy

from creacion_grafo_v2 import LectorFichero, TablaEstaciones, GrafoMetro
import math
import json


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
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setBackgroundRole(QPalette.Dark)
        self.scroll.setWidgetResizable(False)
        self.lineaRuta = LineaRutaDibujo(self.scroll)
        self.resumenruta = QtWidgets.QLabel(f"Tiempo de viaje: --\nNumero de Paradas: --")
        self.titulodatos = QtWidgets.QLabel("Datos:")
        self.titulodatos.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        self.tituloruta = QtWidgets.QLabel("Ruta:")
        self.tituloruta.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        self.resumenruta.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))


        for estacion in self.estaciones:
            self.textos.append(estacion)

        # Sección autocompletardor
        self.completador = QtWidgets.QCompleter(self.textos)
        self.completador.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completador.setFilterMode(Qt.MatchFlag.MatchContains)
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
        self.vbox.addWidget(self.titulodatos)
        self.vbox.addWidget(self.origenTexto)
        self.vbox.addWidget(self.texto)
        self.vbox.addWidget(self.destinoTexto)
        self.vbox.addWidget(self.texto2)
        self.hbox.addWidget(self.boton1)
        self.hbox.addWidget(self.boton2)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.label_estado)
        self.vbox.addWidget(self.tituloruta)
        self.vbox.addWidget(self.scroll)
        self.vbox.addWidget(self.resumenruta)
        self.lineaRuta.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scroll.setWidget(self.lineaRuta)
        self.scroll.setAlignment(QtCore.Qt.AlignHCenter)
        self.setLayout(self.vbox)
        self.minimo_trasbordos = {
            "1": {"1": 0, "2": 1, "3": 1, "4": 1, "5": 1, "6": 2, "7": 1, "8": 1, "9": 1, "A": 1, "B": 1, "12": 2},
            "2": {"1": 1, "2": 0, "3": 1, "4": 2, "5": 2, "6": 2, "7": 1, "8": 1, "9": 1, "A": 2, "B": 2, "12": 1},
            "3": {"1": 1, "2": 1, "3": 0, "4": 2, "5": 1, "6": 1, "7": 2, "8": 2, "9": 1, "A": 2, "B": 1, "12": 1},
            "4": {"1": 1, "2": 2, "3": 2, "4": 0, "5": 1, "6": 1, "7": 2, "8": 1, "9": 1, "A": 2, "B": 1, "12": 2},
            "5": {"1": 1, "2": 2, "3": 1, "4": 1, "5": 0, "6": 1, "7": 2, "8": 2, "9": 1, "A": 1, "B": 1, "12": 2},
            "6": {"1": 2, "2": 2, "3": 1, "4": 1, "5": 1, "6": 0, "7": 1, "8": 2, "9": 2, "A": 2, "B": 2, "12": 2},
            "7": {"1": 1, "2": 1, "3": 2, "4": 2, "5": 2, "6": 1, "7": 0, "8": 2, "9": 1, "A": 2, "B": 2, "12": 1},
            "8": {"1": 1, "2": 1, "3": 2, "4": 1, "5": 2, "6": 2, "7": 2, "8": 0, "9": 1, "A": 2, "B": 1, "12": 1},
            "9": {"1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 2, "7": 1, "8": 1, "9": 0, "A": 1, "B": 2, "12": 2},
            "A": {"1": 1, "2": 2, "3": 2, "4": 2, "5": 1, "6": 2, "7": 2, "8": 2, "9": 1, "A": 0, "B": 2, "12": 3},
            "B": {"1": 1, "2": 2, "3": 1, "4": 1, "5": 1, "6": 2, "7": 2, "8": 1, "9": 2, "A": 2, "B": 0, "12": 2},
            "12": {"1": 2, "2": 1, "3": 1, "4": 2, "5": 2, "6": 2, "7": 1, "8": 1, "9": 2, "A": 3, "B": 2, "12": 0}
        }
        with open("./data/estaciones_metro2.json", "r", encoding="utf-8") as f:
            self.json_coordenadas = json.load(f)

    def calcularDistancia(self, coordsOrigen, coordsDestino) -> int:
        latOrigen = math.radians(float(coordsOrigen["lat"]))
        longOrigen = math.radians(float(coordsOrigen["lng"]))
        latDestino = math.radians(float(coordsDestino["lat"]))
        longDestino = math.radians(float(coordsOrigen["lng"]))
        radio_tierra = 6371000
        coordenadas_origen = (radio_tierra * math.cos(latOrigen) * math.cos(longOrigen),
                              radio_tierra * math.cos(latOrigen) * math.sin(longOrigen),
                              radio_tierra * math.sin(latOrigen))
        coordenadas_destino = (radio_tierra * math.cos(latDestino) * math.cos(longDestino),
                               radio_tierra * math.cos(latDestino) * math.sin(longDestino),
                               radio_tierra * math.sin(latDestino))
        return round(math.sqrt((coordenadas_origen[0] - coordenadas_destino[0]) ** 2 + (
                coordenadas_origen[1] - coordenadas_destino[1]) ** 2 + (
                                       coordenadas_origen[2] - coordenadas_destino[2]) ** 2))


    def heuristica(self, origen, destino) -> int:
       return (self.calcularDistancia(self.json_coordenadas[self.grafo_metro.grafo.nodes[origen]["nombre"]]["results"][0]["geometry"].get("location", ()),
            self.json_coordenadas[self.grafo_metro.grafo.nodes[destino]["nombre"]]["results"][0]["geometry"].get("location", ())) +
            self.minimo_trasbordos[self.grafo_metro.grafo.nodes[origen]["linea"]][self.grafo_metro.grafo.nodes[destino]["linea"]] * 1080)

    @QtCore.Slot()
    def limpiar(self):
        self.texto.clear()
        self.texto2.clear()

        # Resetear cajas y label
        self.texto.setStyleSheet("")
        self.texto2.setStyleSheet("")
        #self.texto.setPlaceholderText("Origen")
        #self.texto2.setPlaceholderText("Destino")

        # limpiar mensaje de estado
        self.resumenruta.setText(f"Tiempo de viaje: --\nNumero de Paradas: --")
        self.label_estado.clear()
        self.label_estado.setStyleSheet("")

        # limpiamos el mapa
        self.lineaRuta.reinicio()
        self.mapa.limpiar_rutas()


    def buscar(self):
        origen = self.texto.text().strip() # cojo el texto de la caja (origen)
        destino = self.texto2.text().strip()

        # Reseteamos cajas y label
        self.texto.setStyleSheet("")
        self.texto2.setStyleSheet("")
        #self.texto.setPlaceholderText("Origen")
        #self.texto2.setPlaceholderText("Destino")
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
                    heuristic = self.heuristica,
                    weight = "weight"
                )
                coste_total = nx.astar_path_length(
                    self.grafo_metro.grafo,
                    id_origen,
                    id_destino,
                    heuristic = self.heuristica,
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
            else: #si no es la primera estación, compruebas si es transbordo. Si no lo es, es la siguiente parada
                if nombre == prev_nombre and linea != prev_linea:
                    #transbordo
                    lineas_salida.append(f"Transbordo de la línea {prev_linea} a la línea {linea}")
                elif nombre != prev_nombre:
                    # Siguiente estacion
                    lineas_salida.append(nombre)
            prev_nombre,prev_linea = nombre,linea # para la siguiente iteración

        texto_camino = "\n".join(lineas_salida)

        # Calculamos el Tiempo Estimado
        vel_m_h = 21600 # promedio del tren es de 25km/h
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
                                  f"El número total de paradas son: {num_estaciones}\n"
                                  f"Tiempo estimado de tu trayecto: {texto_tiempo}\n"
        )
        self.label_estado.setStyleSheet("color: green;")
        self.resumenruta.setText(f"Tiempo de viaje: {texto_tiempo}\nNumero de Paradas: {num_estaciones}")

        # Dibujar en el mapa
        #TODO: BORRAR SI NO NECESARIO
        # nombres_camino = [nombre for (nombre,linea) in estaciones_camino_optimo]
        self.mapa.add_ruta(estaciones_camino_optimo, color= QColor(0, 255, 60))
        self.lineaRuta.add_ruta(estaciones_camino_optimo)


class LineaRutaDibujo(QtWidgets.QWidget):
    aumento = 30
    inicio = 50
    ruta = []
    def __init__(self, scroll):
        super().__init__()
        #self.setStyleSheet("background: transparent;")
        self.scroll = scroll
        self.setStyleSheet("background: transparent;")
        self.resize(380,self.inicio)
        self.puntomedio = puntoMedio = int(self.width()/2)

    def redimension(self):
        self.resize(self.width(), self.height() + self.aumento)
        self.inicio += self.aumento

    def add_ruta(self, rutap):
        self.reinicio()
        self.ruta = rutap
        self.resize(self.width(), self.height() + self.aumento * len(rutap))
        self.update()

    def reinicio(self):
        self.resize(self.width(), self.inicio)
        self.ruta.clear()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 10))
        for i in range(len(self.ruta)):
            pos = self.inicio + self.aumento*i
            painter.setPen(QtGui.QPen(QtCore.Qt.white, 10))
            painter.drawText(QtCore.QPointF(self.puntomedio + 12, pos + 4), self.ruta[i][0])
            painter.setPen(QtGui.QPen(self.linea_color(self.ruta[i][1]), 10))
            painter.drawEllipse(QtCore.QPointF(self.puntomedio, pos), 5, 5)

            if i < len(self.ruta)-1:
                painter.drawLine(QtCore.QPointF(self.puntomedio, pos), QtCore.QPointF(self.puntomedio, pos + self.aumento))
                if self.ruta[i][1] != self.ruta[i + 1][1]:
                    painter.setPen(QtGui.QPen(QtCore.Qt.white, 10))
                    painter.drawText(QtCore.QPointF(self.puntomedio - 185, pos + (self.aumento/2)+1), f"Transbordo de linea: {self.ruta[i][1]} a linea: {self.ruta[i+1][1]}\n")


    def linea_color(self, linea) -> QtGui.QColor:
        switcher = {
            "1": QColor.fromRgb(211, 85, 144),
            "2": QColor.fromRgb(1, 124, 192),
            "3": QColor.fromRgb(158, 154, 58),
            "4": QColor.fromRgb(150, 207, 184),
            "5": QColor.fromRgb(250, 195, 3),
            "6": QColor.fromRgb(217, 38, 26),
            "7": QColor.fromRgb(238, 149, 58),
            "8": QColor.fromRgb(3, 146, 63),
            "9": QColor.fromRgb(141, 85, 68),
            "A": QColor.fromRgb(143, 30, 116),
            "B": QColor.fromRgb(169, 169, 169),
            "12": QColor.fromRgb(184, 157, 78),
        }
        return switcher.get(linea)




class RutasWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label_estado=None):
        super().__init__(parent)
        self.rutas = []
        self.label_estado = label_estado  # referencia al label de MainScreen
        # transparente (pero SIN WA_TransparentForMouseEvents para poder recibir clics)
        self.setStyleSheet("background: transparent;")
        self.lineas = {
            "1": ("Observatorio", "Tacubaya", "Juanacatlán", "Chapultepec", "Sevilla", "aux1L1","Insurgentes", "Cuauhtémoc",
                  "Balderas", "Salto del Agua", "Isabel la Católica", "Pino Suárez", "aux2L1", "Merced", "Candelaria",
                  "San Lázaro", "Moctezuma", "Balbuena", "aux3L1", "Boulevard Puerto Aéreo", "aux4L1", "Gómez Farías",
                  "Zaragoza", "aux5L1", "Pantitlán"),
            "2": ("Cuatro Caminos", "Panteones", "Tacuba", "Cuitláhuac", "Popotla", "aux1L2", "Colegio Militar", "Normal",
                  "San Cosme", "Revolución", "Hidalgo", "Bellas Artes", "aux2L2", "Allende", "aux3L2", "Zócalo",
                  "Pino Suárez", "San Antonio Abad", "Chabacano", "Viaducto", "Xola", "Villa de Cortés", "Nativitas",
                  "Portales", "Ermita", "General Anaya", "Tasqueña"),
            "3": ("Indios Verdes", "Deportivo 18 de Marzo", "aux1L3", "Potrero", "La Raza", "Tlatelolco", "aux2L3",
                  "Guerrero", "Hidalgo", "Juárez", "Balderas", "Niños Héroes", "Hospital General", "Centro Médico",
                  "Etiopía/Plaza de la Transparencia", "Eugenia", "División del Norte", "Zapata", "Coyoacán",
                  "Viveros/Derechos Humanos", "Miguel Ángel de Quevedo", "Copilco", "Universidad"),
            "4": ("Martín Carrera", "Talismán", "Bondojito", "Consulado", "Canal del Norte", "Morelos", "Candelaria",
                  "Fray Servando", "Jamaica", "Santa Anita"),
            "5": ("Pantitlán", "Hangares", "Terminal Aérea", "aux1L5", "Oceanía", "Aragón", "Eduardo Molina", "aux2L5",
                  "Consulado", "Valle Gómez", "aux3L5", "Misterios", "La Raza", "Autobuses del Norte",
                  "Instituto del Petróleo", "aux4L5", "Politécnico"),
            "6": ("El Rosario", "Tezozómoc", "aux1L6", "Azcapotzalco", "Ferrería", "Norte 45", "Vallejo",
                  "Instituto del Petróleo", "Lindavista", "Deportivo 18 de Marzo", "La Villa-Basílica",
                  "Martín Carrera"),
            "7": ("El Rosario", "Aquíles Serdán", "Camarones", "Refinería", "Tacuba", "San Joaquín", "Polanco",
                  "Auditorio", "Constituyentes", "Tacubaya", "San Pedro de los Pinos", "San Antonio", "Mixcoac",
                  "Barranca del Muerto"),
            "8": ("Garibaldi", "Bellas Artes", "San Juan de Letrán", "Salto del Agua", "aux1L8", "Doctores", "Obrera",
                  "Chabacano", "La Viga", "aux2L8", "Santa Anita", "aux3L8", "aux4L8", "Coyuya", "Iztacalco",
                  "Apatlaco", "Aculco", "Escuadrón 201", "aux5L8", "Atlalilco", "aux6L8", "Iztapalapa",
                  "Cerro de la Estrella", "UAM I", "Constitución de 1917"),
            "9": ("Tacubaya", "Patriotismo", "Chilpancingo", "Centro Médico", "Lázaro Cárdenas", "Chabacano", "Jamaica",
                  "Mixiuhca", "Velódromo", "Ciudad Deportiva", "aux1L9", "Puebla", "Pantitlán"),
            "A": ("Pantitlán", "aux1LA", "Agrícola Oriental", "Canal de San Juan", "Tepalcates", "Guelatao",
                  "Peñón Viejo", "Acatitla", "Santa Marta", "aux2LA", "Los Reyes", "La Paz"),
            "B": ("Ciudad Azteca", "Plaza Aragón", "Olímpica", "Ecatepec", "Múzquiz", "Río de los Remedios",
                  "Impulsora", "Nezahualcóyotl", "Villa de Aragón", "Bosques de Aragón", "aux1LB", "Deportivo Oceanía",
                  "Oceanía", "Romero Rubio", "aux2LB", "Ricardo Flores Magón", "San Lázaro", "Morelos", "aux3LB",
                  "Tepito", "Lagunilla", "Garibaldi", "Guerrero", "Buenavista"),
            "12": ("Tláhuac", "Tlaltenco", "Zapotitlán", "Nopalera", "Olivos", "Tezonco", "Periférico Oriente",
                   "aux1L12", "Calle 11", "Lomas Estrella", "San Andrés Tomatlán", "Culhuacán", "Atlalilco",
                   "Mexicaltzingo", "aux2L12", "Ermita", "Eje Central", "aux3L12", "aux4L12", "Parque de los Venados",
                   "Zapata", "Hospital 20 de Noviembre", "Insurgentes Sur", "Mixcoac")
        }
        self.coordenadas = GetCoordenadas()

    def add_ruta(self,ruta, color=QColor(0,255,60)):
        """Recibe una lista de nombres de estaciones y construye (nombre, (x,y))."""
        #print(f"RUTA RECIBIDA: {ruta}")
        coords : list[tuple[str, tuple[float, float]]] = []
        for i in range(len(ruta)-1):
            origen = str(ruta[i][0])
            linea_origen = str(ruta[i][1])
            destino = str(ruta[i+1][0])
            linea_destino = str(ruta[i+1][1])
            #print(f"origen {origen} destino {destino} linea_o {linea_origen} linea_d {linea_destino}")
            if linea_origen == linea_destino:
                index_origen = self.lineas[linea_origen].index(origen)
                index_destino = self.lineas[linea_destino].index(destino)
                inicio = min(index_origen, index_destino)
                fin = max(index_origen, index_destino)
                #print(f"ORIGEN {origen} DESTINO {destino}")
                lista_add = []
                for j in range(inicio, fin+1):
                    nombre_pintar = str(self.lineas[linea_origen][j])
                    coordenadas_pintar = self.coordenadas.getc(nombre_pintar)
                    entrada_coordenadas = (nombre_pintar, coordenadas_pintar)
                    if coords.count(entrada_coordenadas) == 0:
                        #print(f"SE HA AÑADIDO: {entrada_coordenadas}")
                        lista_add.append(entrada_coordenadas)
                if index_destino < index_origen:
                    lista_add.reverse()
                for entrada in lista_add:
                    coords.append(entrada)
        #print(f"LA LISTA DE COORDENADAS ES {coords}")
        entrada_rutas = (color, coords)
        self.rutas.append(entrada_rutas)
        self.update()

    def limpiar_rutas(self):
        self.rutas.clear()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for color, estaciones in self.rutas:
            print(color.name())
            # líneas entre estaciones consecutivas
            painter.setPen(QtGui.QPen(color, 6))
            for i in range(len(estaciones) - 1):
                _, (x1, y1) = estaciones[i]
                _, (x2, y2) = estaciones[i + 1]
                painter.drawLine(x1, y1, x2, y2)

            # círculos en cada estación (excepto nombres 'aux')
            painter.setPen(QtGui.QPen(color, 1))  # borde
            painter.setBrush(QtGui.QBrush(color))  # relleno
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
        #self.textos.setStyleSheet("CajasTexto#textos {}")

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
    sys.exit(app.exec())

