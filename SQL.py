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
            # Verificar drivers disponibles
            available_drivers = pyodbc.drivers()
            if not any('ODBC Driver 17 for SQL Server' in driver for driver in available_drivers):
                print("❌ Error: El driver 'ODBC Driver 17 for SQL Server' no está instalado.")
                print("Drivers disponibles:", available_drivers)
                print("Descárgalo desde: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server")
                return False
                
            connection_string = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                'Trusted_Connection=yes;'
            )
            
            print(f"🔗 Intentando conectar con: {connection_string}")
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("✅ Conexión exitosa a la base de datos")
            return True
            
        except pyodbc.Error as e:
            print("❌ Error al conectar a la base de datos:")
            print("Código:", e.args[0])
            print("Mensaje:", e.args[1])
            self.conn = None
            self.cursor = None
            return False
    
    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
            print("🔌 Conexión cerrada")
    
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
                print(f"🆕 Base de datos '{self.database}' creada exitosamente")
            else:
                print(f"ℹ️ La base de datos '{self.database}' ya existe")
                
            master_conn.close()
            return True
        except pyodbc.Error as e:
            print(f"❌ Error al crear la base de datos: {e.args[1]}")
            return False
    
    def check_connection(self):
        """Verifica si hay una conexión activa"""
        if not self.cursor:
            print("⚠️ No hay conexión activa a la base de datos")
            return False
        return True
    
    def create_tables(self):
        """Crea todas las tablas necesarias"""
        if not self.check_connection():
            return False
            
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
            print("✅ Tablas creadas exitosamente")
            return True
        except pyodbc.Error as e:
            print(f"❌ Error al crear tablas: {e.args[1]}")
            self.conn.rollback()
            return False
    
    def insert_sample_data(self):
        """Inserta datos de ejemplo en las tablas"""
        if not self.check_connection():
            return False
            
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
            print("✅ Datos de ejemplo insertados correctamente")
            return True
        except pyodbc.Error as e:
            print(f"❌ Error al insertar datos: {e.args[1]}")
            self.conn.rollback()
            return False
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta y devuelve los resultados"""
        if not self.check_connection():
            return None
            
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
                return {"status": "success", "message": "Operación ejecutada correctamente"}
        except pyodbc.Error as e:
            print(f"❌ Error en la consulta: {e.args[1]}")
            self.conn.rollback()
            return {"status": "error", "message": str(e.args[1])}

    # Resto de los métodos permanecen igual...
    # (get_clientes, get_productos, add_cliente, etc.)

if __name__ == "__main__":
    print("🚀 Iniciando demostración de SQL con Python")
    
    # Configuración - cambia esto según tu entorno
    server_name = 'localhost\\SQLEXPRESS'  # Para SQL Server Express
    # server_name = 'localhost'           # Para SQL Server estándar
    
    db_manager = SQLDatabaseManager(server=server_name)
    
    try:
        # Paso 1: Crear la base de datos
        if not db_manager.create_database():
            print("No se pudo crear la base de datos. Saliendo...")
            exit(1)
        
        # Paso 2: Conectar a la base de datos
        if not db_manager.connect():
            print("No se pudo conectar a la base de datos. Saliendo...")
            exit(1)
        
        # Paso 3: Crear tablas
        if not db_manager.create_tables():
            print("No se pudieron crear las tablas. Saliendo...")
            exit(1)
        
        # Paso 4: Insertar datos de ejemplo
        if not db_manager.insert_sample_data():
            print("No se pudieron insertar datos de ejemplo. Continuando con demostración...")
        
        # Demostración de operaciones
        
        print("\n📋 Listado de clientes:")
        clientes = db_manager.execute_query("SELECT * FROM Clientes")
        for cliente in clientes:
            print(f"{cliente['ClienteID']}: {cliente['Nombre']} {cliente['Apellido']}")
        
        print("\n📋 Productos electrónicos:")
        productos = db_manager.execute_query("SELECT * FROM Productos WHERE Categoria = ?", ('Electrónicos',))
        for producto in productos:
            print(f"{producto['ProductoID']}: {producto['Nombre']} - ${producto['Precio']}")
        
        print("\n➕ Añadiendo nuevo cliente...")
        resultado = db_manager.execute_query(
            "INSERT INTO Clientes (Nombre, Apellido, Email) VALUES (?, ?, ?)",
            ('Ana', 'Martínez', 'ana.martinez@email.com')
        )
        print("Resultado:", resultado)
        
        print("\n🔄 Actualizando precio de producto...")
        resultado = db_manager.execute_query(
            "UPDATE Productos SET Precio = ? WHERE ProductoID = ?",
            (1250.00, 1)
        )
        print("Resultado:", resultado)
        
        print("\n📊 Informe de productos:")
        informe = db_manager.execute_query("""
            SELECT Categoria, COUNT(*) as Cantidad, AVG(Precio) as PrecioPromedio
            FROM Productos
            GROUP BY Categoria
        """)
        for item in informe:
            print(f"{item['Categoria']}: {item['Cantidad']} productos, precio promedio ${item['PrecioPromedio']:.2f}")
            
    except KeyboardInterrupt:
        print("\n🛑 Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
    finally:
        # Cerrar conexión
        db_manager.close()
        print("\n🏁 Demostración completada")
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