import numpy as np #importar numpy como np
import matplotlib.pyplot as plt #importar matplotlib.pyplot como plt

# Función objetivo (múltiples mínimos locales)
def f(x):
    return np.sin(x) * np.exp(-0.1 * x)

x = np.linspace(0, 20, 100)
plt.plot(x, f(x), label="Función objetivo")

# Ejemplo de Hill Climbing
x_actual = 2.0
trayectoria = [x_actual]
for _ in range(10):
    vecinos = [x_actual + np.random.normal(0, 0.5) for _ in range(5)]
    x_actual = max(vecinos, key=f)
    trayectoria.append(x_actual)

plt.scatter(trayectoria, [f(x) for x in trayectoria], c='red', label="Búsqueda local")
plt.legend()
plt.show()