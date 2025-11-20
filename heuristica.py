import networkx as nx
import json
if __name__ == '__main__':
    #Representacion de las lineas como listas de paradas (o puntos intermedios) para pintar
    lineas = {
        "1": ("Observatorio","Tacubaya","Juanacatlán","Chapultepec","Sevilla","aux1L1","Insurgentes","Cuauhtémoc","Balderas","Salto del Agua","Isabel la Católica","Pino Suárez","aux2L1","Merced","Candelaria","San Lázaro","Moctezuma","Balbuena","aux3L1","Boulevard Puerto Aéreo","aux4L1","Gómez Farías","Zaragoza","aux5L1","Pantitlán"),
        "2":("Cuatro Caminos","Panteones","Cuitláhuac","Popotla","aux1L2","Colegio Militar","Normal","San Cosme","Revolución","Hidalgo","Bellas Artes","aux2L2","Allende","aux3L2","Zócalo","Pino Suárez","San Antonio Abad","Chabacano","Viaducto","Xola","Villa de Cortés","Nativitas","Portales","Ermita","General Anaya","Tasqueña"),
        "3":("Indios Verdes","Deportivo 18 de Marzo","aux1L3","Potrero","La Raza","Tlatelolco","aux2L3","Guerrero","Hidalgo","Juárez","Balderas","Niños Héroes","Hospital General","Centro Médico","Etiopía/Plaza de la Transparencia","Eugenia","División del Norte","Zapata","Coyoacán","Viveros/Derechos Humanos","Miguel Ángel de Quevedo","Copilco","Universidad"),
        "4":("Martín Carrera","Talismán","Bondojito", "Consulado","Canal del Norte","Morelos","Candelaria","Fray Servando","Jamaica","Santa Anita"),
        "5":("Pantitlán","Hangares","Terminal Aérea","aux1L5","Oceanía","Aragón","Eduardo Molina","aux2L5","Consulado","Valle Gómez","aux3L5","Misterios","La Raza","Autobuses del Norte","Instituto del Petróleo","aux4L5","Politécnico"),
        "6":("El Rosario","Tezozómoc","aux1L6","Azcapotzalco","Ferrería","Norte 45","Vallejo","Instituto del Petróleo","Lindavista","Deportivo 18 de Marzo","La Villa-Basílica","Martín Carrera"),
        "7":("El Rosario","Aquíles Serdán","Camarones","Refinería","Tacuba","San Joaquín","Polanco","Auditorio","Constituyentes","Tacubaya","San Pedro de los Pinos","San Antonio","Mixcoac","Barranca del Muerto"),
        "8":("Garibaldi","Bellas Artes","San Juan de Letrán","Salto del Agua","aux1L8","Doctores","Obrera","Chabacano","La Viga","aux2L8","Santa Anita","aux3L8","aux4L8","Coyuya","Iztacalco","Apatlaco","Aculco","Escuadrón 201","aux5L8","Atlalilco","aux6L8","Iztapalapa","Cerro de la Estrella","UAM I","Constitución de 1917"),
        "9":("Tacubaya","Patriotismo","Chilpancingo","Centro Médico","Lázaro Cárdenas","Chabacano", "Jamaica","Mixiuhca","Velódromo","Ciudad Deportiva","aux1L9","Puebla","Pantitlán"),
        "A":("Pantitlán","aux1LA","Agrícola Oriental","Canal de San Juan","Tepalcates","Guelatao","Peñón Viejo","Acatitla","Santa Marta","aux2LA","Los Reyes","La Paz"),
        "B":("Ciudad Azteca","Plaza Aragón","Olímpica","Ecatepec","Múzquiz","Río de los Remedios","Impulsora","Nezahualcóyotl","Villa de Aragón","Bosques de Aragón","aux1LB","Deportivo Oceanía","Oceanía","Romero Rubio","aux2LB","Ricardo Flores Magón","San Lázaro","Morelos","aux3LB","Tepito","Lagunilla","Garibaldi","Guerrero","Buenavista"),
        "12":("Tláhuac","Tlaltenco","Zapotitlán","Nopalera","Olivos","Tezonco","Periférico Oriente","aux1L12","Calle 11","Lomas Estrella","San Andrés Tomatlán","Culhuacán","Atlalilco","Mexicaltzingo","aux2L12","Ermita","Eje Central","aux3L12","aux4L12","Parque de los Venados","Zapata","Hospital 20 de Noviembre","Insurgentes Sur","Mixcoac")
    }
    #Prueba de ver si funciona
    origen = "Pantitlán"
    linea_origen = "5"
    destino = "Oceanía"
    linea_destino = "5"
    index_origen = lineas[linea_origen].index(origen)
    index_destino = lineas[linea_destino].index(destino)
    print(f"Indice origen ({origen}): {index_origen}, Indices destino ({destino}): {index_destino}")
    inicio = min(index_origen, index_destino)
    fin = max(index_origen, index_destino)
    for i in range (inicio, fin):
        print(f"Se pinta linea de {lineas[linea_origen][i]} a {lineas[linea_origen][i+1]}")

#Implementacion de la matriz de trasbordos con un diccionario de diccionarios
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
        "9":{"1": 1,"2": 1,"3": 1, "4": 1, "5":1, "6": 2, "7": 1, "8": 1, "9": 0, "A": 1, "B": 2, "12": 2},
        "A":{"1": 1,"2": 2,"3":2, "4":2, "5":1, "6": 2, "7": 2, "8": 2, "9": 1, "A": 0, "B": 2, "12": 3},
        "B":{"1": 1,"2": 2,"3": 1, "4": 1, "5":1, "6": 2, "7": 2, "8": 1, "9": 2, "A": 2, "B": 0, "12": 2},
        "12":{"1":2,"2": 1,"3": 1,"4":2, "5": 2,"6": 2, "7": 1, "8": 1, "9": 2, "A": 3, "B": 2, "12": 0},

    }
    return trasbordos[origen["nombre"]][destino["nombre"]]
#Funcion implementada por Christian
def calcularDistancia(coordsOrigen,coordsDestino) -> int:
    return 0
#Heurística. TODO: revisar que sea minorante en todos los casos
def heuristica (origen, destino) -> int:
    with open("./data/estaciones_metro2.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (
            calcularDistancia(data[origen["nombre"]]["results"][0].get("geometry", ()),  data[destino["nombre"]]["results"][0].get("geometry",()))
            + minimoTrasbordos(origen["linea"],destino["linea"]) * 1080
            )
