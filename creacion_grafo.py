import networkx as nx
import matplotlib.pyplot as plt

"""
CONFIGURACION
"""
FICHERO_ESTACIONES = "data/163Estaciones.txt"
FICHERO_CONEXIONES = "data/183Conexiones.txt"

"""
CLASES
"""
class LectorFichero():
    """Se encarga de leer los ficheros"""
    def __init__(self):
        self.fichero_estaciones: str = FICHERO_ESTACIONES
        self.fichero_conexiones: str = FICHERO_CONEXIONES

    """Lee las estaciones y devuelve una lista de ellas"""
    def obtener_estaciones(self) -> list[str]:
        estaciones: list[str] = []
        with open(self.fichero_estaciones, "r", encoding = "utf-8") as fichero:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    estaciones.append(linea)
        return estaciones

    """Lee las conexiones entre estaciones y devuelve una lista de conexiones: [origen, destino, peso]"""
    def obtener_conexiones(self) -> list[tuple[str, str, int]]:
        conexiones: list[tuple[str, str, int]] = []
        with open(self.fichero_conexiones, "r", encoding = "utf-8") as fichero:
            for linea in fichero:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    conexiones.append((partes[0], partes[1], int(partes[2])))
        return conexiones


class TablaEstaciones():
    """Mantiene mapas de relaciones entre el nombre de una estacion y su identificador"""
    def __init__(self, estaciones: list[str]):
        self.nombre_a_id : dict[str, int] = {}
        self.id_a_nombre : dict[int, str] = {}
        self.estaciones = estaciones
        self.rellenar_mapas()

    def rellenar_mapas(self):
        i = 0
        for estacion in self.estaciones:
            self.nombre_a_id[estacion] = i
            self.id_a_nombre[i] = estacion
            i += 1

    def obtener_nombre(self, i: int) -> str:
        return self.id_a_nombre[i]

    def obtener_id(self, estacion: str) -> int:
        return self.nombre_a_id[estacion]

class GrafoMetro():
    """Crea y almacena el grafo del metro de la CDMX"""
    def __init__(self, mapa: TablaEstaciones, estaciones: list[str], conexiones: list[tuple[str, str, int]]):
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
            self.grafo.add_node(id_estacion, nombre = estacion)

    """Rellena las aristas del grafo. Cada arista tiene su id_origen, id_destino, peso"""
    def rellenar_aristas(self):
        for conexion in self.conexiones:
            id_origen = self.mapa.obtener_id(conexion[0])
            id_destino = self.mapa.obtener_id(conexion[1])
            self.grafo.add_edge(id_origen, id_destino, weight = conexion[2])



def main():
    lector = LectorFichero()
    estaciones = lector.obtener_estaciones()
    print(estaciones)
    conexiones = lector.obtener_conexiones()
    print(conexiones)
    tabla_estaciones = TablaEstaciones(estaciones)
    print(tabla_estaciones.nombre_a_id)
    print(tabla_estaciones.id_a_nombre)
    grafo_metro = GrafoMetro(tabla_estaciones, estaciones, conexiones)
    print(grafo_metro.grafo.nodes)
    print(grafo_metro.grafo.edges)

    #Imprimir el grafo

    fig = plt.figure( figsize=(60,30))
    grafo_metro.rellenar_aristas()

    #pos = nx.planar_layout(grafo_metro.grafo)
    #pos = nx.spring_layout(grafo_metro.grafo, k = 3)
    pos = nx.kamada_kawai_layout(grafo_metro.grafo)

    nx.draw(grafo_metro.grafo, pos, with_labels=False,  node_size = 300)
    nombres = nx.get_node_attributes(grafo_metro.grafo, "nombre")
    nx.draw_networkx_labels(grafo_metro.grafo, pos, labels = nombres, font_size = 10)
    peso_aristas = nx.get_edge_attributes(grafo_metro.grafo, "weight")
    nx.draw_networkx_edge_labels(grafo_metro.grafo, pos, edge_labels = peso_aristas, font_size = 10)
    plt.show()

if __name__ == "__main__":
    main()
















