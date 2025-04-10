import pyodbc
import pandas as pd
from datetime import datetime

class SQLDatabaseManager:
    def __init__(self, server='localhost', database='MiBaseDeDatosEjemplo'):
        self.server = server
        self.database = database
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establece conexión con la base de datos SQL Server"""
        try:
            self.conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                'Trusted_Connection=yes;'
            )
            self.cursor = self.conn.cursor()
            print("Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
    
    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
            print("Conexión cerrada")
    
    def create_database(self):
        """Crea la base de datos si no existe"""
        try:
            # Conexión al servidor sin especificar base de datos
            master_conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                'Trusted_Connection=yes;'
            )
            master_cursor = master_conn.cursor()
            
            # Verificar si la base de datos existe
            master_cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{self.database}'")
            if not master_cursor.fetchone():
                master_cursor.execute(f"CREATE DATABASE {self.database}")
                print(f"Base de datos '{self.database}' creada exitosamente")
            else:
                print(f"La base de datos '{self.database}' ya existe")
                
            master_conn.close()
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
    
    def create_tables(self):
        """Crea todas las tablas necesarias"""
        try:
            # Tabla Clientes
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clientes' AND xtype='U')
            CREATE TABLE Clientes (
                ClienteID INT PRIMARY KEY IDENTITY(1,1),
                Nombre NVARCHAR(100) NOT NULL,
                Apellido NVARCHAR(100) NOT NULL,
                Email NVARCHAR(100) UNIQUE,
                FechaNacimiento DATE,
                Telefono NVARCHAR(20),
                FechaRegistro DATETIME DEFAULT GETDATE(),
                Activo BIT DEFAULT 1
            )
            """)
            
            # Tabla Productos
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Productos' AND xtype='U')
            CREATE TABLE Productos (
                ProductoID INT PRIMARY KEY IDENTITY(1,1),
                Nombre NVARCHAR(100) NOT NULL,
                Descripcion NVARCHAR(500),
                Precio DECIMAL(10, 2) NOT NULL,
                Stock INT NOT NULL DEFAULT 0,
                Categoria NVARCHAR(50),
                FechaCreacion DATETIME DEFAULT GETDATE()
            )
            """)
            
            # Tabla Pedidos
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Pedidos' AND xtype='U')
            CREATE TABLE Pedidos (
                PedidoID INT PRIMARY KEY IDENTITY(1,1),
                ClienteID INT NOT NULL,
                FechaPedido DATETIME DEFAULT GETDATE(),
                Estado NVARCHAR(20) DEFAULT 'Pendiente',
                Total DECIMAL(10, 2),
                FOREIGN KEY (ClienteID) REFERENCES Clientes(ClienteID)
            )
            """)
            
            # Tabla DetallesPedido
            self.cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='DetallesPedido' AND xtype='U')
            CREATE TABLE DetallesPedido (
                DetalleID INT PRIMARY KEY IDENTITY(1,1),
                PedidoID INT NOT NULL,
                ProductoID INT NOT NULL,
                Cantidad INT NOT NULL,
                PrecioUnitario DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (PedidoID) REFERENCES Pedidos(PedidoID),
                FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
            )
            """)
            
            self.conn.commit()
            print("Tablas creadas exitosamente")
        except Exception as e:
            print(f"Error al crear tablas: {e}")
            self.conn.rollback()
    
    def insert_sample_data(self):
        """Inserta datos de ejemplo en las tablas"""
        try:
            # Insertar clientes
            clientes = [
                ('Juan', 'Pérez', 'juan.perez@email.com', '1985-05-15', '555-1234'),
                ('María', 'Gómez', 'maria.gomez@email.com', '1990-08-22', '555-5678'),
                ('Carlos', 'López', 'carlos.lopez@email.com', '1978-11-30', '555-9012')
            ]
            
            self.cursor.executemany("""
            INSERT INTO Clientes (Nombre, Apellido, Email, FechaNacimiento, Telefono)
            VALUES (?, ?, ?, ?, ?)
            """, clientes)
            
            # Insertar productos
            productos = [
                ('Laptop', 'Laptop de 15 pulgadas, 16GB RAM', 1200.00, 50, 'Electrónicos'),
                ('Teléfono', 'Teléfono inteligente 128GB', 800.00, 100, 'Electrónicos'),
                ('Libro', 'Libro de programación en Python', 45.00, 200, 'Libros')
            ]
            
            self.cursor.executemany("""
            INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
            VALUES (?, ?, ?, ?, ?)
            """, productos)
            
            self.conn.commit()
            print("Datos de ejemplo insertados correctamente")
        except Exception as e:
            print(f"Error al insertar datos: {e}")
            self.conn.rollback()
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta y devuelve los resultados"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            # Para consultas SELECT, devolver los resultados
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in self.cursor.description]
                results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
                return results
            else:
                self.conn.commit()
                return {"message": "Operación ejecutada correctamente"}
        except Exception as e:
            print(f"Error en la consulta: {e}")
            self.conn.rollback()
            return {"error": str(e)}
    
    def get_clientes(self):
        """Obtiene todos los clientes"""
        return self.execute_query("SELECT * FROM Clientes")
    
    def get_productos(self):
        """Obtiene todos los productos"""
        return self.execute_query("SELECT * FROM Productos")
    
    def add_cliente(self, nombre, apellido, email=None, fecha_nacimiento=None, telefono=None):
        """Añade un nuevo cliente"""
        query = """
        INSERT INTO Clientes (Nombre, Apellido, Email, FechaNacimiento, Telefono)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (nombre, apellido, email, fecha_nacimiento, telefono)
        return self.execute_query(query, params)
    
    def update_producto_precio(self, producto_id, nuevo_precio):
        """Actualiza el precio de un producto"""
        query = "UPDATE Productos SET Precio = ? WHERE ProductoID = ?"
        params = (nuevo_precio, producto_id)
        return self.execute_query(query, params)
    
    def delete_cliente(self, cliente_id):
        """Elimina un cliente"""
        query = "DELETE FROM Clientes WHERE ClienteID = ?"
        params = (cliente_id,)
        return self.execute_query(query, params)
    
    def get_productos_por_categoria(self, categoria):
        """Obtiene productos por categoría"""
        query = "SELECT * FROM Productos WHERE Categoria = ?"
        params = (categoria,)
        return self.execute_query(query, params)
    
    def get_clientes_con_pedidos(self):
        """Obtiene clientes que han realizado pedidos"""
        query = """
        SELECT c.ClienteID, c.Nombre, c.Apellido, COUNT(p.PedidoID) as TotalPedidos
        FROM Clientes c
        LEFT JOIN Pedidos p ON c.ClienteID = p.ClienteID
        GROUP BY c.ClienteID, c.Nombre, c.Apellido
        HAVING COUNT(p.PedidoID) > 0
        """
        return self.execute_query(query)
    
    def generar_informe_ventas(self):
        """Genera un informe de ventas por categoría"""
        query = """
        SELECT 
            p.Categoria,
            COUNT(dp.DetalleID) as VentasTotales,
            SUM(dp.Cantidad * dp.PrecioUnitario) as IngresosTotales
        FROM DetallesPedido dp
        JOIN Productos p ON dp.ProductoID = p.ProductoID
        GROUP BY p.Categoria
        ORDER BY IngresosTotales DESC
        """
        return self.execute_query(query)

if __name__ == "__main__":
    # Configuración inicial
    db_manager = SQLDatabaseManager(server='localhost\\SQLEXPRESS')
    
    try:
        # Paso 1: Crear la base de datos
        db_manager.create_database()
        
        # Paso 2: Conectar a la base de datos
        db_manager.connect()
        
        # Paso 3: Crear tablas
        db_manager.create_tables()
        
        # Paso 4: Insertar datos de ejemplo
        db_manager.insert_sample_data()
        
        # Ejemplos de operaciones
        
        # 1. Obtener todos los clientes
        print("\nClientes:")
        clientes = db_manager.get_clientes()
        for cliente in clientes:
            print(cliente)
        
        # 2. Obtener productos electrónicos
        print("\nProductos electrónicos:")
        productos = db_manager.get_productos_por_categoria('Electrónicos')
        for producto in productos:
            print(producto)
        
        # 3. Añadir un nuevo cliente
        print("\nAñadiendo nuevo cliente...")
        db_manager.add_cliente('Ana', 'Martínez', 'ana.martinez@email.com', '1992-04-15', '555-4321')
        
        # 4. Actualizar precio de producto
        print("\nActualizando precio de producto...")
        db_manager.update_producto_precio(1, 1250.00)
        
        # 5. Generar informe de ventas
        print("\nInforme de ventas:")
        informe = db_manager.generar_informe_ventas()
        for item in informe:
            print(item)
        
        # 6. Ejemplo de consulta personalizada
        print("\nClientes con pedidos:")
        clientes_pedidos = db_manager.get_clientes_con_pedidos()
        for cliente in clientes_pedidos:
            print(cliente)
            
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
    finally:
        # Cerrar conexión
        db_manager.close()