import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

np.random.seed(42)

tamanio = np.random.randint(50, 250, 50)
habitaciones = np.random.randint(1, 5, 50)

precio = 50000 + (tamanio * 1500) + (habitaciones * 10000) + np.random.randint(-10000, 10000, 50)

datos = pd.DataFrame({'Tamanio (m2)': tamanio, 'Habitaciones': habitaciones, 'Precio ($)': precio})

print(datos)


X = datos[['Tamanio (m2)', 'Habitaciones']]
y = datos['Precio ($)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = LinearRegression()
modelo.fit(X_train, y_train)

print(f"Coeficientes: {modelo.coef_}")
print(f"Intercepto: {modelo.intercept_}")

y_pred = modelo.predict(X_test)

plt.scatter(y_test, y_pred)
plt.xlabel('Precio real')
plt.ylabel('Precio predicho')
plt.title('Comparación entre precio real y precio predicho')
plt.show()

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print(f"Error absoluto medio: {mae}")
print(f"Error cuadrático medio: {mse}")



nueva_casa = np.array([[180, 3]])
prediccion = modelo.predict(nueva_casa)

print(f"Predicción del precio de la nueva casa: {prediccion[0]:.2f} dólares")
