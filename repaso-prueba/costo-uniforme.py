import heapq

def ucs(grafo, inicio, meta):
    
    heap = [(0, inicio, [inicio])]
    visitados = set()
    
    while heap:
        costo, nodo, camino = heapq.heappop(heap)
        
        if nodo in visitados:
            continue
        
        visitados.add(nodo)
        
        if nodo == meta:
            return costo, camino
        
        for vecino, costo_arista in grafo[nodo].items():

            if vecino not in visitados:
                nuevo_costo = costo + costo_arista
                nuevo_camino = camino + [vecino]
                heapq.heappush(heap, (nuevo_costo, vecino, nuevo_camino))
    
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

costo, camino = ucs(grafo, 'A', 'G')

print(costo)
print(camino)