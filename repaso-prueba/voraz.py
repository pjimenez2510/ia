import heapq

def voraz(grafo, heuristica, inicio, meta):
    
    heap = [(heuristica[inicio], inicio, [inicio])]
    visitados = set()
    
    while heap:
        h, nodo, camino = heapq.heappop(heap)
        
        if nodo in visitados:
            continue
        
        visitados.add(nodo)
        
        if nodo == meta:
            return h, camino
        
        for vecino in grafo[nodo]:

            if vecino not in visitados:
                
                nuevo_camino = camino + [vecino]
                heapq.heappush(heap, (heuristica[vecino], vecino, nuevo_camino))
    
    return None

grafo = {
    'A': {'B', 'C'},
    'B': {'A', 'D', 'E'},
    'C': {'A', 'F'},
    'D': {'B', 'E', 'G'},
    'E': {'B', 'D', 'G'},
    'F': {'C', 'G'},
    'G': {'D', 'E', 'F'}
}

heuristica = {'A': 3, 'B': 4, 'C': 2, 'D': 4, 'E': 4, 'F': 5, 'G': 3}

costo, camino = voraz(grafo, heuristica, 'A', 'G')

print(costo)
print(camino)