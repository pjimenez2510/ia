
def bfs(grafo, inicio, meta):
    
    pila = [(inicio, [inicio])]
    
    visitados = set()
    
    while pila:
        nodo, camino = pila.pop()
        
        if nodo == meta:
            return camino
        
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                nuevo_camino = camino + [vecino]
                pila.append((vecino, nuevo_camino))
    return None

grafo = grafo = {
    'A': {'B': 5, 'C': 10},
    'B': {'A': 5, 'D': 3, 'E': 8},
    'C': {'A': 10, 'F': 7},
    'D': {'B': 3, 'E': 2, 'G': 4},
    'E': {'B': 8, 'D': 2, 'G': 5},
    'F': {'C': 7, 'G': 6},
    'G': {'D': 4, 'E': 5, 'F': 6}
}

camino =bfs(grafo, 'A', 'G')

print(camino)