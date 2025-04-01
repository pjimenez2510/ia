import networkx as nx 
import matplotlib.pyplot as plt 

G = nx.Graph()
profesiones = ['Ingeniero', 'Doctor', 'Programador', 'Cientifico de Datos', 'Dontologo']
habilidades = ['Matemáticas', 'Programación', 'Análisis de Datos', 'Medicina' ]

G.add_nodes_from(profesiones, color='blue')
G.add_nodes_from(habilidades, color='green')

G.add_edges_from([('Ingeniero', 'Matemáticas'), 
                  ('Doctor', 'Medicina'), 
                  ('Programador', 'Programación'), 
                  ('Cientifico de Datos', 'Análisis de Datos'), 
                  ('Cientifico de Datos', 'Matemáticas'), 
                  ('Doctor', 'Análisis de Datos'),
                  ('Análisis de Datos', 'Matemáticas'),
                  ('Programación', 'Matemáticas'),
                  ('Dontologo', 'Medicina'),
                  ])

plt.figure(figsize=(10, 8))
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10)
plt.show()


