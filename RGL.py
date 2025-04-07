from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
import matplotlib.pyplot as plt

# Generar datos de ejemplo
X, y = make_regression(n_samples=100, n_features=1, noise=10, random_state=1)

# Crear el modelo y entrenarlo
model = LinearRegression()
model.fit(X, y)

# Predicciones
y_pred = model.predict(X)

# Visualización
plt.scatter(X, y, color='blue')
plt.plot(X, y_pred, color='red')
plt.title("Ejemplo de Regresión Lineal")
plt.show()
