
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

class GetCoordenadas():
    def __init__(self):
        super().__init__()
        self.json_solicitudes = {}
        self.ESTACIONES = {}
        with open(file="data/163CoordInterfaz.txt", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    self.ESTACIONES[parts[0]] = (float(parts[1]), float(parts[2]))
        with open("./data/estaciones_metro2.json", "r", encoding="utf-8") as f:
            self.json_solicitudes = json.load(f)

    def getc(self, nombre: str) -> tuple[float, float]:
        return self.ESTACIONES[nombre]
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
    retorno = (calcularDistancia(data[origen["nombre"]]["results"][0]["geometry"].get("location", ()),  data[destino["nombre"]]["results"][0]["geometry"].get("location",()))
            + minimoTrasbordos(origen["linea"],destino["linea"]) * 1080)
    if retorno < 0:
        print("SE HA ENCONTRADO HEURISTICA MENOR QUE 0")
    return retorno

if __name__ == "__main__":
    print("SE HA CREADO CONEXIONES")
    coords = GetCoordenadas()
    print("SE HA CREADO COORDS")
    with open("data/230Conexiones_v4.txt", "r", encoding="utf-8") as fichero:
        with open("data/fallos_heuristica.txt", "w", encoding="utf-8") as fallos:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    origen = {"nombre" : partes[0], "linea":partes[1]}
                    destino = {"nombre": partes[2], "linea": partes[3]}
                    dist_calculada = heuristica(origen,destino)
                    #fallos.write(f"SE HA OBTENIDO {partes[4]},  HEURISTICA {dist_calculada}")
                    print(f"SE HA CALCULADO LA DISTANCIA {dist_calculada} Y EL VALOR DEL FICHERO ES {partes[4]}")
                    if dist_calculada > int(partes[4]):
                        fallos.write(f"\nERROR EN LA HEURISTICA, DISTANCIA ENTRE {partes[0]} y {partes[2]} = {int(partes[4])}, PERO LA HEURISTICA DICE {dist_calculada}")
                        fallos.write("\n---------------------------------------------------------------------------------------------------------------------------------------\n")
                    elif dist_calculada == int(partes[4]):
                        fallos.write(f"LA CONEXION {partes[0]}, {partes[2]} HA SIDO CAMBIADA CORRECTAMENTE\n-----------------------------------------------------\n")
    print("SE HA TERMINADO DE COMPROBAR")

