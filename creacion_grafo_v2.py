import networkx as nx
import matplotlib.pyplot as plt

"""
CONFIGURACION
"""
FICHERO_ESTACIONES = "data/195Estaciones_v2.txt"
FICHERO_CONEXIONES = "data/230Conexiones_v%.txt"

"""
CLASES
"""
class LectorFichero():
    """Se encarga de leer los ficheros"""
    def __init__(self):
        self.fichero_estaciones: str = FICHERO_ESTACIONES
        self.fichero_conexiones: str = FICHERO_CONEXIONES

    """Lee las estaciones y su linea correspondiente. Devuelve una lista de ellas"""
    def obtener_estaciones(self) -> list[tuple[str, str]]:
        estaciones: list[tuple[str, str]] = []
        with open(self.fichero_estaciones, "r", encoding = "utf-8") as fichero:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    estaciones.append((partes[0], partes[1]))
        return estaciones

    @staticmethod
    def obtener_estaciones_163() -> list[str]:
        estaciones: list[str] = []
        estaciones_unico: str = "data/163Estaciones.txt"
        with open(estaciones_unico, "r", encoding = "utf-8") as fichero:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    estaciones.append(linea)
        return estaciones

    """Lee las conexiones entre estaciones y devuelve una lista de conexiones: [origen, linea_o, destino, linea_d, peso]"""
    def obtener_conexiones(self) -> list[tuple[str, str, str, str, int]]:
        conexiones: list[tuple[str, str, str, str, int]] = []
        with open(self.fichero_conexiones, "r", encoding = "utf-8") as fichero:

            for linea in fichero:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    conexiones.append((partes[0], partes[1], partes[2], partes[3], int(partes[4])))
        return conexiones


class TablaEstaciones():
    """ Mantiene mapas de relaciones entre el nombre de una estacion y su identificador.
        Ademas contiene un mapa que relaciona el nombre de estacion con las lineas a las que pertenece
    """
    def __init__(self, estaciones: list[tuple[str,str]]):
        self.estacion_a_id : dict[tuple[str,str], int] = {}
        self.id_a_estacion : dict[int, tuple[str,str]] = {}
        self.estacion_a_lineas : dict[str, list[str]] = {}
        self.estaciones = estaciones
        self.transbordos : set[str] = set()
        self.rellenar_mapas()

    def rellenar_mapas(self):
        i = 0
        for nombre, linea in self.estaciones:
            #Rellena el mapa estacion -> lineas
            if nombre not in self.estacion_a_lineas:
                self.estacion_a_lineas[nombre] = []
            self.estacion_a_lineas[nombre].append(linea)

            #Rellena transbordos
            if nombre not in self.transbordos and len(self.estacion_a_lineas[nombre]) >= 2:
                self.transbordos.add(nombre)

            #Rellena los mapas estacion <-> id
            self.estacion_a_id[(nombre, linea)] = i
            self.id_a_estacion[i] = (nombre, linea)
            i += 1


    def obtener_estacion(self, i: int) -> tuple[str,str]:
        return self.id_a_estacion[i]

    def obtener_id(self, estacion: tuple[str,str]) -> int:
        return self.estacion_a_id[estacion]

    def obtener_lineas(self, nombre: str) -> list[str]:
        return self.estacion_a_lineas[nombre]


class GrafoMetro():
    """Crea y almacena el grafo del metro de la CDMX"""
    def __init__(self, mapa: TablaEstaciones, estaciones: list[tuple[str,str]], conexiones: list[tuple[str, str, str, str, int]]):
        self.mapa = mapa
        self.estaciones = estaciones
        self.conexiones = conexiones
        self.grafo = nx.Graph()

        self.rellenar_nodos()
        self.rellenar_aristas()

    """Rellena los nodos del grafo. Cada nodo se identifica por un id y tiene de atributo el nombre"""
    def rellenar_nodos(self):
        for estacion in self.estaciones:
            id_estacion = self.mapa.obtener_id(estacion)
            self.grafo.add_node(id_estacion, nombre = estacion[0], linea = estacion[1])

    """Rellena las aristas del grafo. Cada arista tiene su id_origen, id_destino, peso"""
    def rellenar_aristas(self):
        for conexion in self.conexiones:
            #print(conexion)
            id_origen = self.mapa.obtener_id((conexion[0], conexion[1]))
            id_destino = self.mapa.obtener_id((conexion[2], conexion[3]))
            self.grafo.add_edge(id_origen, id_destino, weight = conexion[4])



def main():
    lector = LectorFichero()
    estaciones = lector.obtener_estaciones()
    print(f"Hay {len(estaciones)} estaciones")
    print(estaciones)
    conexiones = lector.obtener_conexiones()
    print(f"Hay {len(conexiones)} conexiones")
    print(conexiones)
    tabla_estaciones = TablaEstaciones(estaciones)
    print("Tabla de estaciones -> id")
    print(tabla_estaciones.estacion_a_id)
    print("Tabla de id -> estacion")
    print(tabla_estaciones.id_a_estacion)
    print("Tabla de estacion -> lineas")
    print(tabla_estaciones.estacion_a_lineas)
    grafo_metro = GrafoMetro(tabla_estaciones, estaciones, conexiones)
    print(grafo_metro.grafo.nodes)
    print(grafo_metro.grafo.edges)

    #Imprimir el grafo

    colores_linea = {
        "1" : "pink",
        "2" : "blue",
        "3" : "lime",
        "4" : "cyan",
        "5" : "yellow",
        "6" : "red",
        "7" : "orange",
        "8" : "green",
        "9" : "brown",
        "12" : "navy",
        "A" : "purple",
        "B" : "gray"
    }
    print(grafo_metro.grafo.nodes(data = True))
    colores_nodos = [colores_linea[data["linea"]] for n, data in grafo_metro.grafo.nodes(data = True)]

    plt.figure(figsize=(100, 60))
    grafo_metro.rellenar_aristas()

    # pos = nx.planar_layout(grafo_metro.grafo)
    # pos = nx.spring_layout(grafo_metro.grafo, k = 3)
    pos = nx.kamada_kawai_layout(grafo_metro.grafo)
    nx.draw(grafo_metro.grafo, pos, node_color=colores_nodos, with_labels=False, node_size=300)
    nombres = nx.get_node_attributes(grafo_metro.grafo, "nombre")
    ############################
    # Dibujar nombres una sola vez
    nombres_dibujados = set()
    etiquetas_nombres = {}
    etiquetas_lineas = {}
    for n, data in grafo_metro.grafo.nodes(data=True):
        nombre = data["nombre"]
        if nombre not in nombres_dibujados:
            etiquetas_nombres[n] = nombre
            lineas = tabla_estaciones.obtener_lineas(nombre)
            etiquetas_lineas[n] = ", ".join(lineas)
            nombres_dibujados.add(nombre)
    ############################
    # Desplazar ligeramente las etiquetas de línea
    pos_lineas = {n: (x, y - 0.003) for n, (x, y) in pos.items() if n in etiquetas_lineas}

    nx.draw_networkx_labels(grafo_metro.grafo, pos, labels=etiquetas_nombres, font_size=8)
    nx.draw_networkx_labels(grafo_metro.grafo, pos_lineas, labels=etiquetas_lineas, font_size=7)
    peso_aristas = nx.get_edge_attributes(grafo_metro.grafo, "weight")
    nx.draw_networkx_edge_labels(grafo_metro.grafo, pos, edge_labels=peso_aristas, font_size=7)
    plt.show()


if __name__ == "__main__":
    main()
