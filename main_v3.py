
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

    def distancia_menor(self, estacion1:str, estacion2:str) -> float:
        """ Devulve la distancia en línea recta entre dos estaciones en METROS
            usando la fórmula de Haversine sobre una Tierra esférica"""
        lat1_deg = self.json_solicitudes[estacion1]["results"][0]["geometry"]["location"]["lat"]
        lon1_deg = self.json_solicitudes[estacion1]["results"][0]["geometry"]["location"]["lng"]
        lat2_deg = self.json_solicitudes[estacion2]["results"][0]["geometry"]["location"]["lat"]
        lon2_deg = self.json_solicitudes[estacion2]["results"][0]["geometry"]["location"]["lng"]

        # Pasar a radianes
        lat1 = math.radians(lat1_deg)
        lon1 = math.radians(lon1_deg)


        lat2 = math.radians(lat2_deg)
        lon2 = math.radians(lon2_deg)

        dlat = lat2-lat1
        dlon = lon2-lon1

        #TODO: probar distancia euclídea
        # Haversine

        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        R = 6371000 # radio de la Tierra en metros
        distancia_metros = R*c
        return distancia_metros


if __name__ == "__main__":
    print("SE HA CREADO CONEXIONES")
    coords = GetCoordenadas()
    print("SE HA CREADO COORDS")
    with open("data/230Conexiones_v3.txt", "r", encoding="utf-8") as fichero:
        with open("data/fallos_heuristica.txt", "w", encoding="utf-8") as fallos:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    dist_calculada = coords.distancia_menor(partes[0], partes[2])
                    #fallos.write(f"SE HA OBTENIDO {partes[4]},  HEURISTICA {dist_calculada}")
                    if (dist_calculada > (int(partes[4]) + 150)):
                        fallos.write(f"\nERROR EN LA HEURISTICA, DISTANCIA ENTRE {partes[0]} y {partes[2]} = {int(partes[4])}, PERO LA HEURISTICA DICE {dist_calculada}")
                        fallos.write("\n---------------------------------------------------------------------------------------------------------------------------------------\n")
    print("SE HA TERMINADO DE COMPROBAR")

