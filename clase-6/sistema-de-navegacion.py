import heapq
from math import sqrt
import networkx as nx
import matplotlib.pyplot as plt

# Grafo del mapa (representado como diccionario de adyacencia)
mapa_ciudad = {
    'Almacén': {'A': 2, 'B': 5},
    'A': {'Almacén': 2, 'C': 3, 'D': 4},
    'B': {'Almacén': 5, 'D': 2, 'E': 6},
    'C': {'A': 3, 'F': 1},
    'D': {'A': 4, 'B': 2, 'F': 3, 'G': 2},
    'E': {'B': 6, 'G': 4},
    'F': {'C': 1, 'D': 3, 'Destino': 7},
    'G': {'D': 2, 'E': 4, 'Destino': 3},
    'Destino': {'F': 7, 'G': 3}
}

coordenadas = {
    'Almacén': (0, 0),
    'A': (2, 1),
    'B': (4, -1),
    'C': (5, 3),
    'D': (4, 2),
    'E': (8, -2),
    'F': (6, 4),
    'G': (6, 1),
    'Destino': (9, 3)
}


def heuristica(nodo_actual, nodo_destino):
    x1, y1 = coordenadas[nodo_actual]
    x2, y2 = coordenadas[nodo_destino]
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def a_star(mapa, inicio, destino):
    frontera = []
    heapq.heappush(frontera, (0 + heuristica(inicio, destino), inicio, [], 0))
    visitados = set()
    
    while frontera:
        _, nodo_actual, camino, costo_acumulado = heapq.heappop(frontera)
        
        if nodo_actual == destino:
            return camino + [nodo_actual], costo_acumulado
        
        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            for vecino, distancia in mapa[nodo_actual].items():
                nuevo_costo = costo_acumulado + distancia
                heapq.heappush(frontera,
                              (nuevo_costo + heuristica(vecino, destino),
                               vecino,
                               camino + [nodo_actual],
                               nuevo_costo))
    
    return None