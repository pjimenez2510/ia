import numpy as np #importar numpy como np
import matplotlib.pyplot as plt #importar matplotlib.pyplot como plt
from mpl_toolkits.mplot3d import Axes3D #importar Axes3D para gráficos 3D
# Solución parcial (Hill Climbing)
def hill_climbing(f, x_inicial, generar_vecinos, max_iter=1000):
    x_actual = x_inicial
    for _ in range(max_iter):
        vecinos = generar_vecinos(x_actual)
        x_siguiente = max(vecinos, key=f)
        if f(x_siguiente) <= f(x_actual):
            break  # Óptimo local encontrado
        x_actual = x_siguiente
    return x_actual

def generar_vecinos(xy):
    x, y = xy
    return [(x + dx, y + dy) for dx in [-0.1, 0, 0.1] for dy in [-0.1, 0, 0.1]]

# Definir la función a optimizar
def f(xy):
    return -xy[0]**2 - xy[1]**2 - 3*np.cos(2*xy[0])

solucion = hill_climbing(f=f,
                        x_inicial=(1, 1),
                        generar_vecinos=generar_vecinos)

print("Mínimo encontrado:", solucion)

# Crear el gráfico de la función
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Crear una malla de puntos
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)

# Calcular el valor de la función en cada punto
for i in range(len(x)):
    for j in range(len(y)):
        Z[i, j] = f((X[i, j], Y[i, j]))

# Graficar la superficie
superficie = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)

# Marcar el punto mínimo encontrado
x_min, y_min = solucion
z_min = f(solucion)
ax.scatter([x_min], [y_min], [z_min], color='red', s=100, marker='o', label='Mínimo')

# Añadir etiquetas y título
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('f(x,y)')
ax.set_title('Visualización de la función y el mínimo encontrado')
ax.legend()

# Añadir una barra de color
fig.colorbar(superficie, ax=ax, shrink=0.5, aspect=5)

# Mostrar el gráfico
plt.show()