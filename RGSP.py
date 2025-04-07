from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Cargar dataset
iris = load_iris()
X = iris.data
y = iris.target

# Separar datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

# Crear y entrenar el clasificador
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

# Predicciones
y_pred = knn.predict(X_test)
print("Precisión:", accuracy_score(y_test, y_pred))
