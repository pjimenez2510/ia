
laberinto = [["S", 0, 0, 1 ],[1, 0, 1, 0 ],[1, 0, 0, "G" ]]

from collections import deque

def bfs(laberinto, inicio, meta):
    filas, columnas = len(laberinto), len(laberinto[0])
    cola = deque([(inicio[0], inicio[1], [])])
    visitados = set([(inicio[0], inicio[1])])
    
    while cola:
        fila, col, camino = cola.popleft()
        
        if laberinto[fila][col] == "G":
            return camino + [(fila, col)]
        
        for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nf, nc = fila + df, col + dc
            
            if 0 <= nf < filas and 0 <= nc < columnas and laberinto[nf][nc] != 1 and (nf, nc) not in visitados:
                visitados.add((nf, nc))
                cola.append((nf, nc, camino + [(fila, col)]))
    return None

inicio = (0, 0)
meta = (2, 3)

camino = bfs(laberinto, inicio, meta)
print(camino)
                
                