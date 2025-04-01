import networkx as nx 
import matplotlib.pyplot as plt 

G = nx.Graph()
estudiantes = ['Juan', 'Maria' ]
asignaturas = ['Matematica', 'Programacion' ]
evaluaciones = ['Evaluacion Matematica','Evaluacion Programacion']
profesores = ['Ing. Ana Garcia' ]

G.add_node('Juan', tipo='estudiante', color='blue')
G.add_node('Maria', tipo='estudiante', color='blue')
G.add_node('Matematica', tipo='asignatura', color='green')
G.add_node('Programacion', tipo='asignatura', color='green')
G.add_node('Evaluacion Matematica', tipo='evaluacion', color='yellow')
G.add_node('Evaluacion Programacion', tipo='evaluacion', color='yellow')
G.add_node('Ing. Ana Garcia', tipo='profesor', color='red')

G.add_edge('Juan', 'Matematica', tipo_relacion='Inscripto en') 
G.add_edge('Juan', 'Programacion', tipo_relacion='Inscripto en')
G.add_edge('Maria', 'Matematica', tipo_relacion='Inscripto en')
G.add_edge('Juan', 'Evaluacion Matematica', tipo_relacion='Tiene como evaluacion')
G.add_edge('Maria', 'Evaluacion Matematica', tipo_relacion='Tiene como evaluacion')
G.add_edge('Juan', 'Evaluacion Programacion', tipo_relacion='Tiene como evaluacion')
G.add_edge('Matematica', 'Evaluacion Matematica', tipo_relacion='evalua con')
G.add_edge('Programacion', 'Evaluacion Programacion', tipo_relacion='evalua con')
G.add_edge('Ing. Ana Garcia', 'Matematica', tipo_relacion='enseña')
G.add_edge('Ing. Ana Garcia', 'Programacion', tipo_relacion='enseña')


plt.figure(figsize=(10, 8))
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2500, font_size=10, node_shape='s')
plt.show()

