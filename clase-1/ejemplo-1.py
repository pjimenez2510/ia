import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

 
X = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
y = np.array([2, 4, 6, 8, 10, 12])

plt.scatter(X, y)
plt.xlabel('X')
plt.ylabel('y')
plt.title('Datos de ejemplo')
plt.show()

modelo = LinearRegression()
modelo.fit(X, y)

y_pred = modelo.predict(X)

nueva_x = np.array([7]).reshape(-1, 1)
prediccion = modelo.predict(nueva_x)

print(f"Predicción para x=7: {prediccion[0]}")
