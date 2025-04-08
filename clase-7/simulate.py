import math
import random

def simulated_annealing(f, x_inicial, generar_vecino, temp_inicial=1000, enfriamiento=0.95):
   x_actual = x_inicial
   temp = temp_inicial
   while temp > 1e-3:
       x_vecino = generar_vecino(x_actual)
       delta = f(x_vecino) - f(x_actual)
       if delta > 0 or random.random() < math.exp(delta / temp):
           x_actual = x_vecino
       temp *= enfriamiento
   return x_actual


import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

# Coordenadas (x,y) del almacén y los puntos de entrega
ubicaciones = {
    'Almacén': (0, 0),
    'A': (2, 3),
    'B': (5, 1),
    'C': (4, 4),
    'D': (1, 5),
    'E': (6, 2)
}

# Matriz de distancias entre puntos
distancias = {
    ('Almacén', 'A'): 3.6,
    ('Almacén', 'B'): 5.1,
    ('A', 'B'): 3.6,
    ('A', 'D'): 2.2,
    ('B', 'C'): 3.2,
    ('B', 'E'): 1.4,
    ('C', 'D'): 3.6,
    ('C', 'E'): 2.8,
    ('D', 'E'): 5.4
}

#Calcula la longitud de una ruta completa:
def calcular_costo(ruta):
    costo = 0
    for i in range(len(ruta)-1):
        par = (ruta[i], ruta[i+1])
        costo += distancias.get(par,
                              distancias.get(par[::-1], 0))
    # Agregar regreso al almacén
    costo += distancias.get((ruta[-1], 'Almacén'),
                          distancias.get(('Almacén', ruta[-1]), 0))
    return costo

def generar_vecino(ruta_actual):
  ruta = ruta_actual.copy()
  i, j = np.random.choice(len(ruta)), np.random.choice(len(ruta))
  ruta[i], ruta[j] = ruta[j], ruta[i]
  return ruta

def recocido_simulado(ruta_inicial, temp_inicial=1000, 
                      enfriamiento=0.95, iteraciones=1000):
    ruta_actual = ruta_inicial
    costo_actual = calcular_costo(ruta_actual)
    mejor_ruta = ruta_actual.copy()
    mejor_costo = costo_actual
    
    temp = temp_inicial
    historial_costos = []
    
    for _ in range(iteraciones):
        ruta_vecina = generar_vecino(ruta_actual)
        costo_vecino = calcular_costo(ruta_vecina)
        delta = costo_vecino - costo_actual
        
        if delta < 0 or np.random.random() < np.exp(-delta / temp):
            ruta_actual, costo_actual = ruta_vecina, costo_vecino
            
        if costo_actual < mejor_costo:
            mejor_ruta, mejor_costo = ruta_actual.copy(), costo_actual
            
        historial_costos.append(costo_actual)
        temp *= enfriamiento
        
    return mejor_ruta, mejor_costo, historial_costos


# Ruta inicial aleatoria
ruta_inicial = ['A', 'B', 'C', 'D', 'E']
np.random.shuffle(ruta_inicial)

# Ejecutar algoritmo
ruta_optima, distancia, historial = recocido_simulado(ruta_inicial)

print(f"Ruta óptima: Almacén → {' → '.join(ruta_optima)} → Almacén")
print(f"Distancia total: {distancia:.1f} km")

# Visualización
plt.figure(figsize=(10, 5))
plt.plot(historial, 'b-', linewidth=0.5)
plt.title("Evolución del Costo en el Recocido Simulado")
plt.xlabel("Iteración")
plt.ylabel("Distancia (km)")
plt.grid(True)
plt.show()


plt.figure(figsize=(8, 8))

for punto, (x, y) in ubicaciones.items():
    plt.scatter(x, y, s=200, label=punto)
    plt.text(x, y + 0.2, punto, fontsize=12, ha='center')
    
# Dibuja la ruta óptima
ruta_optima = ['Almacén'] + ruta_optima + ['Almacén']

for i in range(len(ruta_optima)-1):
    x1, y1 = ubicaciones[ruta_optima[i]]
    x2, y2 = ubicaciones[ruta_optima[i+1]]
    plt.plot([x1, x2], [y1, y2], 'r-', linewidth=2)

plt.title("Ruta Óptima")
plt.xlabel("Coordenada X")
plt.ylabel("Coordenada Y")
plt.grid(True)
plt.legend()
plt.show()