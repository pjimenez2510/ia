from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

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

# Definir el grafo
grafo = {
    "Patricio": ["Pablo", "Jair", "Emilia", "Joshua", "Andrea"],
    "Pablo": ["Patricio", "Jair", "Emilia", "Andrea" ],
    "Jair": ["Patricio", "Emilia", "Joshua"],
    "Emilia": ["Patricio", "Pablo", "Jair", "Joshua", "Andrea"],
    "Joshua": ["Patricio", "Pablo", "Jair", "Emilia"],
    "Andrea": ["Patricio", "Emilia"  ]
}

inicio = "Jair"
objetivo = "Andrea"
camino = bfs_social(grafo, inicio, objetivo)

# Crear el gráfico
G = nx.Graph()
for nodo, vecinos in grafo.items():
    for vecino in vecinos:
        G.add_edge(nodo, vecino)

# Configurar colores
color_nodos = ["red" if nodo in camino else "lightblue" for nodo in G.nodes()]
color_aristas = ["red" if (camino[i], camino[i+1]) in G.edges() or (camino[i+1], camino[i]) in G.edges() else "black" 
                 for i in range(len(camino)-1)]

# Dibujar el grafo
pos = nx.spring_layout(G, seed=12)  # Posiciones consistentes
nx.draw(G, pos, with_labels=True, node_color=color_nodos, font_weight='bold', 
        edge_color='gray', width=1.5, node_size=2000)

# Resaltar la ruta
nx.draw_networkx_edges(G, pos, edgelist=[(camino[i], camino[i+1]) for i in range(len(camino)-1)],
                       edge_color="red", width=3)

plt.title("Ruta más corta entre Alice y George\nGrados de separación: 3")
plt.show()