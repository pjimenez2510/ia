
from collections import deque

def bfs_social(grafo, inicio, objetivo):
    cola = deque()
    cola.append((inicio, [inicio]))
    visitados = set()
    visitados.add(inicio)

    while cola:
        usuario_actual, camino = cola.popleft()

        if usuario_actual == objetivo:
            return camino
        
        for amigo in grafo.get(usuario_actual, []):
            if amigo not in visitados:
                visitados.add(amigo)
                cola.append((amigo, camino + [amigo]))

    return None

grafo = {
    "Alice": ["Bob", "Charlie"],
    "Bob": ["Alice", "David", "Eve"],
    "Charlie": ["Alice", "Frank"],
    "David": ["Bob"],
    "Eve": ["Bob", "Frank"],
    "Frank": ["Charlie", "Eve", "George"],
    "George": ["Frank"]
}

inicio = "Alice"
objetivo = "George"

camino = bfs_social(grafo, inicio, objetivo)

if camino:
    print(f"Ruta de conexion mas corta: {inicio} y {objetivo}")
    print(" -> ".join(camino))
    print(f"Grados de separación: {len(camino) - 1}")
else:
    print("No se encontró un camino")


