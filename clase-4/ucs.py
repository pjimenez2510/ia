import heapq

grafo = {
    'A': {'B': 5, 'C': 10},
    'B': {'A': 5, 'D': 3, 'E': 8},
    'C': {'A': 10, 'F': 7},
    'D': {'B': 3, 'E': 2, 'G': 4},
    'E': {'B': 8, 'D': 2, 'G': 5},
    'F': {'C': 7, 'G': 6},
    'G': {'D': 4, 'E': 5, 'F': 6}
}

def ucs(grafo, origen, destino):
    cola_prioridad = [(0, origen, [origen])]
    visitados = set()
    while cola_prioridad:
        costo, nodo, camino = heapq.heappop(cola_prioridad)
        if nodo == destino:
            return camino, costo
        if nodo not in visitados:
            visitados.add(nodo)
            for vecino, distancia in grafo[nodo].items():
                heapq.heappush(cola_prioridad, (costo + distancia, vecino, camino + [vecino]))
    return None

ruta_ucs, costo_ucs = ucs(grafo, 'A', 'G')
print(ruta_ucs)
print(costo_ucs)
                          