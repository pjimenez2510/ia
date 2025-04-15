import heapq

# f(x) = g(x) + h(x)

# g(x) costo real
# h(x) heuristica

def A(grafo, heuristica, inicio, meta):
    
    heap = [(heuristica[inicio], inicio, [inicio], 0)]
    visitados = set()
    
    while heap:
        h, nodo, camino, c = heapq.heappop(heap)
        
        if nodo in visitados:
            continue
        
        visitados.add(nodo)
        
        if nodo == meta:
            return camino, c
        
        for vecino, costo_arista in grafo[nodo].items():

            if vecino not in visitados:
                nuevo_costo = c + costo_arista
                nueva_heuristica = nuevo_costo + heuristica[vecino]
                
                nuevo_camino = camino + [vecino]
                heapq.heappush(heap, (nueva_heuristica, vecino, nuevo_camino, nuevo_costo))
    
    return None

grafo = {
    'A': {'B': 5, 'C': 10},
    'B': {'A': 5, 'D': 3, 'E': 8},
    'C': {'A': 10, 'F': 7},
    'D': {'B': 3, 'E': 2, 'G': 4},
    'E': {'B': 8, 'D': 2, 'G': 5},
    'F': {'C': 7, 'G': 6},
    'G': {'D': 4, 'E': 5, 'F': 6}
}

heuristica = {'A': 3, 'B': 4, 'C': 2, 'D': 4, 'E': 4, 'F': 5, 'G': 3}

costo, camino = A(grafo, heuristica, 'A', 'G')


print(costo)
print(camino)