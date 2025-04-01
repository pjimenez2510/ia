import networkx as nx
import matplotlib.pyplot as plt

grafo = {
    'A': {'B': 5, 'C': 10},
    'B': {'A': 5, 'D': 3, 'E': 8},
    'C': {'A': 10, 'F': 7},
    'D': {'B': 3, 'E': 2, 'G': 4},
    'E': {'B': 8, 'D': 2, 'G': 5},
    'F': {'C': 7, 'G': 6},
    'G': {'D': 4, 'E': 5, 'F': 6}
}

# Crear un grafo dirigido con pesos
G = nx.DiGraph()

# Agregar aristas con pesos
for nodo_origen, destinos in grafo.items():
    for nodo_destino, peso in destinos.items():
        G.add_edge(nodo_origen, nodo_destino, weight=peso)

# Configurar el diseño del grafo
pos = nx.spring_layout(G, seed=42)  # Para obtener un diseño reproducible

# Dibujar nodos
plt.figure(figsize=(10, 8))
nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')

# Dibujar etiquetas de nodos
nx.draw_networkx_labels(G, pos, font_size=20, font_weight='bold')

# Dibujar aristas
nx.draw_networkx_edges(G, pos, width=2, arrowsize=20, alpha=0.7, 
                     edge_color='gray')

# Dibujar pesos de aristas
edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=16)

# Remover ejes
plt.axis('off')

# Añadir título
plt.title('Visualización del Grafo con Pesos', fontsize=16)

# Mostrar el gráfico
plt.tight_layout()
plt.show()