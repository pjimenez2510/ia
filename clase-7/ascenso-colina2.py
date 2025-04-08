import numpy as np #importar numpy como np
import matplotlib.pyplot as plt #importar matplotlib.pyplot como plt
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

solucion = hill_climbing(f=lambda xy: -xy[0]**2 - xy[1]**2 - 3*np.cos(2*xy[0]),
                        x_inicial=(1, 1),
                        generar_vecinos=generar_vecinos)

print("Mínimo encontrado:", solucion)