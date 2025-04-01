import heapq

def greedy_search(laberinto, inicio, meta, heuristica):
    filas, cols = len(laberinto), len(laberinto[0])
    heap = [(heuristica(inicio, meta), inicio[0], inicio[1], [])]
    visitados = set([inicio])
    
    while heap:
        _, fila, col, camino = heapq.heappop(heap)
        
        if (fila, col) == meta:
            return camino + [(fila, col)]
        
        for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nf, nc = fila + df, col + dc
            if 0 <= nf < filas and \
               0 <= nc < cols and \
               laberinto[nf][nc] != 1 and \
               (nf, nc) not in visitados:
                visitados.add((nf, nc))
                heapq.heappush(heap, (heuristica((nf, nc), meta),
                               nf, nc, camino + [(fila, col)]))
    
    return None

# Heurística: Distancia Manhattan
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Uso:
laberinto = [
    ["S", 0, 0, 1],
    [1, 0, 1, 0],
    [1, 0, 0, "G"]
]

solucion = greedy_search(laberinto, (0, 0), (2, 3), manhattan)
print("Camino (Voraz):", solucion)