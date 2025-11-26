import json
import math

from cambiar_pesos_conexiones import heuristica
# Comprueba que la heuristica sea minorante para todo par de de estaciones adyacentes
if __name__ == "__main__":
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

