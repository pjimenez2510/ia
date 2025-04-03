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