from collections import deque

grafo = {
    'A': {'B': 5, 'C': 10},
    'B': {'A': 5, 'D': 3, 'E': 8},
    'C': {'A': 10, 'F': 7},
    'D': {'B': 3, 'E': 2, 'G': 4},
    'E': {'B': 8, 'D': 2, 'G': 5},
    'F': {'C': 7, 'G': 6},
    'G': {'D': 4, 'E': 5, 'F': 6}
}

def bfs(grafo, origen, destino):
    cola = deque([(origen, [origen])])
    visitados = set()
    
    while cola:
        nodo, camino = cola.popleft()
        if nodo == destino:
            return camino
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None

ruta_bfs = bfs(grafo, 'A', 'G')

print(ruta_bfs)

