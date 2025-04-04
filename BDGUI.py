import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import time
import numpy as np
import logging
from PIL import Image, ImageTk, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import sqlite3
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de estilo para matplotlib
style.use('dark_background')

class ModeloCohete:
    def __init__(self):
        self._initialize_parameters()
        self._initialize_environment()
        self._initialize_systems()
        self._initialize_pid()
        self._initialize_data()
        
    def _initialize_parameters(self):
        """Inicializa los parámetros físicos del cohete"""
        self.altitud = 1000  # Altitud inicial en metros
        self.velocidad = -50  # Velocidad inicial en m/s (descenso)
        self.orientacion = 0  # Orientación en grados
        self.aceleracion = 0  # Aceleración en m/s²
        
    def _initialize_environment(self):
        """Inicializa los parámetros ambientales"""
        self.temperatura = 150  # Temperatura en °C
        self.combustible = 100  # Porcentaje de combustible
        self.presion = 1.0  # Presión atmosférica
        self.humedad = 30  # Humedad relativa
        self.viento = random.uniform(0, 10)  # Velocidad del viento
        self.direccion_viento = random.uniform(0, 360)  # Dirección del viento
        
    def _initialize_systems(self):
        """Inicializa el estado de los sistemas"""
        self.estado_propulsores = False
        self.tren_desplegado = False
        self.mision_abortada = False
        self.potencia_propulsores = 0  # 0-100%
        
    def _initialize_pid(self):
        """Inicializa los parámetros del control PID"""
        self.Kp = 0.5  # Ganancia proporcional
        self.Ki = 0.1  # Ganancia integral
        self.Kd = 0.2  # Ganancia derivativa
        self.error_integral = 0
        self.error_anterior = 0
        self.altitud_objetivo = 0  # Objetivo de aterrizaje
        
    def _initialize_data(self):
        """Inicializa las estructuras de datos"""
        self.telemetria = []
        self.tiempo_inicio = time.time()
        self.pid_history = []
        self.alertas = []
        self._add_initial_alerts()
        
    def _add_initial_alerts(self):
        """Añade alertas iniciales del sistema"""
        self.alertas.append(("Sistema: Todos los sistemas nominales", False))
        self.alertas.append(("Comunicación: Enlace estable con la base", False))
        self.alertas.append(("Navegación: GPS con 8 satélites", False))
        
    def actualizar_datos(self):
        """Actualiza todos los parámetros del modelo"""
        if not self.mision_abortada:
            self._update_pid_control()
            self._update_physics()
            self._update_environment()
            self._check_alerts()
            self._record_telemetry()
            
        return self._get_current_data()
    
    def _update_pid_control(self):
        """Calcula y aplica el control PID"""
        error = self.altitud - self.altitud_objetivo
        self.error_integral += error
        error_derivativo = error - self.error_anterior
        self.error_anterior = error
        
        salida_pid = (self.Kp * error + 
                     self.Ki * self.error_integral + 
                     self.Kd * error_derivativo)
        
        if self.estado_propulsores and self.combustible > 0:
            self.potencia_propulsores = max(0, min(100, salida_pid * 10))
            self.aceleracion = self.potencia_propulsores / 10
        else:
            self.aceleracion = 0
    
    def _update_physics(self):
        """Actualiza los parámetros físicos del cohete"""
        dt = 0.1  # Paso de tiempo simulado
        
        # Actualizar velocidad con aceleración, gravedad y efectos aleatorios
        self.velocidad += (self.aceleracion - 9.81) * dt
        self.velocidad += random.uniform(-2, 2)  # Ruido aleatorio
        self.velocidad += self.viento * 0.1 * math.sin(math.radians(self.direccion_viento))
        
        # Actualizar altitud y orientación
        self.altitud = max(0, self.altitud + self.velocidad * dt)
        self.orientacion = (self.orientacion + random.uniform(-1, 1)) % 360
        
        # Efecto de los propulsores en combustible y temperatura
        if self.estado_propulsores and self.combustible > 0:
            self.combustible -= self.potencia_propulsores * 0.005
            self.temperatura += self.potencia_propulsores * 0.05
    
    def _update_environment(self):
        """Actualiza los parámetros ambientales"""
        # Variación aleatoria de temperatura
        self.temperatura += random.uniform(-0.5, 0.5)
        self.temperatura = max(20, min(self.temperatura, 300))
        
        # Modelar presión atmosférica (simplificado)
        self.presion = 1.0 * math.exp(-self.altitud / 8500)
        
        # Modelar humedad (aumenta cerca del suelo)
        self.humedad = 30 + (1000 - min(self.altitud, 1000)) / 10
        
        # Cambiar velocidad y dirección del viento
        self.viento += random.uniform(-1, 1)
        self.viento = max(0, min(self.viento, 20))
        self.direccion_viento = (self.direccion_viento + random.uniform(-5, 5)) % 360
    
    def _check_alerts(self):
        """Genera alertas según las condiciones actuales"""
        if self.altitud < 10 and self.velocidad < -15:
            self.alertas.append(("ALERTA: Velocidad de descenso peligrosa!", True))
        if self.combustible < 10:
            self.alertas.append(("ALERTA: Combustible crítico!", True))
        if self.temperatura > 250:
            self.alertas.append(("ALERTA: Temperatura crítica!", True))
    
    def _record_telemetry(self):
        """Registra los datos de telemetría"""
        tiempo_actual = time.time() - self.tiempo_inicio
        
        self.telemetria.append({
            'tiempo': tiempo_actual,
            'altitud': self.altitud,
            'velocidad': self.velocidad,
            'orientacion': self.orientacion,
            'temperatura': self.temperatura,
            'aceleracion': self.aceleracion,
            'presion': self.presion
        })
        
        self.pid_history.append({
            'tiempo': tiempo_actual,
            'error': self.error_anterior,
            'salida_pid': (self.Kp * self.error_anterior + 
                          self.Ki * self.error_integral + 
                          self.Kd * (self.error_anterior - self.error_integral)),
            'potencia': self.potencia_propulsores
        })
        
        # Limitar tamaño de datos históricos para evitar uso excesivo de memoria
        if len(self.telemetria) > 500:
            self.telemetria = self.telemetria[-250:]
        if len(self.pid_history) > 500:
            self.pid_history = self.pid_history[-250:]
        if len(self.alertas) > 20:
            self.alertas = self.alertas[-10:]
    
    def _get_current_data(self):
        """Devuelve un diccionario con los datos actuales del modelo"""
        return {
            'altitud': self.altitud,
            'velocidad': self.velocidad,
            'orientacion': self.orientacion,
            'temperatura': self.temperatura,
            'combustible': self.combustible,
            'presion': self.presion,
            'humedad': self.humedad,
            'viento': self.viento,
            'direccion_viento': self.direccion_viento,
            'aceleracion': self.aceleracion,
            'propulsores': self.estado_propulsores,
            'potencia': self.potencia_propulsores,
            'tren': self.tren_desplegado,
            'abortado': self.mision_abortada,
            'pid': {
                'Kp': self.Kp,
                'Ki': self.Ki,
                'Kd': self.Kd,
                'error': self.error_anterior,
                'salida': (self.Kp * self.error_anterior + 
                          self.Ki * self.error_integral + 
                          self.Kd * (self.error_anterior - self.error_integral)) 
                          if not self.mision_abortada else 0
            },
            'alertas': self.alertas,
            'tiempo_inicio': self.tiempo_inicio
        }
    
    def activar_propulsores(self, estado):
        """Activa o desactiva los propulsores"""
        self.estado_propulsores = estado
        self.alertas.append((f"Propulsores {'activados' if estado else 'desactivados'}", False))
        
    def ajustar_potencia(self, potencia):
        """Ajusta la potencia de los propulsores"""
        try:
            self.potencia_propulsores = float(potencia)
        except (ValueError, TypeError):
            logger.error(f"Valor de potencia no válido: {potencia}")
            self.alertas.append(("Error: Valor de potencia no válido", True))
        
    def desplegar_tren(self):
        """Intenta desplegar el tren de aterrizaje"""
        if self.altitud < 100 and not self.tren_desplegado:
            self.tren_desplegado = True
            self.alertas.append(("Tren de aterrizaje desplegado", True))
            return True
        
        self.alertas.append(("No se puede desplegar el tren a esta altitud", False))
        return False
        
    def abortar_mision(self):
        """Inicia la secuencia de aborto de misión"""
        self.mision_abortada = True
        self.estado_propulsores = True
        self.potencia_propulsores = 100  # Máxima potencia para abortar
        self.alertas.append(("¡MISIÓN ABORTADA!", True))
    
    def ajustar_pid(self, Kp, Ki, Kd):
        """Ajusta los parámetros del control PID"""
        try:
            self.Kp = float(Kp)
            self.Ki = float(Ki)
            self.Kd = float(Kd)
            self.alertas.append((f"PID ajustado: Kp={Kp}, Ki={Ki}, Kd={Kd}", False))
        except (ValueError, TypeError):
            logger.error(f"Valores PID no válidos: Kp={Kp}, Ki={Ki}, Kd={Kd}")
            self.alertas.append(("Error: Valores PID no válidos", True))
        
    def reiniciar_simulacion(self):
        """Reinicia la simulación a los valores iniciales"""
        self.__init__()
        self.alertas.append(("Simulación reiniciada", True))

class VistaCohete:
    def __init__(self, root):
        self.root = root
        self._images = []  # Lista para mantener referencias a imágenes
        self._figures = []  # Lista para mantener referencias a figuras
        self._setup_main_window()
        self._initialize_images()
        self._setup_styles()
        self._create_main_structure()
        self._create_all_panels()
        self._initialize_graphics()
        self._show_credits()
        
    def _setup_main_window(self):
        """Configura la ventana principal"""
        self.root.title("ASP - Sistema Avanzado de Control de Cohetes")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _on_window_close(self):
        """Maneja el cierre de la ventana"""
        if hasattr(self, 'ani_altitud'):
            self.ani_altitud.event_source.stop()
        if hasattr(self, 'ani_velocidad'):
            self.ani_velocidad.event_source.stop()
        if hasattr(self, 'ani_temperatura'):
            self.ani_temperatura.event_source.stop()
        if hasattr(self, 'ani_aceleracion'):
            self.ani_aceleracion.event_source.stop()
        if hasattr(self, 'ani_pid'):
            self.ani_pid.event_source.stop()
        if hasattr(self, 'ani_perfil'):
            self.ani_perfil.event_source.stop()
        
        self.root.destroy()
    
    def _initialize_images(self):
        """Crea y almacena todas las imágenes necesarias"""
        # Imagen del cohete
        self.img_cohete = self._create_rocket_image()
        
        # Imagen de la Tierra
        self.img_tierra = self._create_earth_image()
        
        # Imagen de nube
        self.img_nube = self._create_cloud_image()
        
        # Imagen del sol
        self.img_sol = self._create_sun_image()
        
        # Imagen de fondo estrellado
        self.img_estrellas = self._create_stars_image()
        
        # Imagen del logo
        self.img_logo = self._create_logo_image()
    
    def _setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configuraciones generales
        style.configure(".", background="#1e1e1e", foreground="white")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="white", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#007acc")])
        
        # Estilos personalizados
        style.configure("Indicador.TFrame", background="#2d2d2d", relief="raised", borderwidth=1)
        style.configure("Indicador.TLabel", font=("Arial", 12, "bold"))
        style.configure("Peligro.TButton", foreground="white", background="#d9534f", font=("Arial", 12, "bold"))
        style.configure("Exito.TButton", foreground="white", background="#5cb85c", font=("Arial", 12, "bold"))
        style.configure("Info.TButton", foreground="white", background="#5bc0de", font=("Arial", 12, "bold"))
        style.configure("Grafico.TFrame", background="#252526", relief="sunken", borderwidth=2)
        
        # Estilo para la tabla
        style.configure("Treeview", background="#292929", foreground="white", fieldbackground="#292929", rowheight=25)
        style.configure("Treeview.Heading", background="#007acc", foreground="white", font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#007acc")])
        
        # Estilo para la consola
        style.configure("Consola.TFrame", background="#292929")
        style.configure("Consola.TLabel", background="#292929", foreground="white")
        
        # Estilo para los créditos
        style.configure("Creditos.TLabel", font=("Arial", 8), foreground="#888888")
    
    def _create_main_structure(self):
        """Crea la estructura principal de la interfaz"""
        self.marco_principal = ttk.Frame(self.root)
        self.marco_principal.pack(fill="both", expand=True)
        
        # Marco superior (título y estado)
        self.marco_superior = ttk.Frame(self.marco_principal)
        self.marco_superior.pack(fill="x", padx=10, pady=5)
        
        # Marco central (datos y visualización)
        self.marco_central = ttk.Frame(self.marco_principal)
        self.marco_central.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Marco inferior (controles)
        self.marco_inferior = ttk.Frame(self.marco_principal)
        self.marco_inferior.pack(fill="x", padx=10, pady=5)
        
        # Marco lateral (gráficos y telemetría)
        self.marco_lateral = ttk.Frame(self.marco_principal, width=350)
        self.marco_lateral.pack(side="right", fill="y", padx=10, pady=5)
    
    def _create_all_panels(self):
        """Crea todos los paneles de la interfaz"""
        self._create_top_panel()
        self._create_center_panel()
        self._create_bottom_panel()
        self._create_side_panel()
    
    def _create_top_panel(self):
        """Crea el panel superior con título y estado"""
        # Logo
        self.label_logo = ttk.Label(self.marco_superior, image=self.img_logo)
        self.label_logo.pack(side="left", padx=5)
        
        # Título principal
        self.label_titulo = ttk.Label(self.marco_superior, 
                                    text="ASP - Sistema Avanzado de Control de Aterrizaje de Cohetes", 
                                    font=("Arial", 18, "bold"))
        self.label_titulo.pack(side="left", padx=10)
        
        # Estado de la misión
        self.label_estado = ttk.Label(self.marco_superior, 
                                     text="ESTADO: NOMINAL", 
                                     font=("Arial", 12, "bold"),
                                     foreground="green")
        self.label_estado.pack(side="right", padx=10)
        
        # Tiempo transcurrido
        self.label_tiempo = ttk.Label(self.marco_superior, 
                                     text="T: 00:00:00", 
                                     font=("Courier New", 12))
        self.label_tiempo.pack(side="right", padx=10)
        
        # Fase de vuelo
        self.label_fase = ttk.Label(self.marco_superior,
                                  text="FASE: DESCENSO",
                                  font=("Arial", 12))
        self.label_fase.pack(side="right", padx=10)
    
    def _create_center_panel(self):
        """Crea el panel central con pestañas"""
        self.notebook = ttk.Notebook(self.marco_central)
        self.notebook.pack(fill="both", expand=True)
        
        # Pestañas principales
        self.tab_datos = ttk.Frame(self.notebook)
        self.tab_visualizacion = ttk.Frame(self.notebook)
        self.tab_telemetria = ttk.Frame(self.notebook)
        self.tab_pid = ttk.Frame(self.notebook)
        self.tab_ambiente = ttk.Frame(self.notebook)
        self.tab_historico = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_datos, text="📊 Datos")
        self.notebook.add(self.tab_visualizacion, text="🚀 Visualización")
        self.notebook.add(self.tab_telemetria, text="📈 Telemetría")
        self.notebook.add(self.tab_pid, text="🎛 Control PID")
        self.notebook.add(self.tab_ambiente, text="🌍 Ambiente")
        self.notebook.add(self.tab_historico, text="📅 Histórico")
        
        # Crear contenido de cada pestaña
        self._create_data_panel()
        self._create_visualization_panel()
        self._create_telemetry_panel()
        self._create_pid_panel()
        self._create_environment_panel()
        self._create_history_panel()
    
    def _create_history_panel(self):
        """Crea el panel de datos históricos"""
        self.marco_historico = ttk.Frame(self.tab_historico)
        self.marco_historico.pack(fill="both", expand=True)
        
        # Notebook para diferentes vistas históricas
        self.notebook_historico = ttk.Notebook(self.marco_historico)
        self.notebook_historico.pack(fill="both", expand=True)
        
        # Pestaña de telemetría histórica
        self.tab_telemetria_historica = ttk.Frame(self.notebook_historico)
        self.notebook_historico.add(self.tab_telemetria_historica, text="Telemetría")
        
        # Pestaña de alertas históricas
        self.tab_alertas_historicas = ttk.Frame(self.notebook_historico)
        self.notebook_historico.add(self.tab_alertas_historicas, text="Alertas")
        
        # Pestaña de configuraciones PID
        self.tab_pid_historico = ttk.Frame(self.notebook_historico)
        self.notebook_historico.add(self.tab_pid_historico, text="Configuraciones PID")
        
        # Crear contenido de cada pestaña
        self._create_historical_telemetry_panel()
        self._create_historical_alerts_panel()
        self._create_historical_pid_panel()
    
    def _create_historical_telemetry_panel(self):
        """Crea el panel de telemetría histórica"""
        self.frame_telemetria_historica = ttk.Frame(self.tab_telemetria_historica)
        self.frame_telemetria_historica.pack(fill="both", expand=True)
        
        # Treeview para mostrar datos
        self.tree_telemetria = ttk.Treeview(self.frame_telemetria_historica, 
                                          columns=("Fecha", "Altitud", "Velocidad", "Temperatura", "Combustible"),
                                          show="headings",
                                          height=15)
        
        # Configurar columnas
        columnas = [
            ("Fecha", "Fecha/Hora"),
            ("Altitud", "Altitud (m)"),
            ("Velocidad", "Velocidad (m/s)"),
            ("Temperatura", "Temperatura (°C)"),
            ("Combustible", "Combustible (%)")
        ]
        
        for col_id, col_text in columnas:
            self.tree_telemetria.heading(col_id, text=col_text)
            self.tree_telemetria.column(col_id, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.frame_telemetria_historica, 
                                 orient="vertical", 
                                 command=self.tree_telemetria.yview)
        self.tree_telemetria.configure(yscrollcommand=scrollbar.set)
        
        self.tree_telemetria.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para cargar datos
        self.boton_cargar_telemetria = ttk.Button(self.frame_telemetria_historica,
                                                text="Cargar Datos",
                                                command=self._load_telemetry_data)
        self.boton_cargar_telemetria.pack(pady=5)
    
    def _load_telemetry_data(self):
        """Carga datos de telemetría desde la base de datos"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'db'):
            datos = self.controller.db.get_last_telemetry(50)
            
            # Limpiar tabla
            for row in self.tree_telemetria.get_children():
                self.tree_telemetria.delete(row)
            
            # Añadir datos
            for dato in reversed(datos):  # Mostrar del más antiguo al más reciente
                self.tree_telemetria.insert("", "end", values=(
                    dato[1],  # timestamp
                    f"{dato[2]:.2f}",  # altitud
                    f"{dato[3]:.2f}",  # velocidad
                    f"{dato[5]:.2f}",  # temperatura
                    f"{dato[8]:.1f}"   # combustible
                ))
    
    def _create_historical_alerts_panel(self):
        """Crea el panel de alertas históricas"""
        self.frame_alertas_historicas = ttk.Frame(self.tab_alertas_historicas)
        self.frame_alertas_historicas.pack(fill="both", expand=True)
        
        # Treeview para mostrar alertas
        self.tree_alertas = ttk.Treeview(self.frame_alertas_historicas,
                                       columns=("Fecha", "Mensaje", "Crítica"),
                                       show="headings",
                                       height=15)
        
        # Configurar columnas
        columnas = [
            ("Fecha", "Fecha/Hora"),
            ("Mensaje", "Mensaje de Alerta"),
            ("Crítica", "Crítica")
        ]
        
        for col_id, col_text in columnas:
            self.tree_alertas.heading(col_id, text=col_text)
            self.tree_alertas.column(col_id, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.frame_alertas_historicas,
                                 orient="vertical",
                                 command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_alertas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para cargar alertas
        self.boton_cargar_alertas = ttk.Button(self.frame_alertas_historicas,
                                             text="Cargar Alertas",
                                             command=self._load_alerts_data)
        self.boton_cargar_alertas.pack(pady=5)
    
    def _load_alerts_data(self):
        """Carga datos de alertas desde la base de datos"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'db'):
            alertas = self.controller.db.get_alerts(50)
            
            # Limpiar tabla
            for row in self.tree_alertas.get_children():
                self.tree_alertas.delete(row)
            
            # Añadir datos
            for alerta in reversed(alertas):
                self.tree_alertas.insert("", "end", values=(
                    alerta[1],  # timestamp
                    alerta[2],  # mensaje
                    "Sí" if alerta[3] else "No"  # crítica
                ))
    
    def _create_historical_pid_panel(self):
        """Crea el panel de configuraciones PID históricas"""
        self.frame_pid_historico = ttk.Frame(self.tab_pid_historico)
        self.frame_pid_historico.pack(fill="both", expand=True)
        
        # Treeview para mostrar configuraciones PID
        self.tree_pid = ttk.Treeview(self.frame_pid_historico,
                                    columns=("Fecha", "Kp", "Ki", "Kd", "Comentario"),
                                    show="headings",
                                    height=15)
        
        # Configurar columnas
        columnas = [
            ("Fecha", "Fecha/Hora"),
            ("Kp", "Ganancia Proporcional"),
            ("Ki", "Ganancia Integral"),
            ("Kd", "Ganancia Derivativa"),
            ("Comentario", "Comentario")
        ]
        
        for col_id, col_text in columnas:
            self.tree_pid.heading(col_id, text=col_text)
            self.tree_pid.column(col_id, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.frame_pid_historico,
                                 orient="vertical",
                                 command=self.tree_pid.yview)
        self.tree_pid.configure(yscrollcommand=scrollbar.set)
        
        self.tree_pid.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para cargar configuraciones PID
        self.boton_cargar_pid = ttk.Button(self.frame_pid_historico,
                                          text="Cargar Configuraciones",
                                          command=self._load_pid_data)
        self.boton_cargar_pid.pack(pady=5)
    
    def _load_pid_data(self):
        """Carga datos de configuraciones PID desde la base de datos"""
        if hasattr(self, 'controller') and hasattr(self.controller, 'db'):
            configs = self.controller.db.get_pid_config_history(20)
            
            # Limpiar tabla
            for row in self.tree_pid.get_children():
                self.tree_pid.delete(row)
            
            # Añadir datos
            for config in reversed(configs):
                self.tree_pid.insert("", "end", values=(
                    config[1],  # timestamp
                    f"{config[2]:.2f}",  # Kp
                    f"{config[3]:.2f}",  # Ki
                    f"{config[4]:.2f}",  # Kd
                    config[5] if config[5] else ""  # comentario
                ))
    
    def _create_data_panel(self):
        """Crea el panel de datos principales"""
        # Marco para indicadores principales
        self.marco_indicadores = ttk.Frame(self.tab_datos)
        self.marco_indicadores.pack(fill="x", pady=10)
        
        # Indicadores principales
        indicadores = [
            ("Altitud (m)", "0.00", "altitud", "#4fc3f7"),
            ("Velocidad (m/s)", "0.00", "velocidad", "#ff7043"),
            ("Orientación (°)", "0.00", "orientacion", "#ba68c8"),
            ("Temperatura (°C)", "0.00", "temperatura", "#ff5252"),
            ("Combustible (%)", "100", "combustible", "#66bb6a"),
            ("Presión (atm)", "1.0", "presion", "#26c6da"),
            ("Aceleración (m/s²)", "0.00", "aceleracion", "#ffca28"),
            ("Viento (m/s)", "0.00", "viento", "#b0bec5")
        ]
        
        self.indicadores = {}
        
        for i, (texto, valor, nombre, color) in enumerate(indicadores):
            frame = ttk.Frame(self.marco_indicadores, style="Indicador.TFrame")
            frame.grid(row=0, column=i, padx=5, sticky="nsew")
            
            label_titulo = ttk.Label(frame, text=texto, foreground=color)
            label_titulo.pack()
            
            label_valor = ttk.Label(frame, text=valor, style="Indicador.TLabel")
            label_valor.pack()
            
            self.indicadores[nombre] = label_valor
        
        # Tabla de datos históricos
        self.frame_tabla = ttk.Frame(self.tab_datos)
        self.frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(self.frame_tabla, 
                                columns=("Tiempo", "Altitud", "Velocidad", "Orientación", "Temperatura", "Aceleración"), 
                                show="headings", 
                                height=10)
        
        columnas = [
            ("Tiempo", "Tiempo (s)"),
            ("Altitud", "Altitud (m)"),
            ("Velocidad", "Velocidad (m/s)"),
            ("Orientación", "Orientación (°)"),
            ("Temperatura", "Temperatura (°C)"),
            ("Aceleración", "Aceleración (m/s²)")
        ]
        
        for col_id, col_text in columnas:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_visualization_panel(self):
        """Crea el panel de visualización 3D"""
        self.marco_visualizacion = ttk.Frame(self.tab_visualizacion, style="Grafico.TFrame")
        self.marco_visualizacion.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_visualizacion = tk.Canvas(self.marco_visualizacion, bg="#000033", width=800, height=500)
        self.canvas_visualizacion.pack(fill="both", expand=True)
        
        # Fondo estrellado
        self.img_estrellas_canvas = self.canvas_visualizacion.create_image(400, 250, image=self.img_estrellas)
        
        # Dibujar horizonte
        self.canvas_visualizacion.create_arc(100, 300, 700, 900, start=0, extent=180, fill="#000066", outline="")
        
        # Elementos visuales
        self.img_tierra_canvas = self.canvas_visualizacion.create_image(400, 700, image=self.img_tierra, anchor="center")
        self.img_sol_canvas = self.canvas_visualizacion.create_image(700, 100, image=self.img_sol)
        self.img_nube_canvas = []
        for _ in range(3):
            x = random.randint(100, 700)
            y = random.randint(400, 500)
            img = self.canvas_visualizacion.create_image(x, y, image=self.img_nube)
            self.img_nube_canvas.append(img)
        
        # Cohete
        self.img_cohete_canvas = self.canvas_visualizacion.create_image(400, 100, image=self.img_cohete, anchor="center")
        
        # Indicadores
        self.barra_altitud = self.canvas_visualizacion.create_rectangle(750, 50, 770, 450, fill="gray")
        self.indicator_altitud = self.canvas_visualizacion.create_rectangle(750, 450, 770, 450, fill="red")
        self.canvas_visualizacion.create_text(760, 30, text="Altitud", fill="white")
        
        # Indicador de orientación
        self.canvas_visualizacion.create_text(50, 30, text="Orientación:", fill="white")
        self.indicador_orientacion = self.canvas_visualizacion.create_text(120, 30, text="0°", fill="white")
        
        # Indicador de velocidad
        self.canvas_visualizacion.create_text(50, 60, text="Velocidad:", fill="white")
        self.indicador_velocidad = self.canvas_visualizacion.create_text(120, 60, text="0 m/s", fill="white")
        
        # Indicador de llamas (animación)
        self.llamas = []
        for i in range(5):
            llama = self.canvas_visualizacion.create_polygon([0, 0, 0, 0], fill="#ff5252")
            self.llamas.append(llama)
    
    def _create_telemetry_panel(self):
        """Crea el panel de telemetría con gráficos"""
        self.marco_telemetria = ttk.Frame(self.tab_telemetria)
        self.marco_telemetria.pack(fill="both", expand=True)
        
        # Notebook para diferentes gráficos
        self.notebook_telemetria = ttk.Notebook(self.marco_telemetria)
        self.notebook_telemetria.pack(fill="both", expand=True)
        
        # Pestaña de altitud
        self.tab_altitud = ttk.Frame(self.notebook_telemetria)
        self.notebook_telemetria.add(self.tab_altitud, text="Altitud")
        
        # Pestaña de velocidad
        self.tab_velocidad = ttk.Frame(self.notebook_telemetria)
        self.notebook_telemetria.add(self.tab_velocidad, text="Velocidad")
        
        # Pestaña de temperatura
        self.tab_temperatura = ttk.Frame(self.notebook_telemetria)
        self.notebook_telemetria.add(self.tab_temperatura, text="Temperatura")
        
        # Pestaña de aceleración
        self.tab_aceleracion = ttk.Frame(self.notebook_telemetria)
        self.notebook_telemetria.add(self.tab_aceleracion, text="Aceleración")
        
        # Crear gráficos
        self._create_altitude_chart()
        self._create_velocity_chart()
        self._create_temperature_chart()
        self._create_acceleration_chart()
    
    def _create_altitude_chart(self):
        """Crea el gráfico de altitud"""
        self.fig_altitud = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_altitud)
        
        self.ax_altitud = self.fig_altitud.add_subplot(111)
        self.ax_altitud.set_facecolor('#252526')
        self.ax_altitud.set_title('Altitud vs Tiempo', color='white')
        self.ax_altitud.set_xlabel('Tiempo (s)', color='white')
        self.ax_altitud.set_ylabel('Altitud (m)', color='white')
        self.ax_altitud.tick_params(colors='white')
        self.ax_altitud.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_altitud, = self.ax_altitud.plot([], [], 'c-', linewidth=2)
        
        self.canvas_altitud = FigureCanvasTkAgg(self.fig_altitud, self.tab_altitud)
        self.canvas_altitud.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_velocity_chart(self):
        """Crea el gráfico de velocidad"""
        self.fig_velocidad = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_velocidad)
        
        self.ax_velocidad = self.fig_velocidad.add_subplot(111)
        self.ax_velocidad.set_facecolor('#252526')
        self.ax_velocidad.set_title('Velocidad vs Tiempo', color='white')
        self.ax_velocidad.set_xlabel('Tiempo (s)', color='white')
        self.ax_velocidad.set_ylabel('Velocidad (m/s)', color='white')
        self.ax_velocidad.tick_params(colors='white')
        self.ax_velocidad.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_velocidad, = self.ax_velocidad.plot([], [], 'y-', linewidth=2)
        
        self.canvas_velocidad = FigureCanvasTkAgg(self.fig_velocidad, self.tab_velocidad)
        self.canvas_velocidad.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_temperature_chart(self):
        """Crea el gráfico de temperatura"""
        self.fig_temperatura = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_temperatura)
        
        self.ax_temperatura = self.fig_temperatura.add_subplot(111)
        self.ax_temperatura.set_facecolor('#252526')
        self.ax_temperatura.set_title('Temperatura vs Tiempo', color='white')
        self.ax_temperatura.set_xlabel('Tiempo (s)', color='white')
        self.ax_temperatura.set_ylabel('Temperatura (°C)', color='white')
        self.ax_temperatura.tick_params(colors='white')
        self.ax_temperatura.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_temperatura, = self.ax_temperatura.plot([], [], 'r-', linewidth=2)
        
        self.canvas_temperatura = FigureCanvasTkAgg(self.fig_temperatura, self.tab_temperatura)
        self.canvas_temperatura.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_acceleration_chart(self):
        """Crea el gráfico de aceleración"""
        self.fig_aceleracion = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_aceleracion)
        
        self.ax_aceleracion = self.fig_aceleracion.add_subplot(111)
        self.ax_aceleracion.set_facecolor('#252526')
        self.ax_aceleracion.set_title('Aceleración vs Tiempo', color='white')
        self.ax_aceleracion.set_xlabel('Tiempo (s)', color='white')
        self.ax_aceleracion.set_ylabel('Aceleración (m/s²)', color='white')
        self.ax_aceleracion.tick_params(colors='white')
        self.ax_aceleracion.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_aceleracion, = self.ax_aceleracion.plot([], [], 'm-', linewidth=2)
        
        self.canvas_aceleracion = FigureCanvasTkAgg(self.fig_aceleracion, self.tab_aceleracion)
        self.canvas_aceleracion.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_pid_panel(self):
        """Crea el panel de control PID"""
        self.marco_pid = ttk.Frame(self.tab_pid)
        self.marco_pid.pack(fill="both", expand=True)
        
        # Marco para controles PID
        self.marco_controles_pid = ttk.Frame(self.marco_pid)
        self.marco_controles_pid.pack(fill="x", pady=10)
        
        # Controles PID
        ttk.Label(self.marco_controles_pid, text="Control PID", font=("Arial", 14)).pack()
        
        # Sliders para ajustar parámetros PID
        self._create_pid_slider("Kp (Proporcional):", 0, 2, 0.5)
        self._create_pid_slider("Ki (Integral):", 0, 1, 0.1)
        self._create_pid_slider("Kd (Derivativo):", 0, 1, 0.2)
        
        # Gráfico PID
        self.fig_pid = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_pid)
        
        self.ax_pid = self.fig_pid.add_subplot(111)
        self.ax_pid.set_facecolor('#252526')
        self.ax_pid.set_title('Control PID', color='white')
        self.ax_pid.set_xlabel('Tiempo (s)', color='white')
        self.ax_pid.set_ylabel('Valor', color='white')
        self.ax_pid.tick_params(colors='white')
        self.ax_pid.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_error, = self.ax_pid.plot([], [], 'r-', label='Error', linewidth=2)
        self.line_salida, = self.ax_pid.plot([], [], 'g-', label='Salida PID', linewidth=2)
        self.line_potencia, = self.ax_pid.plot([], [], 'b-', label='Potencia', linewidth=2)
        self.ax_pid.legend()
        
        self.canvas_pid = FigureCanvasTkAgg(self.fig_pid, self.marco_pid)
        self.canvas_pid.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_pid_slider(self, texto, min_val, max_val, valor_inicial):
        """Crea un slider para ajustar parámetros PID"""
        frame = ttk.Frame(self.marco_controles_pid)
        frame.pack(fill="x", padx=10, pady=5)
        
        label = ttk.Label(frame, text=texto, width=20)
        label.pack(side="left", padx=5)
        
        valor_var = tk.StringVar()
        valor_var.set(str(valor_inicial))
        
        label_valor = ttk.Label(frame, textvariable=valor_var, width=5)
        label_valor.pack(side="right", padx=5)
        
        slider = ttk.Scale(frame, from_=min_val, to=max_val, value=valor_inicial,
                          command=lambda v, var=valor_var: var.set(f"{float(v):.2f}"))
        slider.pack(side="left", fill="x", expand=True)
        
        # Guardar referencia
        if texto.startswith("Kp"):
            self.slider_kp = slider
            self.var_kp = valor_var
        elif texto.startswith("Ki"):
            self.slider_ki = slider
            self.var_ki = valor_var
        elif texto.startswith("Kd"):
            self.slider_kd = slider
            self.var_kd = valor_var
    
    def _create_environment_panel(self):
        """Crea el panel de información ambiental"""
        self.marco_ambiente = ttk.Frame(self.tab_ambiente)
        self.marco_ambiente.pack(fill="both", expand=True)
        
        # Notebook para diferentes vistas ambientales
        self.notebook_ambiente = ttk.Notebook(self.marco_ambiente)
        self.notebook_ambiente.pack(fill="both", expand=True)
        
        # Pestaña de condiciones actuales
        self.tab_condiciones = ttk.Frame(self.notebook_ambiente)
        self.notebook_ambiente.add(self.tab_condiciones, text="Condiciones Actuales")
        
        # Pestaña de perfil atmosférico
        self.tab_perfil = ttk.Frame(self.notebook_ambiente)
        self.notebook_ambiente.add(self.tab_perfil, text="Perfil Atmosférico")
        
        # Contenido de las pestañas
        self._create_conditions_panel()
        self._create_profile_panel()
    
    def _create_conditions_panel(self):
        """Crea el panel de condiciones ambientales"""
        self.marco_condiciones = ttk.Frame(self.tab_condiciones)
        self.marco_condiciones.pack(fill="both", expand=True, padx=10, pady=10)
        
        indicadores = [
            ("Presión (atm)", "presion", "#26c6da"),
            ("Humedad Relativa (%)", "humedad", "#42a5f5"),
            ("Velocidad del Viento (m/s)", "viento", "#b0bec5"),
            ("Dirección del Viento", "direccion_viento", "#78909c")
        ]
        
        self.indicadores_ambiente = {}
        
        for i, (texto, nombre, color) in enumerate(indicadores):
            frame = ttk.Frame(self.marco_condiciones)
            frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            
            label = ttk.Label(frame, text=texto, width=25, anchor="w")
            label.pack(side="left")
            
            valor = ttk.Label(frame, text="0.00", width=10)
            valor.pack(side="right")
            
            self.indicadores_ambiente[nombre] = valor
        
        # Rosa de los vientos
        self.frame_viento = ttk.Frame(self.marco_condiciones)
        self.frame_viento.grid(row=0, column=1, rowspan=4, padx=10, pady=10)
        
        self.canvas_viento = tk.Canvas(self.frame_viento, width=200, height=200, bg="#292929", highlightthickness=0)
        self.canvas_viento.pack()
        
        # Dibujar círculo de la rosa de los vientos
        self.canvas_viento.create_oval(50, 50, 150, 150, outline="#5bc0de", width=2)
        self.canvas_viento.create_text(100, 30, text="N", fill="white")
        self.canvas_viento.create_text(100, 170, text="S", fill="white")
        self.canvas_viento.create_text(30, 100, text="O", fill="white")
        self.canvas_viento.create_text(170, 100, text="E", fill="white")
    
    def _create_profile_panel(self):
        """Crea el panel de perfil atmosférico"""
        self.fig_perfil = Figure(figsize=(6, 4), dpi=100, facecolor='#252526')
        self._figures.append(self.fig_perfil)
        
        self.ax_perfil = self.fig_perfil.add_subplot(111)
        self.ax_perfil.set_facecolor('#252526')
        self.ax_perfil.set_title('Perfil Atmosférico', color='white')
        self.ax_perfil.set_xlabel('Valor', color='white')
        self.ax_perfil.set_ylabel('Altitud (m)', color='white')
        self.ax_perfil.tick_params(colors='white')
        self.ax_perfil.grid(color='gray', linestyle='--', alpha=0.5)
        
        self.line_presion, = self.ax_perfil.plot([], [], 'c-', label='Presión (atm)', linewidth=2)
        self.line_temp_perfil, = self.ax_perfil.plot([], [], 'r-', label='Temperatura (°C)', linewidth=2)
        self.ax_perfil.legend()
        
        self.canvas_perfil = FigureCanvasTkAgg(self.fig_perfil, self.tab_perfil)
        self.canvas_perfil.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_bottom_panel(self):
        """Crea el panel inferior con controles"""
        self.marco_controles = ttk.Frame(self.marco_inferior)
        self.marco_controles.pack(fill="x", pady=5)
        
        # Botones de control
        self.boton_propulsor = ttk.Button(self.marco_controles, text="ACTIVAR PROPULSORES", 
                                        style="Info.TButton", 
                                        command=lambda: self.controller.toggle_propulsores())
        self.boton_propulsor.grid(row=0, column=0, padx=5)
        
        self.boton_tren = ttk.Button(self.marco_controles, text="DESPLEGAR TREN", 
                                    style="Exito.TButton", 
                                    command=lambda: self.controller.desplegar_tren())
        self.boton_tren.grid(row=0, column=1, padx=5)
        
        self.boton_abortar = ttk.Button(self.marco_controles, text="ABORTAR MISIÓN", 
                                       style="Peligro.TButton", 
                                       command=lambda: self.controller.abortar_mision())
        self.boton_abortar.grid(row=0, column=2, padx=5)
        
        self.boton_reiniciar = ttk.Button(self.marco_controles, text="REINICIAR SIMULACIÓN", 
                                         command=lambda: self.controller.reiniciar_simulacion())
        self.boton_reiniciar.grid(row=0, column=3, padx=5)
        
        # Control de potencia manual
        self.label_potencia = ttk.Label(self.marco_controles, text="Potencia propulsores: 0%")
        self.label_potencia.grid(row=0, column=4, padx=10)
        
        self.slider_potencia = ttk.Scale(self.marco_controles, from_=0, to=100, orient="horizontal")
        self.slider_potencia.grid(row=0, column=5, padx=5)
        self.slider_potencia.bind("<ButtonRelease-1>", lambda e: self.controller.ajustar_potencia(self.slider_potencia.get()))
        
        # Configurar columnas para que se expandan
        for i in range(6):
            self.marco_controles.columnconfigure(i, weight=1)
    
    def _create_side_panel(self):
        """Crea el panel lateral con información adicional"""
        self.notebook_lateral = ttk.Notebook(self.marco_lateral)
        self.notebook_lateral.pack(fill="both", expand=True)
        
        # Pestaña de alertas
        self.tab_alertas = ttk.Frame(self.notebook_lateral)
        self.notebook_lateral.add(self.tab_alertas, text="⚠ Alertas")
        
        # Pestaña de sistemas
        self.tab_sistemas = ttk.Frame(self.notebook_lateral)
        self.notebook_lateral.add(self.tab_sistemas, text="🛠 Sistemas")
        
        # Pestaña de consola
        self.tab_consola = ttk.Frame(self.notebook_lateral)
        self.notebook_lateral.add(self.tab_consola, text="💻 Consola")
        
        # Contenido de las pestañas
        self._create_alerts_panel()
        self._create_systems_panel()
        self._create_console_panel()
    
    def _create_alerts_panel(self):
        """Crea el panel de alertas"""
        self.lista_alertas = tk.Listbox(self.tab_alertas, bg="#292929", fg="white", font=("Consolas", 10), height=15)
        scrollbar = ttk.Scrollbar(self.tab_alertas, orient="vertical", command=self.lista_alertas.yview)
        self.lista_alertas.configure(yscrollcommand=scrollbar.set)
        
        self.lista_alertas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Diccionario de colores para alertas
        self.colores_alertas = {
            "info": "#5bc0de",
            "warning": "#ffc107",
            "danger": "#dc3545"
        }
        
        # Añadir algunas alertas de ejemplo
        for alerta in self.controller.modelo.alertas if hasattr(self, 'controller') else []:
            self.lista_alertas.insert("end", f"[00:00:00] {alerta[0]}")
            self.lista_alertas.itemconfig("end", fg=self.colores_alertas["danger" if alerta[1] else "info"])
    
    def _create_systems_panel(self):
        """Crea el panel de estado de sistemas"""
        self.marco_sistemas = ttk.Frame(self.tab_sistemas)
        self.marco_sistemas.pack(fill="both", expand=True)
        
        # Sistemas a monitorear
        sistemas = [
            ("Propulsión", "green", "propulsion"),
            ("Navegación", "green", "navegacion"),
            ("Comunicaciones", "green", "comunicaciones"),
            ("Computadora", "green", "computadora"),
            ("Sensores", "green", "sensores"),
            ("Energía", "green", "energia"),
            ("Guía", "green", "guia"),
            ("Control", "green", "control")
        ]
        
        self.indicadores_sistema = {}
        
        for i, (nombre, color, id_sistema) in enumerate(sistemas):
            frame = ttk.Frame(self.marco_sistemas, style="Indicador.TFrame")
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            
            label = ttk.Label(frame, text=nombre, width=15, anchor="w")
            label.pack(side="left", padx=5)
            
            # Indicador de estado (simulado con un canvas)
            canvas = tk.Canvas(frame, width=20, height=20, bg="#292929", highlightthickness=0)
            canvas.pack(side="right", padx=5)
            canvas.create_oval(2, 2, 18, 18, fill=color)
            
            self.indicadores_sistema[id_sistema] = (canvas, color)
    
    def _create_console_panel(self):
        """Crea el panel de consola"""
        self.consola = tk.Text(self.tab_consola, bg="#292929", fg="white", font=("Consolas", 10), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.tab_consola, orient="vertical", command=self.consola.yview)
        self.consola.configure(yscrollcommand=scrollbar.set)
        
        self.consola.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar tags para colores
        self.consola.tag_config("info", foreground="#5bc0de")
        self.consola.tag_config("warning", foreground="#ffc107")
        self.consola.tag_config("danger", foreground="#dc3545")
        self.consola.tag_config("success", foreground="#28a745")
        
        # Mensaje inicial
        self.consola.insert("end", ">>> Sistema de control de cohete inicializado\n", "info")
        self.consola.insert("end", ">>> Todos los sistemas verificados\n", "success")
        self.consola.insert("end", ">>> Listo para secuencia de descenso\n", "info")
        self.consola.configure(state="disabled")
    
    def _create_rocket_image(self):
        """Crea la imagen del cohete"""
        image = Image.new("RGBA", (60, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Cuerpo del cohete
        draw.rectangle([20, 0, 40, 100], fill="#b0bec5")
        
        # Punta del cohete
        draw.polygon([20, 0, 40, 0, 30, -20], fill="#ff7043")
        
        # Alas
        draw.polygon([20, 60, 0, 80, 20, 80], fill="#78909c")
        draw.polygon([40, 60, 60, 80, 40, 80], fill="#78909c")
        
        # Ventana
        draw.ellipse([25, 20, 35, 30], fill="#42a5f5")
        
        # Llamas (solo base)
        draw.polygon([20, 100, 30, 120, 40, 100], fill="#ff5252")
        
        img = ImageTk.PhotoImage(image)
        self._images.append(img)  # Mantener referencia
        return img
    
    def _create_earth_image(self):
        """Crea la imagen de la Tierra"""
        image = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Planeta
        draw.ellipse([0, 0, 800, 800], fill="#0d47a1")
        
        # Continentes (simplificados)
        draw.ellipse([100, 100, 300, 300], fill="#4caf50", outline="#2e7d32")
        draw.polygon([400, 200, 600, 150, 700, 300, 500, 400], fill="#4caf50", outline="#2e7d32")
        draw.polygon([200, 500, 300, 600, 150, 700], fill="#4caf50", outline="#2e7d32")
        
        # Nubes
        for _ in range(10):
            x, y = random.randint(0, 800), random.randint(0, 800)
            draw.ellipse([x, y, x+50, y+30], fill="white", outline="lightgray")
        
        img = ImageTk.PhotoImage(image.resize((600, 600)))
        self._images.append(img)
        return img
    
    def _create_cloud_image(self):
        """Crea la imagen de una nube"""
        image = Image.new("RGBA", (100, 60), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.ellipse([0, 20, 40, 60], fill="white")
        draw.ellipse([20, 0, 80, 50], fill="white")
        draw.ellipse([60, 20, 100, 60], fill="white")
        
        img = ImageTk.PhotoImage(image)
        self._images.append(img)
        return img
    
    def _create_sun_image(self):
        """Crea la imagen del sol"""
        image = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.ellipse([0, 0, 100, 100], fill="#ffeb3b")
        
        # Rayos de sol
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = 50 + 60 * math.cos(rad)
            y1 = 50 + 60 * math.sin(rad)
            x2 = 50 + 80 * math.cos(rad)
            y2 = 50 + 80 * math.sin(rad)
            draw.line([x1, y1, x2, y2], fill="#ffeb3b", width=3)
        
        img = ImageTk.PhotoImage(image)
        self._images.append(img)
        return img
    
    def _create_stars_image(self):
        """Crea el fondo estrellado"""
        image = Image.new("RGB", (800, 500), "#000033")
        draw = ImageDraw.Draw(image)
        
        # Dibujar estrellas
        for _ in range(200):
            x = random.randint(0, 800)
            y = random.randint(0, 300)  # Solo en la parte superior
            size = random.randint(1, 3)
            brightness = random.randint(200, 255)
            color = (brightness, brightness, brightness)
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        # Añadir Vía Láctea (simplificada)
        for _ in range(50):
            x = random.randint(100, 700)
            y = random.randint(100, 200)
            size = random.randint(1, 2)
            brightness = random.randint(150, 200)
            color = (brightness, brightness, brightness)
            draw.ellipse([x, y, x+size, y+size], fill=color)
        
        img = ImageTk.PhotoImage(image)
        self._images.append(img)
        return img
    
    def _create_logo_image(self):
        """Crea la imagen del logo"""
        image = Image.new("RGBA", (100, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Dibujar cohete pequeño
        draw.rectangle([20, 10, 30, 30], fill="#b0bec5")
        draw.polygon([20, 10, 30, 10, 25, 0], fill="#ff7043")
        draw.polygon([20, 30, 15, 40, 20, 40], fill="#78909c")
        draw.polygon([30, 30, 35, 40, 30, 40], fill="#78909c")
        
        # Texto ASP
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            
        draw.text((40, 5), "ASP", fill="#007acc", font=font)
        draw.text((40, 25), "Control", fill="#ffffff", font=font)
        
        img = ImageTk.PhotoImage(image)
        self._images.append(img)
        return img
    
    def _initialize_graphics(self):
        """Inicializa los gráficos y animaciones"""
        self.x_data = []
        self.altitud_data = []
        self.velocidad_data = []
        self.temperatura_data = []
        self.aceleracion_data = []
        self.error_data = []
        self.salida_pid_data = []
        self.potencia_data = []
        self.presion_data = []
        
        # Inicializar animaciones después de que haya datos
        self.ani_altitud = None
        self.ani_velocidad = None
        self.ani_temperatura = None
        self.ani_aceleracion = None
        self.ani_pid = None
        self.ani_perfil = None
    
    def _start_animations(self):
        """Inicia las animaciones de los gráficos"""
        if not hasattr(self, 'animations_started'):
            self.animations_started = True
            
            self.ani_altitud = animation.FuncAnimation(
                self.fig_altitud, self._update_altitude_chart, interval=200, blit=False)
            
            self.ani_velocidad = animation.FuncAnimation(
                self.fig_velocidad, self._update_velocity_chart, interval=200, blit=False)
            
            self.ani_temperatura = animation.FuncAnimation(
                self.fig_temperatura, self._update_temperature_chart, interval=200, blit=False)
            
            self.ani_aceleracion = animation.FuncAnimation(
                self.fig_aceleracion, self._update_acceleration_chart, interval=200, blit=False)
            
            self.ani_pid = animation.FuncAnimation(
                self.fig_pid, self._update_pid_chart, interval=200, blit=False)
            
            self.ani_perfil = animation.FuncAnimation(
                self.fig_perfil, self._update_profile_chart, interval=500, blit=False)
    
    def _update_altitude_chart(self, frame):
        """Actualiza el gráfico de altitud"""
        if hasattr(self, 'controller'):
            datos = self.controller.modelo.telemetria
            if datos:
                self.x_data = [d['tiempo'] for d in datos]
                self.altitud_data = [d['altitud'] for d in datos]
                
                # Limitar puntos para mejorar rendimiento
                max_points = 100
                if len(self.x_data) > max_points:
                    step = len(self.x_data) // max_points
                    x_data = self.x_data[::step]
                    altitud_data = self.altitud_data[::step]
                else:
                    x_data = self.x_data
                    altitud_data = self.altitud_data
                
                self.line_altitud.set_data(x_data, altitud_data)
                self.ax_altitud.relim()
                self.ax_altitud.autoscale_view()
                self.canvas_altitud.draw_idle()
    
    def _update_velocity_chart(self, frame):
        """Actualiza el gráfico de velocidad"""
        if hasattr(self, 'controller'):
            datos = self.controller.modelo.telemetria
            if datos:
                self.velocidad_data = [d['velocidad'] for d in datos]
                
                max_points = 100
                if len(self.x_data) > max_points:
                    step = len(self.x_data) // max_points
                    x_data = self.x_data[::step]
                    velocidad_data = self.velocidad_data[::step]
                else:
                    x_data = self.x_data
                    velocidad_data = self.velocidad_data
                
                self.line_velocidad.set_data(x_data, velocidad_data)
                self.ax_velocidad.relim()
                self.ax_velocidad.autoscale_view()
                self.canvas_velocidad.draw_idle()
    
    def _update_temperature_chart(self, frame):
        """Actualiza el gráfico de temperatura"""
        if hasattr(self, 'controller'):
            datos = self.controller.modelo.telemetria
            if datos:
                self.temperatura_data = [d['temperatura'] for d in datos]
                
                max_points = 100
                if len(self.x_data) > max_points:
                    step = len(self.x_data) // max_points
                    x_data = self.x_data[::step]
                    temperatura_data = self.temperatura_data[::step]
                else:
                    x_data = self.x_data
                    temperatura_data = self.temperatura_data
                
                self.line_temperatura.set_data(x_data, temperatura_data)
                self.ax_temperatura.relim()
                self.ax_temperatura.autoscale_view()
                self.canvas_temperatura.draw_idle()
    
    def _update_acceleration_chart(self, frame):
        """Actualiza el gráfico de aceleración"""
        if hasattr(self, 'controller'):
            datos = self.controller.modelo.telemetria
            if datos:
                self.aceleracion_data = [d['aceleracion'] for d in datos]
                
                max_points = 100
                if len(self.x_data) > max_points:
                    step = len(self.x_data) // max_points
                    x_data = self.x_data[::step]
                    aceleracion_data = self.aceleracion_data[::step]
                else:
                    x_data = self.x_data
                    aceleracion_data = self.aceleracion_data
                
                self.line_aceleracion.set_data(x_data, aceleracion_data)
                self.ax_aceleracion.relim()
                self.ax_aceleracion.autoscale_view()
                self.canvas_aceleracion.draw_idle()
    
    def _update_pid_chart(self, frame):
        """Actualiza el gráfico PID"""
        if hasattr(self, 'controller'):
            datos = self.controller.modelo.pid_history
            if datos:
                x_pid = [d['tiempo'] for d in datos]
                self.error_data = [d['error'] for d in datos]
                self.salida_pid_data = [d['salida_pid'] for d in datos]
                self.potencia_data = [d['potencia'] for d in datos]
                
                max_points = 100
                if len(x_pid) > max_points:
                    step = len(x_pid) // max_points
                    x_pid = x_pid[::step]
                    error_data = self.error_data[::step]
                    salida_pid_data = self.salida_pid_data[::step]
                    potencia_data = self.potencia_data[::step]
                else:
                    error_data = self.error_data
                    salida_pid_data = self.salida_pid_data
                    potencia_data = self.potencia_data
                
                self.line_error.set_data(x_pid, error_data)
                self.line_salida.set_data(x_pid, salida_pid_data)
                self.line_potencia.set_data(x_pid, potencia_data)
                
                self.ax_pid.relim()
                self.ax_pid.autoscale_view()
                self.canvas_pid.draw_idle()
    
    def _update_profile_chart(self, frame):
        """Actualiza el gráfico de perfil atmosférico"""
        if hasattr(self, 'controller'):
            # Simular perfil atmosférico
            alturas = np.linspace(0, 1000, 50)
            presiones = 1.0 * np.exp(-alturas / 8500)
            temperaturas = 20 + (300 - 20) * (1 - alturas / 1000)
            
            self.line_presion.set_data(presiones, alturas)
            self.line_temp_perfil.set_data(temperaturas, alturas)
            
            self.ax_perfil.set_xlim(0, max(max(presiones), max(temperaturas)) + 0.1)
            self.ax_perfil.relim()
            self.ax_perfil.autoscale_view(scalex=True, scaley=False)
            self.canvas_perfil.draw_idle()
    
    def update_view(self, datos):
        """Actualiza toda la vista con los nuevos datos"""
        try:
            self._update_indicators(datos)
            self._update_environment_indicators(datos)
            self._update_mission_status(datos)
            self._update_data_table()
            self._update_3d_visualization(datos)
            self._update_control_buttons(datos)
            self._update_console(datos)
            self._update_systems_status(datos)
            self._update_alerts(datos)
            self._update_pid_values(datos)
            
            # Iniciar animaciones si hay suficientes datos
            if hasattr(self.controller.modelo, 'telemetria') and len(self.controller.modelo.telemetria) > 10:
                self._start_animations()
                
        except Exception as e:
            logger.error(f"Error al actualizar vista: {e}")
    
    def _update_indicators(self, datos):
        """Actualiza los indicadores principales"""
        self.indicadores['altitud'].config(text=f"{datos['altitud']:.2f}")
        self.indicadores['velocidad'].config(text=f"{datos['velocidad']:.2f}")
        self.indicadores['orientacion'].config(text=f"{datos['orientacion']:.2f}")
        self.indicadores['temperatura'].config(text=f"{datos['temperatura']:.2f}")
        self.indicadores['combustible'].config(text=f"{datos['combustible']:.1f}")
        self.indicadores['presion'].config(text=f"{datos['presion']:.3f}")
        self.indicadores['aceleracion'].config(text=f"{datos['aceleracion']:.2f}")
        self.indicadores['viento'].config(text=f"{datos['viento']:.1f}")
    
    def _update_environment_indicators(self, datos):
        """Actualiza los indicadores ambientales"""
        self.indicadores_ambiente['presion'].config(text=f"{datos['presion']:.3f}")
        self.indicadores_ambiente['humedad'].config(text=f"{datos['humedad']:.1f}")
        self.indicadores_ambiente['viento'].config(text=f"{datos['viento']:.1f}")
        self.indicadores_ambiente['direccion_viento'].config(text=f"{datos['direccion_viento']:.0f}°")
        
        # Actualizar rosa de los vientos
        self.canvas_viento.delete("direccion_viento")
        x = 100 + 50 * math.sin(math.radians(datos['direccion_viento']))
        y = 100 - 50 * math.cos(math.radians(datos['direccion_viento']))
        self.canvas_viento.create_line(100, 100, x, y, arrow=tk.LAST, fill="red", width=2, tags="direccion_viento")
    
    def _update_mission_status(self, datos):
        """Actualiza el estado de la misión"""
        estado_texto = "ABORTADA" if datos['abortado'] else "NOMINAL" if datos['altitud'] > 10 else "ATERRIZAJE"
        estado_color = "red" if datos['abortado'] else "green" if datos['altitud'] > 10 else "yellow"
        self.label_estado.config(text=f"ESTADO: {estado_texto}", foreground=estado_color)
        
        # Actualizar fase de vuelo
        fase_texto = "DESCENSO" if datos['altitud'] > 500 else "APROXIMACIÓN" if datos['altitud'] > 100 else "ATERRIZAJE"
        self.label_fase.config(text=f"FASE: {fase_texto}")
        
        # Actualizar tiempo transcurrido
        tiempo_actual = time.strftime("%H:%M:%S", time.gmtime(time.time() - datos.get('tiempo_inicio', 0)))
        self.label_tiempo.config(text=f"T: {tiempo_actual}")
    
    def _update_data_table(self):
        """Actualiza la tabla de datos"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Añadir últimos datos (los 10 más recientes)
        if hasattr(self, 'controller'):
            telemetria_reciente = self.controller.modelo.telemetria[-10:]
            for dato in telemetria_reciente:
                self.tree.insert("", "end", values=(
                    f"{dato['tiempo']:.1f}",
                    f"{dato['altitud']:.2f}",
                    f"{dato['velocidad']:.2f}",
                    f"{dato['orientacion']:.2f}",
                    f"{dato['temperatura']:.2f}",
                    f"{dato['aceleracion']:.2f}"
                ))
    
    def _update_3d_visualization(self, datos):
        """Actualiza la visualización 3D"""
        # Calcular posición del cohete (simulando descenso)
        y_pos = 100 + (datos['altitud'] / 1000 * 300)
        y_pos = min(400, max(100, y_pos))
        
        # Mover cohete
        self.canvas_visualizacion.coords(self.img_cohete_canvas, 400, y_pos)
        
        # Actualizar barra de altitud
        altura_barra = 400 * (1 - datos['altitud'] / 1000)
        self.canvas_visualizacion.coords(self.indicator_altitud, 750, 50 + altura_barra, 770, 450)
        
        # Rotar cohete según orientación
        self.canvas_visualizacion.delete("cohete_rotado")
        angle = datos['orientacion']
        rotated_img = self.img_cohete.rotate(-angle)
        self.img_cohete_rotado = ImageTk.PhotoImage(rotated_img)
        self._images.append(self.img_cohete_rotado)  # Mantener referencia
        self.canvas_visualizacion.itemconfig(self.img_cohete_canvas, image=self.img_cohete_rotado)
        
        # Cambiar color de la barra según velocidad
        color = "red" if datos['velocidad'] < -20 else "yellow" if datos['velocidad'] < -10 else "green"
        self.canvas_visualizacion.itemconfig(self.indicator_altitud, fill=color)
        
        # Actualizar indicadores de orientación y velocidad
        self.canvas_visualizacion.itemconfig(self.indicador_orientacion, text=f"{angle:.1f}°")
        self.canvas_visualizacion.itemconfig(self.indicador_velocidad, text=f"{datos['velocidad']:.1f} m/s")
        
        # Mover nubes (efecto de viento)
        for i, img in enumerate(self.img_nube_canvas):
            x, y = self.canvas_visualizacion.coords(img)
            x = (x - 1 - datos['viento'] * 0.5) % 800
            self.canvas_visualizacion.coords(img, x, y)
        
        # Animar llamas si los propulsores están activos
        if datos['propulsores'] and datos['potencia'] > 0:
            for i, llama in enumerate(self.llamas):
                offset = random.uniform(-5, 5)
                base_x1 = 400 - 10 + offset
                base_x2 = 400 + 10 + offset
                tip_x = 400 + offset
                base_y = y_pos + 50 + i * 5
                tip_y = base_y + 20 + datos['potencia'] * 0.3
                
                self.canvas_visualizacion.coords(llama, 
                                               base_x1, base_y,
                                               tip_x, tip_y,
                                               base_x2, base_y)
                self.canvas_visualizacion.itemconfig(llama, fill=f"#ff{max(0, 255 - i*50):02x}00")
        else:
            for llama in self.llamas:
                self.canvas_visualizacion.coords(llama, 0, 0, 0, 0)
    
    def _update_control_buttons(self, datos):
        """Actualiza el estado de los botones de control"""
        estado_propulsores = datos['propulsores']
        self.boton_propulsor.config(
            text="DESACTIVAR PROPULSORES" if estado_propulsores else "ACTIVAR PROPULSORES",
            style="Peligro.TButton" if estado_propulsores else "Info.TButton"
        )
        
        self.boton_tren.state(['!disabled' if datos['altitud'] < 100 and not datos['tren'] else 'disabled'])
        
        # Actualizar slider de potencia
        if not self.slider_potencia.winfo_ismapped() or self.slider_potencia.get() != datos['potencia']:
            self.slider_potencia.set(datos['potencia'])
            self.label_potencia.config(text=f"Potencia propulsores: {int(datos['potencia'])}%")
    
    def _update_console(self, datos):
        """Actualiza la consola con nuevos mensajes"""
        self.consola.configure(state="normal")
        
        # Añadir mensajes importantes
        if datos['altitud'] < 10 and datos['velocidad'] < -15 and not datos['abortado']:
            self.consola.insert("end", f"ALERTA: Velocidad de descenso peligrosa! {datos['velocidad']:.1f} m/s\n", "danger")
        
        if datos['combustible'] < 10 and not datos['abortado']:
            self.consola.insert("end", f"ALERTA: Combustible crítico! {datos['combustible']:.1f}%\n", "danger")
        
        if datos['abortado'] and len(self.controller.modelo.telemetria) < 2:
            self.consola.insert("end", "MISIÓN ABORTADA: Activando secuencia de emergencia\n", "danger")
        
        # Limitar tamaño de la consola
        lineas = self.consola.get("1.0", "end").split('\n')
        if len(lineas) > 100:
            self.consola.delete("1.0", f"{len(lineas)-80}.0")
        
        self.consola.see("end")
        self.consola.configure(state="disabled")
    
    def _update_systems_status(self, datos):
        """Actualiza el estado de los sistemas"""
        # Simular cambios en el estado de los sistemas
        sistemas = [
            ("propulsion", datos['combustible'] > 5 and not datos['abortado']),
            ("navegacion", datos['altitud'] > 0),
            ("comunicaciones", True),
            ("computadora", True),
            ("sensores", datos['temperatura'] < 280),
            ("energia", True),
            ("guia", datos['altitud'] > 10),
            ("control", True)
        ]
        
        for sistema_id, estado in sistemas:
            canvas, color_original = self.indicadores_sistema[sistema_id]
            color = color_original if estado else "red"
            canvas.delete("all")
            canvas.create_oval(2, 2, 18, 18, fill=color)
    
    def _update_alerts(self, datos):
        """Actualiza la lista de alertas"""
        # Mostrar alertas del modelo
        for alerta, critico in datos.get('alertas', []):
            timestamp = time.strftime("%H:%M:%S", time.gmtime(time.time() - datos['tiempo_inicio']))
            if critico:
                self.lista_alertas.insert("end", f"[{timestamp}] {alerta}")
                self.lista_alertas.itemconfig("end", fg="#dc3545")  # Rojo para peligro
                self.root.bell()  # Sonido de alerta
            else:
                self.lista_alertas.insert("end", f"[{timestamp}] {alerta}")
                self.lista_alertas.itemconfig("end", fg="#ffc107")  # Amarillo para advertencia
            self.lista_alertas.see("end")
    
    def _update_pid_values(self, datos):
        """Actualiza los valores PID mostrados"""
        self.var_kp.set(f"{datos['pid']['Kp']:.2f}")
        self.var_ki.set(f"{datos['pid']['Ki']:.2f}")
        self.var_kd.set(f"{datos['pid']['Kd']:.2f}")
    
    def show_alert(self, mensaje, critico=False):
        """Muestra una alerta en la interfaz"""
        timestamp = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.controller.modelo.tiempo_inicio))
        if critico:
            self.lista_alertas.insert("end", f"[{timestamp}] {mensaje}")
            self.lista_alertas.itemconfig("end", fg="#dc3545")
            self.root.bell()  # Sonido de alerta
            messagebox.showerror("Alerta Crítica", mensaje)
        else:
            self.lista_alertas.insert("end", f"[{timestamp}] {mensaje}")
            self.lista_alertas.itemconfig("end", fg="#ffc107")
        self.lista_alertas.see("end")
    
    def _show_credits(self):
        """Muestra los créditos en la parte inferior"""
        marco_creditos = ttk.Frame(self.root, style="Creditos.TLabel")
        marco_creditos.pack(side="bottom", fill="x")
        
        texto_creditos = "Desarrollado por: Jorge Luis Angulo Cordova y Gerardo Gamboa Nuñez | © 2023 Sistema de Control de Cohetes"
        label_creditos = ttk.Label(marco_creditos, text=texto_creditos, style="Creditos.TLabel")
        label_creditos.pack(pady=5)

class ControladorCohete:
    def __init__(self, root):
        self.modelo = ModeloCohete()
        self.vista = VistaCohete(root)
        self.vista.controller = self
        
        # Inicializar la base de datos
        self.db = CoheteDatabase()
        
        # Configurar eventos
        self._setup_bindings()
        
        # Iniciar actualización periódica
        self._start_data_update()
    
    def _setup_bindings(self):
        """Configura los eventos de la interfaz"""
        self.vista.slider_kp.bind("<ButtonRelease-1>", lambda e: self.ajustar_pid())
        self.vista.slider_ki.bind("<ButtonRelease-1>", lambda e: self.ajustar_pid())
        self.vista.slider_kd.bind("<ButtonRelease-1>", lambda e: self.ajustar_pid())
    
    def _start_data_update(self):
        """Inicia el ciclo de actualización de datos"""
        self.update_data()
    
    def update_data(self):
        """Actualiza los datos del modelo y la vista"""
        try:
            datos = self.modelo.actualizar_datos()
            
            # Guardar datos en la base de datos
            self.db.insert_telemetry(datos)
            
            # Guardar alertas nuevas
            for alerta, critico in datos.get('alertas', []):
                if alerta not in [a[0] for a in self.modelo.alertas[:-1]]:  # Solo nuevas alertas
                    self.db.insert_alert(alerta, critico)
            
            self.vista.root.after(0, lambda: self.vista.update_view(datos))
            self.vista.root.after(200, self.update_data)
        except Exception as e:
            logger.error(f"Error en actualización de datos: {e}")
            self.vista.root.after(1000, self.update_data)
    
    def toggle_propulsores(self):
        """Alterna el estado de los propulsores"""
        estado_actual = self.modelo.estado_propulsores
        self.modelo.activar_propulsores(not estado_actual)
    
    def desplegar_tren(self):
        """Intenta desplegar el tren de aterrizaje"""
        if self.modelo.desplegar_tren():
            self.vista.show_alert("Tren de aterrizaje desplegado con éxito", False)
        else:
            self.vista.show_alert("No se puede desplegar el tren a esta altitud", False)
    
    def abortar_mision(self):
        """Inicia la secuencia de aborto de misión"""
        if messagebox.askyesno("Abortar Misión", "¿Está seguro de que desea abortar la misión?"):
            self.modelo.abortar_mision()
            self.vista.show_alert("¡MISIÓN ABORTADA!", True)
    
    def ajustar_potencia(self, potencia):
        """Ajusta la potencia de los propulsores"""
        self.modelo.ajustar_potencia(potencia)
    
    def ajustar_pid(self):
        """Ajusta los parámetros PID según los sliders"""
        Kp = self.vista.slider_kp.get()
        Ki = self.vista.slider_ki.get()
        Kd = self.vista.slider_kd.get()
        self.modelo.ajustar_pid(Kp, Ki, Kd)
        
        # Registrar cambio en la base de datos
        self.db.insert_pid_config(Kp, Ki, Kd, "Ajuste manual desde GUI")
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación a los valores iniciales"""
        if messagebox.askyesno("Reiniciar Simulación", "¿Está seguro de que desea reiniciar la simulación?"):
            self.modelo.reiniciar_simulacion()
            self.vista.show_alert("Simulación reiniciada", True)

class CoheteDatabase:
    def __init__(self, db_name='cohete_data.db'):
        """Inicializa la base de datos y crea las tablas necesarias"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Crea las tablas en la base de datos si no existen"""
        # Tabla principal de telemetría
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            altitud REAL,
            velocidad REAL,
            orientacion REAL,
            temperatura REAL,
            aceleracion REAL,
            presion REAL,
            combustible REAL,
            potencia_propulsores REAL,
            estado_propulsores BOOLEAN,
            tren_desplegado BOOLEAN,
            mision_abortada BOOLEAN,
            Kp REAL,
            Ki REAL,
            Kd REAL
        )
        ''')
        
        # Tabla de alertas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mensaje TEXT,
            critica BOOLEAN
        )
        ''')
        
        # Tabla de configuraciones PID
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuraciones_pid (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Kp REAL,
            Ki REAL,
            Kd REAL,
            comentario TEXT
        )
        ''')
        
        self.conn.commit()
    
    def insert_telemetry(self, data):
        """Inserta un registro de telemetría en la base de datos"""
        query = '''
        INSERT INTO telemetria (
            altitud, velocidad, orientacion, temperatura, aceleracion,
            presion, combustible, potencia_propulsores, estado_propulsores,
            tren_desplegado, mision_abortada, Kp, Ki, Kd
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            data['altitud'], data['velocidad'], data['orientacion'], 
            data['temperatura'], data['aceleracion'], data['presion'],
            data['combustible'], data['potencia'], data['propulsores'],
            data['tren'], data['abortado'], data['pid']['Kp'],
            data['pid']['Ki'], data['pid']['Kd']
        )
        
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def insert_alert(self, mensaje, critica=False):
        """Registra una alerta en la base de datos"""
        query = 'INSERT INTO alertas (mensaje, critica) VALUES (?, ?)'
        self.cursor.execute(query, (mensaje, critica))
        self.conn.commit()
    
    def insert_pid_config(self, Kp, Ki, Kd, comentario=""):
        """Registra un cambio en la configuración PID"""
        query = '''
        INSERT INTO configuraciones_pid (Kp, Ki, Kd, comentario)
        VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (Kp, Ki, Kd, comentario))
        self.conn.commit()
    
    def get_last_telemetry(self, limit=10):
        """Obtiene los últimos registros de telemetría"""
        query = 'SELECT * FROM telemetria ORDER BY timestamp DESC LIMIT ?'
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()
    
    def get_alerts(self, limit=10, only_critical=False):
        """Obtiene las alertas registradas"""
        if only_critical:
            query = 'SELECT * FROM alertas WHERE critica=1 ORDER BY timestamp DESC LIMIT ?'
        else:
            query = 'SELECT * FROM alertas ORDER BY timestamp DESC LIMIT ?'
        
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()
    
    def get_pid_config_history(self, limit=5):
        """Obtiene el historial de configuraciones PID"""
        query = 'SELECT * FROM configuraciones_pid ORDER BY timestamp DESC LIMIT ?'
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        self.conn.close()
    
    def __del__(self):
        """Destructor que cierra la conexión"""
        self.close()

def main():
    root = tk.Tk()
    try:
        app = ControladorCohete(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        messagebox.showerror("Error", f"Se produjo un error fatal: {e}")
    finally:
        if 'app' in locals():
            app.vista._on_window_close()
            app.db.close()  # Asegurar que la BD se cierre correctamente

if __name__ == "__main__":
    main()