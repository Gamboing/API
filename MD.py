"""
REPOSITORIO ÚNICO DE IMPLEMENTACIONES DE MODELOS DE DISEÑO
Incluye todos los patrones y arquitecturas mencionados en el reporte
"""

# ====================
# 1. ARQUITECTURAS
# ====================

# ----- 1.1 Modelo Cliente-Servidor -----
from flask import Flask, jsonify
import requests

def run_client_server_example():
    # Servidor
    server = Flask(__name__)

    @server.route('/api/data', methods=['GET'])
    def get_data():
        return jsonify({"status": "success", "data": [1, 2, 3]})

    # Ejecutar servidor en hilo separado
    from threading import Thread
    server_thread = Thread(target=lambda: server.run(port=5000))
    server_thread.daemon = True
    server_thread.start()

    # Cliente
    response = requests.get('http://localhost:5000/api/data')
    print("\n1.1 Cliente-Servidor:")
    print(response.json())

# ----- 1.2 Arquitectura en Capas -----
class UserRepository:
    def get_by_id(self, id):
        return {"id": id, "name": "María García", "email": "maria@example.com"}

class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    def get_user_info(self, user_id):
        return self.repository.get_by_id(user_id)

class UserController:
    def __init__(self):
        self.service = UserService()
    
    def display_user(self, user_id):
        user = self.service.get_user_info(user_id)
        print(f"\n1.2 Arquitectura en Capas:\nUsuario: {user['name']} - Email: {user['email']}")

# ----- 1.3 Modelo-Vista-Controlador (MVC) -----
class ProductModel:
    def __init__(self):
        self.products = {
            1: {"name": "Laptop", "price": 999.99},
            2: {"name": "Mouse", "price": 19.99}
        }
    
    def get_product(self, product_id):
        return self.products.get(product_id)

class ProductView:
    def show_product(self, product_data):
        if product_data:
            print(f"\n1.3 MVC:\nProducto: {product_data['name']} - Precio: ${product_data['price']}")
        else:
            print("Producto no encontrado")

class ProductController:
    def __init__(self):
        self.model = ProductModel()
        self.view = ProductView()
    
    def show_product_details(self, product_id):
        product = self.model.get_product(product_id)
        self.view.show_product(product)

# ----- 1.4 Microservicios -----
from flask import Flask
def setup_microservices():
    app = Flask(__name__)

    @app.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        return {"id": user_id, "name": "Carlos Mendoza"}

    @app.route('/orders/<int:user_id>', methods=['GET'])
    def get_orders(user_id):
        return {"orders": [{"id": 1, "product": "Book"}]}

    # Ejecutar en puerto diferente
    from threading import Thread
    micro_thread = Thread(target=lambda: app.run(port=5001))
    micro_thread.daemon = True
    micro_thread.start()

# ====================
# 2. PATRONES DE DISEÑO
# ====================

# ----- 2.1 Singleton -----
class AppConfig:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance
    
    def load_config(self):
        self.settings = {"theme": "dark", "language": "es"}

# ----- 2.2 Observer -----
class NewsPublisher:
    def __init__(self):
        self._subscribers = []
    
    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)
    
    def notify_all(self, news):
        for sub in self._subscribers:
            sub.update(news)

class EmailSubscriber:
    def update(self, news):
        print(f"Enviando email: {news}")

class SMSSubscriber:
    def update(self, news):
        print(f"Enviando SMS: {news}")

# ----- 2.3 Strategy -----
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Pagando ${amount} con tarjeta de crédito")

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Pagando ${amount} via PayPal")

class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def execute_payment(self, amount):
        self.strategy.pay(amount)

# ====================
# 3. PRINCIPIOS COMPLEMENTARIOS
# ====================

# ----- 3.1 Diseño de Interfaces -----
from abc import ABC, abstractmethod

class DatabaseConnector(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def execute_query(self, query):
        pass

class MySQLConnector(DatabaseConnector):
    def connect(self):
        print("Conectando a MySQL...")
    
    def execute_query(self, query):
        print(f"Ejecutando en MySQL: {query}")

# ----- 3.2 Diseño de Datos -----
from dataclasses import dataclass
from typing import List

@dataclass
class Product:
    id: int
    name: str
    price: float

class ProductRepository:
    def __init__(self):
        self.products = [
            Product(1, "Monitor", 199.99),
            Product(2, "Teclado", 49.99)
        ]
    
    def get_all(self) -> List[Product]:
        return self.products
    
    def get_by_id(self, product_id: int) -> Product:
        return next((p for p in self.products if p.id == product_id), None)

# ====================
# EJECUCIÓN DE EJEMPLOS
# ====================

if __name__ == "__main__":
    print("=== DEMOSTRACIÓN DE MODELOS DE DISEÑO ===")
    
    # 1. Arquitecturas
    run_client_server_example()
    
    UserController().display_user(101)
    
    ProductController().show_product_details(1)
    ProductController().show_product_details(3)
    
    setup_microservices()
    import time; time.sleep(1)  # Esperar que el servidor inicie
    print("\n1.4 Microservicios:")
    print(requests.get('http://localhost:5001/users/1').json())
    print(requests.get('http://localhost:5001/orders/1').json())
    
    # 2. Patrones de Diseño
    print("\n2.1 Singleton:")
    config1 = AppConfig()
    config2 = AppConfig()
    print(f"Misma instancia: {config1 is config2}")
    print(f"Configuración: {config1.settings}")
    
    print("\n2.2 Observer:")
    publisher = NewsPublisher()
    publisher.subscribe(EmailSubscriber())
    publisher.subscribe(SMSSubscriber())
    publisher.notify_all("Nueva actualización del sistema")
    
    print("\n2.3 Strategy:")
    processor = PaymentProcessor(CreditCardPayment())
    processor.execute_payment(100)
    processor.strategy = PayPalPayment()
    processor.execute_payment(50)
    
    # 3. Principios Complementarios
    print("\n3.1 Diseño de Interfaces:")
    connector = MySQLConnector()
    connector.connect()
    connector.execute_query("SELECT * FROM users")
    
    print("\n3.2 Diseño de Datos:")
    repo = ProductRepository()
    print(repo.get_by_id(1))
    print(repo.get_all())