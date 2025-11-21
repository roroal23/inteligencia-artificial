
import sys
import json
import networkx as nx
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import QSizePolicy
import math

def minimoTrasbordos(origen, destino) -> int:
    trasbordos = {
        "1": {"1": 0,"2": 1,"3": 1,"4": 1,"5": 1,"6": 2, "7": 1, "8": 1, "9": 1, "A": 1, "B": 1, "12": 2},
        "2":{"1": 1,"2": 0,"3": 1,"4": 2, "5": 2, "6": 2, "7": 1, "8": 1, "9": 1, "A": 2, "B": 2, "12": 1},
        "3":{"1":1,"2": 1,"3": 0,"4": 2, "5":1, "6":1 , "7":2 , "8":2 , "9":1 , "A":2 , "B": 1, "12": 1},
        "4":{"1": 1,"2": 2,"3": 2,"4": 0,"5":1, "6": 1, "7": 2, "8": 1, "9": 1, "A":2 , "B":1 , "12":2 },
        "5":{"1": 1,"2": 2,"3":1, "4": 1,"5": 0,"6": 1, "7": 2, "8": 2, "9": 1, "A": 1, "B": 1, "12":2 },
        "6":{"1": 2,"2": 2,"3": 1,"4": 1,"5": 1,"6": 0, "7": 1, "8": 2, "9": 2, "A": 2, "B": 2, "12": 2},
        "7":{"1": 1,"2": 1,"3": 2,"4":2, "5":2, "6": 1, "7": 0, "8": 2, "9": 1, "A": 2, "B": 2, "12": 1},
        "8":{"1": 1,"2": 1,"3":2, "4":1, "5":2, "6": 2, "7": 2, "8": 0, "9": 1, "A": 2, "B": 1, "12": 1},
        "9":{"1": 1,"2": 1,"3": 1,"4": 1, "5":1, "6": 2, "7": 1, "8": 1, "9": 0, "A": 1, "B": 2, "12": 2},
        "A":{"1": 1,"2": 2,"3":2, "4":2, "5":1, "6": 2, "7": 2, "8": 2, "9": 1, "A": 0, "B": 2, "12": 3},
        "B":{"1": 1,"2": 2,"3": 1, "4": 1, "5":1, "6": 2, "7": 2, "8": 1, "9": 2, "A": 2, "B": 0, "12": 2},
        "12":{"1":2,"2": 1,"3": 1,"4":2, "5": 2,"6": 2, "7": 1, "8": 1, "9": 2, "A": 3, "B": 2, "12": 0},

    }
    return trasbordos[origen][destino]

def calcularDistancia(coordsOrigen,coordsDestino) -> int:
    print(coordsOrigen)
    print(coordsDestino)
    latOrigen =  math.radians(float(coordsOrigen["lat"]))
    longOrigen =  math.radians(float(coordsOrigen["lng"]))
    latDestino =  math.radians(float(coordsDestino["lat"]))
    longDestino =  math.radians(float(coordsOrigen["lng"]))
    radio_tierra = 6371000
    coordenadas_origen = (radio_tierra*math.cos(latOrigen)*math.cos(longOrigen),radio_tierra*math.cos(latOrigen)*math.sin(longOrigen),radio_tierra*math.sin(latOrigen))
    coordenadas_destino = (radio_tierra * math.cos(latDestino) * math.cos(longDestino), radio_tierra * math.cos(latDestino) * math.sin(longDestino), radio_tierra * math.sin(latDestino))
    return round(math.sqrt( (coordenadas_origen[0] - coordenadas_destino[0]) **2 + (coordenadas_origen[1] - coordenadas_destino[1]) **2 + (coordenadas_origen[2] - coordenadas_destino[2]) **2 ))

    #Heurística. TODO: revisar que sea minorante en todos los casos
def heuristica (origen, destino) -> int:
    with open("./data/estaciones_metro2.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return (calcularDistancia(data[origen["nombre"]]["results"][0]["geometry"].get("location", ()),  data[destino["nombre"]]["results"][0]["geometry"].get("location",()))
            + minimoTrasbordos(origen["linea"],destino["linea"]) * 1080)

if __name__ == '__main__':
    with open("./data/230Conexiones_v3.txt", "r", encoding="utf-8") as f:
        conexiones = []
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(",")
                origen = {"nombre": parts[0], "linea": parts[1]}
                destino = {"nombre": parts[2], "linea": parts[3]}
                dist_calculada = heuristica(origen, destino)
                if dist_calculada > int(parts[4]):
                    parts[4] = dist_calculada
                conexiones.append(parts)
    with open("./data/230Conexiones_v4.txt", "w", encoding="utf-8") as f:
        for conexion in conexiones:
            f.write(f"{conexion[0]},{conexion[1]},{conexion[2]},{conexion[3]},{conexion[4]}\n")
