from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Crear datos simulados
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

# Aplicar K-means
kmeans = KMeans(n_clusters=3, random_state=0)
kmeans.fit(X)
y_kmeans = kmeans.predict(X)

# Visualización
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='viridis')
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', marker='x', s=200, label='Centroides')
plt.legend()
plt.title("Ejemplo de Agrupamiento con K-means")
plt.show()
