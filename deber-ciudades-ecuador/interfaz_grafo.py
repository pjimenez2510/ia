# Importación de módulos de tkinter para la interfaz gráfica
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# Importación de módulos para manejo de datos y visualización
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx

# Importación de módulos del sistema
import sys
import os

# Agregar el directorio actual al path de Python para poder importar módulos locales
# Esto es necesario para importar los módulos grafo_ecuador y base_datos_rutas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importación de módulos locales
from grafo_ecuador import GrafoEcuador
from base_datos_rutas import BaseDatosRutas

class AplicacionRutas:
    """
        Clase principal que implementa la interfaz gráfica para el sistema de rutas de Ecuador.

        Esta clase proporciona una interfaz de usuario completa que permite:
        - Visualizar el grafo de ciudades y rutas
        - Buscar rutas entre ciudades usando diferentes algoritmos
        - Gestionar ciudades y conexiones
        - Importar/exportar datos en formato JSON
        - Interactuar con el mapa de forma intuitiva

        La interfaz está dividida en:
        - Panel izquierdo: Controles y opciones
        - Panel derecho: Visualización del grafo/mapa
    """
    
    def __init__(self, root):
        """
            Inicializa la aplicación con la ventana principal.
            
            Args:
                root (tk.Tk): Ventana principal de la aplicación.
                
            Configura:
            - Título y tamaño de la ventana
            - Conexión a la base de datos
            - Inicialización del grafo
            - Variables de control de la interfaz
            - Configuración de la interfaz gráfica
        """
        self.root = root
        self.root.title("Sistema de Rutas de Ecuador")
        self.root.geometry("1200x700")
        
        # Inicializar conexión a la base de datos
        self.db = BaseDatosRutas('rutas_ecuador.db')
        
        # Inicializar el grafo
        self.grafo = GrafoEcuador()
        
        # Sincronizar el grafo con la base de datos
        self.sincronizar_grafo_bd()
        
        # Variables de control para la interfaz
        self.ciudad_origen_var = tk.StringVar()
        self.ciudad_destino_var = tk.StringVar()
        self.algoritmo_var = tk.StringVar(value="Búsqueda A*")
        self.mapa_real_var = tk.BooleanVar(value=True)
        
        # Variables de estado
        self.ruta_actual = None
        self.ciudad_seleccionada = None
        self.ultima_figura = None
        
        # Configurar la interfaz gráfica
        self.configurar_interfaz()
    
    def sincronizar_grafo_bd(self):
        """
            Sincroniza el grafo en memoria con la base de datos.
            
            Este método maneja dos escenarios:
            1. Si la base de datos está vacía:
                - Importa el grafo predeterminado a la base de datos
                - Muestra un mensaje informativo al usuario
            2. Si la base de datos ya tiene datos:
                - Carga el grafo y las coordenadas desde la base de datos
                - Actualiza el grafo en memoria con los datos de la BD
                - Actualiza la lista de ciudades
            
            El proceso asegura que el grafo en memoria y la base de datos estén
            siempre sincronizados, manteniendo la consistencia de los datos.
        """
        # Obtener lista de ciudades desde la base de datos
        ciudades = self.db.listar_ciudades()
        
        if not ciudades:
            # Caso 1: Base de datos vacía - inicializar con grafo predeterminado
            grafo_dict = self.grafo.grafo
            # Preparar diccionario de coordenadas en formato para la BD
            coords_dict = {ciudad: {"lat": lat, "lng": lng} 
                          for ciudad, (lat, lng) in self.grafo.coordenadas.items()}
            
            # Importar grafo predeterminado a la base de datos
            self.db.importar_grafo(grafo_dict, coords_dict)
            messagebox.showinfo("Información", "Base de datos inicializada con el grafo predeterminado.")
        else:
            # Caso 2: Cargar datos existentes de la base de datos
            grafo_dict, coords_dict = self.db.obtener_grafo_completo_con_coords()
            # Actualizar grafo en memoria
            self.grafo.grafo = grafo_dict
            # Convertir coordenadas al formato del grafo
            self.grafo.coordenadas = {ciudad: (datos["lat"], datos["lng"]) 
                                    for ciudad, datos in coords_dict.items() 
                                    if datos["lat"] is not None and datos["lng"] is not None}
            # Actualizar lista de ciudades
            self.grafo.ciudades = list(self.grafo.grafo.keys())
    
    def configurar_interfaz(self):
        """
            Configura la interfaz gráfica de la aplicación.
            
            La interfaz se divide en dos paneles principales:
            1. Panel izquierdo:
                - Controles de búsqueda (origen, destino, algoritmo)
                - Opciones de visualización
                - Información de rutas
                - Gestión de datos
            
            2. Panel derecho:
                - Visualización del grafo/mapa
                - Herramientas de navegación
                - Interacción con el mapa
            
            El método configura:
            - Estructura de paneles y frames
            - Widgets de control
            - Visualización del grafo
            - Eventos de interacción
            - Menús contextuales
        """
        # Crear panel principal dividido en dos secciones
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo para controles
        panel_izquierdo = ttk.Frame(panel_principal, width=300)
        panel_principal.add(panel_izquierdo, weight=1)
        
        # Panel derecho para visualización
        panel_derecho = ttk.Frame(panel_principal)
        panel_principal.add(panel_derecho, weight=3)
        
        # Configurar notebook para pestañas en panel izquierdo
        self.notebook = ttk.Notebook(panel_izquierdo)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Búsqueda
        panel_busqueda = ttk.Frame(self.notebook)
        self.notebook.add(panel_busqueda, text="Búsqueda")
        
        # Configurar controles de búsqueda
        ttk.Label(panel_busqueda, text="Seleccione la ciudad de origen:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_origen = ttk.Combobox(panel_busqueda, textvariable=self.ciudad_origen_var, 
                                     values=self.grafo.listar_ciudades())
        self.combo_origen.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(panel_busqueda, text="Seleccione la ciudad de destino:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_destino = ttk.Combobox(panel_busqueda, textvariable=self.ciudad_destino_var, 
                                      values=self.grafo.listar_ciudades())
        self.combo_destino.pack(fill=tk.X, padx=5, pady=5)
        
        # Configurar selector de algoritmo
        ttk.Label(panel_busqueda, text="Seleccione el algoritmo de búsqueda:").pack(pady=(10, 5), anchor=tk.W)
        algoritmos = ["Búsqueda en Amplitud", "Búsqueda en Profundidad", 
                     "Búsqueda de Costo Uniforme", "Búsqueda A*"]
        self.combo_algoritmo = ttk.Combobox(panel_busqueda, textvariable=self.algoritmo_var, 
                                        values=algoritmos, state="readonly")
        self.combo_algoritmo.pack(fill=tk.X, padx=5, pady=5)
        
        # Configurar opción de mapa real
        ttk.Checkbutton(panel_busqueda, text="Usar mapa real", variable=self.mapa_real_var,
                       command=self.actualizar_visualizacion).pack(pady=5)
        
        # Botón de búsqueda
        ttk.Button(panel_busqueda, text="Buscar Ruta", command=self.buscar_ruta).pack(pady=20)
        
        # Panel de información de ruta
        self.marco_info = ttk.LabelFrame(panel_busqueda, text="Información de la Ruta")
        self.marco_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_ruta_text = tk.Text(self.marco_info, height=10, wrap=tk.WORD)
        self.info_ruta_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de Gestión
        panel_gestion = ttk.Frame(self.notebook)
        self.notebook.add(panel_gestion, text="Gestión")
        
        # Configurar gestión de ciudades
        marco_ciudades = ttk.LabelFrame(panel_gestion, text="Gestión de Ciudades")
        marco_ciudades.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_ciudades, text="Agregar Ciudad", 
                  command=self.agregar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_ciudades, text="Editar Ciudad", 
                  command=self.editar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_ciudades, text="Eliminar Ciudad", 
                  command=self.eliminar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        
        # Configurar gestión de rutas
        marco_rutas = ttk.LabelFrame(panel_gestion, text="Gestión de Rutas")
        marco_rutas.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_rutas, text="Agregar Conexión", 
                  command=self.agregar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_rutas, text="Editar Conexión", 
                  command=self.editar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_rutas, text="Eliminar Conexión", 
                  command=self.eliminar_conexion).pack(fill=tk.X, padx=5, pady=5)
        
        # Configurar gestión de base de datos
        marco_bd = ttk.LabelFrame(panel_gestion, text="Gestión de Base de Datos")
        marco_bd.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_bd, text="Importar desde JSON", 
                  command=self.importar_json).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_bd, text="Exportar a JSON", 
                  command=self.exportar_json).pack(fill=tk.X, padx=5, pady=5)
        
        # Panel de ayuda
        marco_ayuda = ttk.LabelFrame(panel_gestion, text="Ayuda Mapa Interactivo")
        marco_ayuda.pack(fill=tk.X, padx=5, pady=5)
        
        ayuda_text = (
            "- Haga clic en una ciudad para ver información\n"
            "- Para seleccionar origen/destino, haga clic y use 'Establecer como...' en el menú\n"
            "- Use las herramientas de navegación para zoom y desplazamiento\n"
            "- Active 'Usar mapa real' para ver ubicaciones geográficas reales"
        )
        ttk.Label(marco_ayuda, text=ayuda_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # Configurar visualización del grafo en panel derecho
        self.figura = plt.Figure(figsize=(7, 6))
        self.ax = self.figura.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figura, panel_derecho)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Agregar barra de herramientas de navegación
        self.toolbar_frame = ttk.Frame(panel_derecho)
        self.toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        
        # Configurar eventos de interacción con el mapa
        self.canvas.mpl_connect('button_press_event', self.on_click_mapa)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover_mapa)
        
        # Visualizar el grafo inicial
        self.visualizar_grafo()
    
    def on_click_mapa(self, event):
        """
            Maneja el evento de clic en el mapa.
            
            Este método se ejecuta cuando el usuario hace clic en el área del mapa.
            Realiza las siguientes acciones:
            1. Verifica si el clic es válido (coordenadas dentro del mapa y botón izquierdo)
            2. Encuentra la ciudad más cercana al punto de clic
            3. Si se encuentra una ciudad, muestra el menú contextual
            
            Args:
                event (matplotlib.backend_bases.MouseEvent): Evento de clic del mouse
                    que contiene las coordenadas del clic y otra información relevante.
        """
        # Verificar si el clic es válido (dentro del mapa y botón izquierdo)
        if event.xdata is None or event.ydata is None or event.button != 1:
            return
        
        # Buscar la ciudad más cercana al punto de clic
        usar_mapa_real = self.mapa_real_var.get()
        ciudad_cercana = self.encontrar_ciudad_cercana(event.xdata, event.ydata, usar_mapa_real)
        
        # Si se encontró una ciudad cercana, mostramos el menú contextual
        if ciudad_cercana:
            self.ciudad_seleccionada = ciudad_cercana
            self.mostrar_menu_ciudad(event)
    
    def encontrar_ciudad_cercana(self, x, y, usar_mapa_real):
        """
            Encuentra la ciudad más cercana a un punto dado en el mapa.
            
            Este método calcula la distancia entre el punto de clic y cada ciudad
            en el grafo, considerando si se está usando el mapa real o la vista
            abstracta del grafo.
            
            Args:
                x (float): Coordenada x del punto de clic
                y (float): Coordenada y del punto de clic
                usar_mapa_real (bool): Indica si se está usando el mapa real o la vista abstracta
                
            Returns:
                str or None: Nombre de la ciudad más cercana si está dentro del umbral,
                            None si no hay ciudades cercanas al punto de clic.
        """
        ciudad_mas_cercana = None
        distancia_minima = float('inf')
        
        # Crear grafo de NetworkX para calcular posiciones
        G = nx.Graph()
        for origen in self.grafo.grafo:
            G.add_node(origen)
        
        # Obtener posiciones según el modo de visualización
        if usar_mapa_real:
            # Usar coordenadas reales (longitud, latitud)
            pos = {ciudad: (lon, lat) for ciudad, (lat, lon) in self.grafo.coordenadas.items() 
                  if ciudad in self.grafo.grafo}
        else:
            # Usar layout automático para vista abstracta
            pos = nx.spring_layout(G, seed=42)
        
        # Calcular distancia a cada ciudad
        for ciudad, (px, py) in pos.items():
            distancia = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
            if distancia < distancia_minima:
                distancia_minima = distancia
                ciudad_mas_cercana = ciudad
        
        # Definir umbral según el modo de visualización
        umbral = 0.05 if usar_mapa_real else 0.1
        return ciudad_mas_cercana if distancia_minima < umbral else None
        
    def mostrar_menu_ciudad(self, event):
        
        """
            Muestra un menú contextual con opciones para la ciudad seleccionada.
            
            El menú incluye:
            - Información de la ciudad seleccionada
            - Opciones para establecer como origen/destino
            - Opción para ver conexiones
            - Opción para editar la ciudad
            - Coordenadas geográficas (si están disponibles)
            
            Args:
                event (matplotlib.backend_bases.MouseEvent): Evento que disparó el menú,
                    usado para posicionar el menú en la pantalla.
        """
        # Crear menú contextual
        menu = tk.Menu(self.root, tearoff=0)
        
        # Agregar título con nombre de la ciudad
        menu.add_command(label=f"Ciudad: {self.ciudad_seleccionada}", state=tk.DISABLED)
        menu.add_separator()
        
        # Agregar opciones principales
        menu.add_command(label="Establecer como Origen", command=self.establecer_como_origen)
        menu.add_command(label="Establecer como Destino", command=self.establecer_como_destino)
        menu.add_separator()
        
        # Agregar opciones de gestión
        menu.add_command(label="Ver Conexiones", command=self.ver_conexiones)
        menu.add_command(label="Editar Ciudad", command=self.editar_ciudad_seleccionada)

        # Mostrar coordenadas si están disponibles
        if self.ciudad_seleccionada in self.grafo.coordenadas:
            lat, lon = self.grafo.coordenadas[self.ciudad_seleccionada]
            menu.add_separator()
            menu.add_command(label=f"Lat: {lat:.4f}, Lon: {lon:.4f}", state=tk.DISABLED)

        # Obtener el widget Tkinter del canvas de matplotlib
        canvas_widget = self.canvas.get_tk_widget()

        # Calcular la posición correcta para el menú
        x = canvas_widget.winfo_rootx() + event.x
        y = canvas_widget.winfo_rooty() + event.y

        # Mostrar el menú en la posición calculada
        menu.tk_popup(x, y)
    
    def establecer_como_origen(self):
        """
            Establece la ciudad seleccionada como punto de origen para la búsqueda de rutas.
            
            Este método:
            1. Actualiza la variable de control de origen con la ciudad seleccionada
            2. Cambia a la pestaña de búsqueda para facilitar la selección del destino
            3. Permite al usuario continuar con la configuración de la ruta
            
            Nota: Este método se llama desde el menú contextual de una ciudad.
        """
        if self.ciudad_seleccionada:
            # Actualizar variable de control con la ciudad seleccionada
            self.ciudad_origen_var.set(self.ciudad_seleccionada)
            # Cambiar a la pestaña de búsqueda para facilitar la selección del destino
            self.notebook.select(0)
    
    def establecer_como_destino(self):
        """
            Establece la ciudad seleccionada como punto de destino para la búsqueda de rutas.
            
            Este método:
            1. Actualiza la variable de control de destino con la ciudad seleccionada
            2. Cambia a la pestaña de búsqueda para facilitar la selección del origen
            3. Permite al usuario continuar con la configuración de la ruta
            
            Nota: Este método se llama desde el menú contextual de una ciudad.
        """
        if self.ciudad_seleccionada:
            # Actualizar variable de control con la ciudad seleccionada
            self.ciudad_destino_var.set(self.ciudad_seleccionada)
            # Cambiar a la pestaña de búsqueda para facilitar la selección del origen
            self.notebook.select(0)
    
    def on_hover_mapa(self, event):
        """
            Maneja el evento de movimiento del mouse sobre el mapa.
            
            Este método proporciona retroalimentación visual al usuario cuando
            el mouse pasa sobre una ciudad en el mapa:
            1. Muestra el nombre de la ciudad en el título del mapa
            2. Cambia el cursor a una mano para indicar que la ciudad es clickeable
            3. Restaura el título original cuando el mouse sale de la ciudad
            
            Args:
                event (matplotlib.backend_bases.MouseEvent): Evento de movimiento del mouse
                    que contiene las coordenadas actuales del cursor.
        """
        if event.xdata is None or event.ydata is None:
            return
        
        # Obtener modo de visualización actual
        usar_mapa_real = self.mapa_real_var.get()
        # Encontrar ciudad más cercana al cursor
        ciudad = self.encontrar_ciudad_cercana(event.xdata, event.ydata, usar_mapa_real)
        
        if ciudad:
            # Cambiar cursor a mano para indicar que es clickeable
            self.canvas.get_tk_widget().config(cursor="hand2")
            
            # Mostrar nombre de la ciudad en el título
            self.ax.set_title(f"Ciudad: {ciudad}")
            self.canvas.draw_idle()
        else:
            # Restaurar cursor normal
            self.canvas.get_tk_widget().config(cursor="")
            
            # Restaurar título original según el contexto
            if self.ruta_actual:
                self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador - Ruta Encontrada")
            else:
                self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
            self.canvas.draw_idle()
    
    def ver_conexiones(self):
        """
            Muestra una ventana con la lista de conexiones de la ciudad seleccionada.
            
            Este método:
            1. Verifica que haya una ciudad seleccionada
            2. Obtiene todas las conexiones de la ciudad desde el grafo
            3. Muestra una ventana con una tabla que incluye:
            - Nombre de la ciudad destino
            - Distancia en kilómetros
            4. Permite al usuario ver rápidamente todas las rutas disponibles
            
            La ventana incluye:
            - Título con el nombre de la ciudad
            - Tabla con conexiones y distancias
            - Barra de desplazamiento para muchas conexiones
            - Botón para cerrar la ventana
        """
        if not self.ciudad_seleccionada:
            return
        
        # Obtener conexiones de la ciudad seleccionada
        conexiones = self.grafo.listar_conexiones(self.ciudad_seleccionada)
        if not conexiones:
            messagebox.showinfo("Conexiones", f"La ciudad {self.ciudad_seleccionada} no tiene conexiones.")
            return
        
        # Crear ventana para mostrar conexiones
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Conexiones desde {self.ciudad_seleccionada}")
        ventana.geometry("400x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Agregar título
        ttk.Label(ventana, text=f"Conexiones desde {self.ciudad_seleccionada}:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Crear frame para la tabla
        frame = ttk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Agregar barra de desplazamiento
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Crear tabla de conexiones
        treeview = ttk.Treeview(frame, columns=("ciudad", "distancia"), show="headings")
        treeview.heading("ciudad", text="Ciudad")
        treeview.heading("distancia", text="Distancia (km)")
        treeview.column("ciudad", width=200)
        treeview.column("distancia", width=100)
        
        # Agregar conexiones a la tabla
        for ciudad, distancia in sorted(conexiones.items()):
            treeview.insert("", "end", values=(ciudad, distancia))
        
        # Configurar scrollbar y mostrar tabla
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=scrollbar.set)
        
        # Agregar botón para cerrar
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    
    def editar_ciudad_seleccionada(self):
        """
        Inicia el proceso de edición de la ciudad actualmente seleccionada en el mapa.
        
        Este método:
        1. Verifica que haya una ciudad seleccionada
        2. Llama al método editar_ciudad con la ciudad seleccionada
        3. Permite al usuario modificar los datos de la ciudad
        
        Nota: Este método se llama desde el menú contextual de una ciudad.
        """
        if self.ciudad_seleccionada:
            self.editar_ciudad(self.ciudad_seleccionada)
    
    def buscar_ruta(self):
        """
        Busca una ruta entre dos ciudades seleccionadas usando el algoritmo especificado.
        
        Este método:
        1. Obtiene las ciudades de origen y destino seleccionadas
        2. Obtiene el algoritmo de búsqueda seleccionado
        3. Verifica que se hayan seleccionado ciudades diferentes
        4. Ejecuta el algoritmo de búsqueda correspondiente:
           - Búsqueda en Amplitud
           - Búsqueda en Profundidad
           - Búsqueda A*
           - Búsqueda de Costo Uniforme
        5. Si se encuentra una ruta:
           - Actualiza la ruta actual
           - Muestra la información de la ruta
           - Visualiza el grafo con la ruta resaltada
        6. Si no se encuentra ruta, muestra un mensaje de error
        
        Nota: Este método se llama cuando el usuario presiona el botón de búsqueda.
        """
        origen = self.ciudad_origen_var.get()
        destino = self.ciudad_destino_var.get()
        algoritmo = self.algoritmo_var.get()
        
        if not origen or not destino:
            messagebox.showerror("Error", "Debe seleccionar ciudad de origen y destino.")
            return
        
        if origen == destino:
            messagebox.showinfo("Información", "El origen y destino son la misma ciudad.")
            return
        
        if algoritmo == "Búsqueda en Amplitud":
            ruta, distancia = self.grafo.busqueda_amplitud(origen, destino)
        elif algoritmo == "Búsqueda en Profundidad":
            ruta, distancia = self.grafo.busqueda_profundidad(origen, destino)
        elif algoritmo == "Búsqueda A*":
            ruta, distancia = self.grafo.busqueda_a_estrella(origen, destino)
        else:
            ruta, distancia = self.grafo.busqueda_costo_uniforme(origen, destino)
        
        if ruta:
            self.ruta_actual = ruta
            self.mostrar_info_ruta(ruta, distancia, algoritmo)
            self.visualizar_grafo(ruta)
        else:
            messagebox.showerror("Error", f"No se encontró ruta entre {origen} y {destino}.")
    
    def mostrar_info_ruta(self, ruta, distancia, algoritmo):
        """
        Muestra información detallada sobre la ruta encontrada en el área de texto de la interfaz.
        
        Este método:
        1. Limpia el área de texto actual
        2. Muestra el algoritmo utilizado para encontrar la ruta
        3. Muestra las ciudades de origen y destino
        4. Muestra la distancia total de la ruta
        5. Si las ciudades tienen coordenadas, calcula y muestra:
           - La distancia en línea recta entre origen y destino
           - El factor de desvío (distancia real / distancia en línea recta)
        6. Muestra la ruta completa con las distancias entre cada par de ciudades
        
        Parámetros:
            ruta (list): Lista de ciudades que forman la ruta
            distancia (float): Distancia total de la ruta en kilómetros
            algoritmo (str): Nombre del algoritmo utilizado para encontrar la ruta
        """
        self.info_ruta_text.delete(1.0, tk.END)
        
        self.info_ruta_text.insert(tk.END, f"Algoritmo: {algoritmo}\n\n")
        self.info_ruta_text.insert(tk.END, f"Origen: {ruta[0]}\n")
        self.info_ruta_text.insert(tk.END, f"Destino: {ruta[-1]}\n")
        self.info_ruta_text.insert(tk.END, f"Distancia total: {distancia} km\n\n")
        
        # Calcular distancia en línea recta si hay coordenadas
        if ruta[0] in self.grafo.coordenadas and ruta[-1] in self.grafo.coordenadas:
            dist_linea_recta = self.grafo.obtener_distancia_linea_recta(ruta[0], ruta[-1])
            factor_desvio = distancia / dist_linea_recta if dist_linea_recta > 0 else "N/A"
            
            self.info_ruta_text.insert(tk.END, f"Distancia en línea recta: {dist_linea_recta:.2f} km\n")
            self.info_ruta_text.insert(tk.END, f"Factor de desvío: {factor_desvio:.2f}\n\n")
        
        self.info_ruta_text.insert(tk.END, "Ruta completa:\n")
        for i in range(len(ruta) - 1):
            dist = self.grafo.obtener_distancia(ruta[i], ruta[i+1])
            self.info_ruta_text.insert(tk.END, f"{ruta[i]} → {ruta[i+1]} ({dist} km)\n")
    
    def actualizar_visualizacion(self):
        """
        Actualiza la visualización del grafo con la configuración actual.
        
        Este método:
        1. Llama a visualizar_grafo con la ruta actual
        2. Permite actualizar la vista cuando:
           - Se cambia el modo de visualización (mapa real/abstracto)
           - Se encuentra una nueva ruta
           - Se modifican las conexiones del grafo
        
        Nota: Este método se llama automáticamente cuando hay cambios en la visualización.
        """
        self.visualizar_grafo(self.ruta_actual)
    
    def visualizar_grafo(self, ruta=None):
        """
        Visualiza el grafo en el panel derecho de la interfaz.
        
        Este método:
        1. Limpia el área de visualización actual
        2. Obtiene el modo de visualización seleccionado (mapa real o abstracto)
        3. Llama al método de visualización del grafo con los parámetros adecuados
        4. Actualiza el título del gráfico según si hay una ruta resaltada
        5. Redibuja el canvas para mostrar los cambios
        
        Parámetros:
            ruta (list, optional): Lista de ciudades que forman la ruta a resaltar.
                Si se proporciona, la ruta se mostrará de manera destacada en el grafo.
        """
        self.ax.clear()
        
        usar_mapa_real = self.mapa_real_var.get()
        self.grafo.visualizar_grafo(ruta, usar_mapa_real=usar_mapa_real, ax=self.ax)
        
        if ruta:
            self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador - Ruta Encontrada")
        else:
            self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
        
        self.canvas.draw()
    
    def agregar_ciudad(self):
        """
        Abre un diálogo para agregar una nueva ciudad al grafo.
        
        Este método:
        1. Crea una ventana de diálogo con campos para:
           - Nombre de la ciudad
           - Latitud
           - Longitud
        2. Valida los datos ingresados:
           - Verifica que el nombre no esté vacío
           - Verifica que las coordenadas sean números válidos
           - Verifica que la ciudad no exista previamente
        3. Si los datos son válidos:
           - Agrega la ciudad a la base de datos
           - Actualiza el grafo en memoria
           - Actualiza las listas de ciudades en la interfaz
           - Visualiza el grafo actualizado
        4. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Agregar Ciudad".
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Ciudad")
        ventana.geometry("400x200")
        ventana.transient(self.root)
        ventana.grab_set()
        
        nombre_var = tk.StringVar()
        latitud_var = tk.StringVar()
        longitud_var = tk.StringVar()
        
        ttk.Label(ventana, text="Nombre de la ciudad:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=nombre_var).grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Latitud:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=latitud_var).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Longitud:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=longitud_var).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def guardar():
            """
            Función que guarda los datos de la ciudad agregada.
            
            Esta función:
            1. Obtiene los datos ingresados por el usuario
            2. Valida que el nombre de la ciudad no esté vacío
            3. Valida que las coordenadas sean números válidos
            4. Verifica que la ciudad no exista previamente
            5. Agrega la ciudad a la base de datos
            6. Actualiza el grafo en memoria
            7. Actualiza las listas de ciudades en la interfaz
            8. Visualiza el grafo actualizado
            
            Nota: Esta función se llama cuando el usuario presiona el botón "Guardar" en la ventana de diálogo.
            """
            nombre = nombre_var.get().strip()
            
            if not nombre:
                messagebox.showerror("Error", "Debe ingresar un nombre para la ciudad.")
                return
            
            try:
                latitud = float(latitud_var.get()) if latitud_var.get() else None
                longitud = float(longitud_var.get()) if longitud_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Los valores de latitud y longitud deben ser números.")
                return
            
            # Verificar que la ciudad no exista
            if nombre in self.grafo.grafo:
                messagebox.showerror("Error", f"La ciudad {nombre} ya existe.")
                return
            
            # Agregar ciudad a la base de datos
            ciudad_id = self.db.agregar_ciudad(nombre, latitud, longitud)
            
            if ciudad_id:
                # Agregar ciudad al grafo
                self.grafo.agregar_ciudad(nombre, latitud, longitud)
                
                # Actualizar listas de ciudades en la interfaz
                self.combo_origen.config(values=self.grafo.listar_ciudades())
                self.combo_destino.config(values=self.grafo.listar_ciudades())
                
                # Visualizar el grafo actualizado
                self.visualizar_grafo()
                
                messagebox.showinfo("Éxito", f"Ciudad {nombre} agregada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo agregar la ciudad a la base de datos.")
        
        ttk.Button(ventana, text="Guardar", command=guardar).grid(
            row=3, column=0, columnspan=2, pady=20)
    
    def editar_ciudad(self, ciudad_editar=None):
        """
        Abre un diálogo para editar una ciudad existente en el grafo.
        
        Este método:
        1. Crea una ventana de diálogo con campos para:
           - Selección de ciudad a editar
           - Nuevo nombre (opcional)
           - Latitud
           - Longitud
        2. Si se proporciona una ciudad específica:
           - Carga sus datos actuales en los campos
           - Bloquea la selección de ciudad
        3. Valida los datos ingresados:
           - Verifica que se haya seleccionado una ciudad
           - Verifica que las coordenadas sean números válidos
           - Verifica que el nuevo nombre no exista previamente
        4. Si los datos son válidos:
           - Actualiza las coordenadas en la base de datos
           - Actualiza el grafo en memoria
           - Visualiza el grafo actualizado
        5. Muestra mensajes de éxito o error según corresponda
        
        Parámetros:
            ciudad_editar (str, optional): Nombre de la ciudad a editar.
                Si se proporciona, se preselecciona esta ciudad en el diálogo.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Ciudad")
        ventana.geometry("400x250")
        ventana.transient(self.root)
        ventana.grab_set()
        
        nombre_var = tk.StringVar()
        ciudad_actual_var = tk.StringVar(value=ciudad_editar if ciudad_editar else "")
        latitud_var = tk.StringVar()
        longitud_var = tk.StringVar()
        
        # Si se proporciona una ciudad, cargar sus datos
        if ciudad_editar:
            lat, lon = self.grafo.coordenadas.get(ciudad_editar, (None, None))
            if lat is not None and lon is not None:
                latitud_var.set(str(lat))
                longitud_var.set(str(lon))
            nombre_var.set(ciudad_editar)
        
        ttk.Label(ventana, text="Seleccione la ciudad:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        if ciudad_editar:
            ttk.Label(ventana, text=ciudad_editar).grid(
                row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        else:
            combo_ciudad = ttk.Combobox(ventana, textvariable=ciudad_actual_var, 
                                    values=self.grafo.listar_ciudades())
            combo_ciudad.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
            
            def on_ciudad_select(event):
                ciudad = ciudad_actual_var.get()
                lat, lon = self.grafo.coordenadas.get(ciudad, (None, None))
                if lat is not None and lon is not None:
                    latitud_var.set(str(lat))
                    longitud_var.set(str(lon))
                nombre_var.set(ciudad)
            
            combo_ciudad.bind("<<ComboboxSelected>>", on_ciudad_select)
        
        ttk.Label(ventana, text="Nuevo nombre (opcional):").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=nombre_var).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Latitud:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=latitud_var).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Longitud:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=longitud_var).grid(
            row=3, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def guardar():
            """
            Función que guarda los datos de la ciudad editada.
            
            Esta función:
            1. Obtiene los datos ingresados por el usuario
            2. Valida que se haya seleccionado una ciudad
            3. Verifica que la ciudad exista en el grafo
            4. Valida que las coordenadas sean números válidos
            5. Si se quiere cambiar el nombre, verifica que no exista previamente
            6. Actualiza las coordenadas en la base de datos
            7. Actualiza el grafo en memoria
            8. Visualiza el grafo actualizado

            Nota: Esta función se llama cuando el usuario presiona el botón "Guardar" en la ventana de diálogo.
            """
            ciudad = ciudad_actual_var.get()
            nuevo_nombre = nombre_var.get().strip()
            
            if not ciudad:
                messagebox.showerror("Error", "Debe seleccionar una ciudad.")
                return
            
            # Verificar que la ciudad existe
            if ciudad not in self.grafo.grafo:
                messagebox.showerror("Error", f"La ciudad {ciudad} no existe.")
                return
            
            try:
                latitud = float(latitud_var.get()) if latitud_var.get() else None
                longitud = float(longitud_var.get()) if longitud_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Los valores de latitud y longitud deben ser números.")
                return
            
            # Si se quiere cambiar el nombre y ya existe
            if nuevo_nombre and nuevo_nombre != ciudad and nuevo_nombre in self.grafo.grafo:
                messagebox.showerror("Error", f"La ciudad {nuevo_nombre} ya existe.")
                return
            
            # Actualizamos coordenadas en la base de datos
            if latitud is not None and longitud is not None:
                self.db.actualizar_coordenadas(ciudad, latitud, longitud)
                
                # Actualizar coordenadas en el grafo
                self.grafo.coordenadas[ciudad] = (latitud, longitud)
            
            # Si se quiere cambiar el nombre
            if nuevo_nombre and nuevo_nombre != ciudad:
                # Esto requeriría más trabajo en un sistema real
                # Necesitaríamos actualizar todas las referencias en rutas, etc.
                messagebox.showinfo("Información", 
                                  "El cambio de nombre de ciudades no está implementado actualmente.")
            
            # Visualizar el grafo actualizado
            self.visualizar_grafo()
            
            messagebox.showinfo("Éxito", f"Ciudad {ciudad} actualizada correctamente.")
            ventana.destroy()
        
        ttk.Button(ventana, text="Guardar", command=guardar).grid(
            row=4, column=0, columnspan=2, pady=20)
    
    def eliminar_ciudad(self):
        """
        Abre un diálogo para eliminar una ciudad del grafo y la base de datos.
        
        Este método:
        1. Crea una ventana de diálogo con:
           - Un selector de ciudades disponibles
           - Un botón para confirmar la eliminación
        2. Valida los datos ingresados:
           - Verifica que se haya seleccionado una ciudad
           - Solicita confirmación del usuario antes de eliminar
        3. Si se confirma la eliminación:
           - Elimina la ciudad de la base de datos
           - Elimina la ciudad del grafo en memoria
           - Actualiza las listas de ciudades en la interfaz
           - Limpia la ruta actual si la ciudad eliminada era parte de ella
           - Visualiza el grafo actualizado
        4. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Eliminar Ciudad".
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Ciudad")
        ventana.geometry("400x150")
        ventana.transient(self.root)
        ventana.grab_set()
        
        ciudad_var = tk.StringVar()
        
        ttk.Label(ventana, text="Seleccione la ciudad a eliminar:").grid(
            row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Combobox(ventana, textvariable=ciudad_var, values=self.grafo.listar_ciudades()).grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def eliminar():
            ciudad = ciudad_var.get()
            
            if not ciudad:
                messagebox.showerror("Error", "Debe seleccionar una ciudad.")
                return
            
            # Confirmar la eliminación
            if not messagebox.askyesno("Confirmar", 
                                     f"¿Está seguro de eliminar la ciudad {ciudad} y todas sus conexiones?"):
                return
            
            # Eliminar de la base de datos
            if self.db.eliminar_ciudad(ciudad):
                # Eliminar del grafo
                self.grafo.eliminar_ciudad(ciudad)
                
                # Actualizar listas de ciudades en la interfaz
                self.combo_origen.config(values=self.grafo.listar_ciudades())
                self.combo_destino.config(values=self.grafo.listar_ciudades())
                
                # Si la ciudad era parte de la ruta actual, limpiar la ruta
                if self.ruta_actual and ciudad in self.ruta_actual:
                    self.ruta_actual = None
                    self.info_ruta_text.delete(1.0, tk.END)
                
                # Visualizar el grafo actualizado
                self.visualizar_grafo()
                
                messagebox.showinfo("Éxito", f"Ciudad {ciudad} eliminada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la ciudad de la base de datos.")
        
        ttk.Button(ventana, text="Eliminar", command=eliminar).grid(
            row=2, column=0, columnspan=2, pady=20)
    
    def agregar_conexion(self):
        """
        Abre un diálogo para agregar una nueva conexión entre dos ciudades.
        
        Este método:
        1. Crea una ventana de diálogo con campos para:
           - Selección de ciudad de origen
           - Selección de ciudad de destino
           - Distancia en kilómetros
        2. Valida los datos ingresados:
           - Verifica que se hayan seleccionado ciudades de origen y destino
           - Verifica que las ciudades sean diferentes
           - Verifica que la distancia sea un número positivo
        3. Si los datos son válidos:
           - Obtiene las coordenadas de las ciudades
           - Agrega la conexión a la base de datos
           - Actualiza el grafo en memoria
           - Visualiza el grafo actualizado
        4. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Agregar Conexión".
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Conexión")
        ventana.geometry("400x200")
        ventana.transient(self.root)
        ventana.grab_set()
        
        origen_var = tk.StringVar()
        destino_var = tk.StringVar()
        distancia_var = tk.StringVar()
        
        ttk.Label(ventana, text="Ciudad de Origen:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Combobox(ventana, textvariable=origen_var, values=self.grafo.listar_ciudades()).grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Ciudad de Destino:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Combobox(ventana, textvariable=destino_var, values=self.grafo.listar_ciudades()).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Distancia (km):").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=distancia_var).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def guardar():
            """
            Función que guarda los datos de la conexión agregada.
            
            Esta función:
            1. Obtiene los datos ingresados por el usuario
            2. Valida que se hayan seleccionado ciudades de origen y destino
            3. Valida que la distancia sea un número positivo
            4. Si los datos son válidos:
               - Obtiene las coordenadas de las ciudades
               - Agrega la conexión a la base de datos
               - Actualiza el grafo en memoria
               - Visualiza el grafo actualizado
            5. Muestra mensajes de éxito o error según corresponda

            Nota: Esta función se llama cuando el usuario presiona el botón "Guardar" en la ventana de diálogo.
            """
            origen = origen_var.get()
            destino = destino_var.get()
            
            try:
                distancia = int(distancia_var.get())
                if distancia <= 0:
                    raise ValueError("La distancia debe ser un número positivo.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            if not origen or not destino:
                messagebox.showerror("Error", "Debe seleccionar ciudades de origen y destino.")
                return
            
            if origen == destino:
                messagebox.showerror("Error", "Las ciudades de origen y destino deben ser diferentes.")
                return
            
            # Obtener coordenadas para agregar junto con la ruta
            origen_lat, origen_lng = self.grafo.coordenadas.get(origen, (None, None))
            destino_lat, destino_lng = self.grafo.coordenadas.get(destino, (None, None))
            
            if self.db.agregar_ruta(origen, destino, distancia, 
                                   origen_lat, origen_lng, destino_lat, destino_lng):
                self.grafo.agregar_conexion(origen, destino, distancia)
                
                # Visualizar el grafo actualizado
                self.visualizar_grafo()
                
                messagebox.showinfo("Éxito", f"Conexión {origen} - {destino} agregada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo agregar la conexión a la base de datos.")
        
        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2, pady=20)
    
    def editar_conexion(self):
        """
        Abre un diálogo para editar una conexión existente entre dos ciudades.
        
        Este método:
        1. Crea una ventana de diálogo con campos para:
           - Selección de ciudad de origen
           - Selección de ciudad de destino (actualizable según el origen)
           - Nueva distancia en kilómetros
        2. Implementa actualización dinámica de destinos:
           - Al seleccionar origen, actualiza la lista de destinos disponibles
           - Al seleccionar destino, carga la distancia actual
        3. Valida los datos ingresados:
           - Verifica que se hayan seleccionado ciudades
           - Verifica que la distancia sea un número positivo
        4. Si los datos son válidos:
           - Elimina la conexión actual de la base de datos
           - Agrega la nueva conexión con la distancia actualizada
           - Actualiza el grafo en memoria
           - Visualiza el grafo actualizado
        5. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Editar Conexión".
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Conexión")
        ventana.geometry("400x200")
        ventana.transient(self.root)
        ventana.grab_set()
        
        origen_var = tk.StringVar()
        destino_var = tk.StringVar()
        distancia_var = tk.StringVar()
        
        ttk.Label(ventana, text="Ciudad de Origen:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        origen_combo = ttk.Combobox(ventana, textvariable=origen_var, values=self.grafo.listar_ciudades())
        origen_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Ciudad de Destino:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        destino_combo = ttk.Combobox(ventana, textvariable=destino_var, values=[])
        destino_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Nueva Distancia (km):").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(ventana, textvariable=distancia_var).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def actualizar_destinos(event=None):
            """
            Actualiza la lista de ciudades destino disponibles según la ciudad de origen seleccionada.
            
            Esta función:
            1. Obtiene la ciudad de origen seleccionada
            2. Si la ciudad existe en el grafo:
               - Obtiene la lista de ciudades conectadas
               - Actualiza el combobox de destinos
               - Limpia la selección de destino y distancia
            """
            origen = origen_var.get()
            if origen in self.grafo.grafo:
                destinos = list(self.grafo.grafo[origen].keys())
                destino_combo.config(values=destinos)
                destino_var.set("")
                distancia_var.set("")
        
        def actualizar_distancia(event=None):
            """
            Actualiza el campo de distancia cuando se selecciona un destino.
            
            Esta función:
            1. Obtiene la ciudad de origen y destino seleccionadas
            2. Si ambas ciudades existen y están conectadas:
               - Obtiene la distancia actual entre ellas
               - Actualiza el campo de distancia con este valor
            """
            origen = origen_var.get()
            destino = destino_var.get()
            if origen in self.grafo.grafo and destino in self.grafo.grafo[origen]:
                distancia_var.set(str(self.grafo.grafo[origen][destino]))
        
        origen_combo.bind("<<ComboboxSelected>>", actualizar_destinos)
        destino_combo.bind("<<ComboboxSelected>>", actualizar_distancia)
        
        def guardar():
            """
            Guarda los cambios realizados a la conexión.
            
            Esta función:
            1. Obtiene y valida los datos ingresados:
               - Verifica que se hayan seleccionado ciudades
               - Verifica que la distancia sea un número positivo
            2. Elimina la conexión actual de la base de datos
            3. Agrega la nueva conexión con la distancia actualizada
            4. Actualiza el grafo en memoria
            5. Visualiza el grafo actualizado
            6. Muestra mensajes de éxito o error según corresponda
            """
            origen = origen_var.get()
            destino = destino_var.get()
            
            try:
                distancia = int(distancia_var.get())
                if distancia <= 0:
                    raise ValueError("La distancia debe ser un número positivo.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            if not origen or not destino:
                messagebox.showerror("Error", "Debe seleccionar ciudades de origen y destino.")
                return
            
            # Primero eliminamos la conexión actual
            if self.db.eliminar_ruta(origen, destino):
                # Luego agregamos la nueva con la distancia actualizada
                origen_lat, origen_lng = self.grafo.coordenadas.get(origen, (None, None))
                destino_lat, destino_lng = self.grafo.coordenadas.get(destino, (None, None))
                
                if self.db.agregar_ruta(origen, destino, distancia,
                                       origen_lat, origen_lng, destino_lat, destino_lng):
                    # Actualizamos el grafo
                    self.grafo.eliminar_conexion(origen, destino)
                    self.grafo.agregar_conexion(origen, destino, distancia)
                    
                    # Visualizar el grafo actualizado
                    self.visualizar_grafo()
                    
                    messagebox.showinfo("Éxito", f"Conexión {origen} - {destino} actualizada correctamente.")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la conexión en la base de datos.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la conexión original.")
        
        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2, pady=20)
    
    def eliminar_conexion(self):
        """
        Abre un diálogo para eliminar una conexión existente entre dos ciudades.
        
        Este método:
        1. Crea una ventana de diálogo con campos para:
           - Selección de ciudad de origen
           - Selección de ciudad de destino (actualizable según el origen)
        2. Implementa actualización dinámica de destinos:
           - Al seleccionar origen, actualiza la lista de destinos disponibles
        3. Valida los datos ingresados:
           - Verifica que se hayan seleccionado ciudades
        4. Si los datos son válidos:
           - Solicita confirmación del usuario
           - Elimina la conexión de la base de datos
           - Actualiza el grafo en memoria
           - Limpia la ruta actual si la conexión eliminada era parte de ella
           - Visualiza el grafo actualizado
        5. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Eliminar Conexión".
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Conexión")
        ventana.geometry("400x150")
        ventana.transient(self.root)
        ventana.grab_set()
        
        origen_var = tk.StringVar()
        destino_var = tk.StringVar()
        
        ttk.Label(ventana, text="Ciudad de Origen:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        origen_combo = ttk.Combobox(ventana, textvariable=origen_var, values=self.grafo.listar_ciudades())
        origen_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Ciudad de Destino:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        destino_combo = ttk.Combobox(ventana, textvariable=destino_var, values=[])
        destino_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def actualizar_destinos(event=None):
            """
            Actualiza la lista de ciudades destino disponibles según la ciudad de origen seleccionada.
            
            Esta función:
            1. Obtiene la ciudad de origen seleccionada
            2. Si la ciudad existe en el grafo:
               - Obtiene la lista de ciudades conectadas
               - Actualiza el combobox de destinos
               - Limpia la selección de destino
            """
            origen = origen_var.get()
            if origen in self.grafo.grafo:
                destinos = list(self.grafo.grafo[origen].keys())
                destino_combo.config(values=destinos)
                destino_var.set("")
        
        origen_combo.bind("<<ComboboxSelected>>", actualizar_destinos)
        
        def eliminar():
            """
            Elimina la conexión seleccionada del grafo y la base de datos.
            
            Esta función:
            1. Obtiene y valida los datos ingresados:
               - Verifica que se hayan seleccionado ciudades
            2. Solicita confirmación del usuario
            3. Si se confirma:
               - Elimina la conexión de la base de datos
               - Actualiza el grafo en memoria
               - Verifica si la conexión era parte de la ruta actual
               - Limpia la ruta actual si es necesario
               - Visualiza el grafo actualizado
            4. Muestra mensajes de éxito o error según corresponda
            """
            origen = origen_var.get()
            destino = destino_var.get()
            
            if not origen or not destino:
                messagebox.showerror("Error", "Debe seleccionar ciudades de origen y destino.")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la conexión {origen} - {destino}?"):
                if self.db.eliminar_ruta(origen, destino):
                    self.grafo.eliminar_conexion(origen, destino)
                    
                    # Si la conexión era parte de la ruta actual, limpiar la ruta
                    if self.ruta_actual and len(self.ruta_actual) > 1:
                        for i in range(len(self.ruta_actual) - 1):
                            if ((self.ruta_actual[i] == origen and self.ruta_actual[i+1] == destino) or
                                (self.ruta_actual[i] == destino and self.ruta_actual[i+1] == origen)):
                                self.ruta_actual = None
                                self.info_ruta_text.delete(1.0, tk.END)
                                break
                    
                    # Visualizar el grafo actualizado
                    self.visualizar_grafo()
                    
                    messagebox.showinfo("Éxito", f"Conexión {origen} - {destino} eliminada correctamente.")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la conexión de la base de datos.")
        
        ttk.Button(ventana, text="Eliminar", command=eliminar).grid(row=2, column=0, columnspan=2, pady=20)
    
    def importar_json(self):
        """
        Importa un grafo desde un archivo JSON a la base de datos.
        
        Este método:
        1. Abre un diálogo para seleccionar el archivo JSON:
           - Permite filtrar por archivos .json
           - Permite ver todos los archivos
        2. Si se selecciona un archivo:
           - Solicita confirmación del usuario (ya que se reemplazarán los datos existentes)
           - Si se confirma:
             - Importa el grafo a la base de datos
             - Actualiza el grafo en memoria con los nuevos datos
             - Actualiza las listas de ciudades en la interfaz
             - Limpia la ruta actual si existe
             - Visualiza el grafo actualizado
        3. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Importar desde JSON".
        """
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            if messagebox.askyesno("Confirmar", "La importación reemplazará todas las rutas existentes. ¿Desea continuar?"):
                if self.db.importar_desde_json(ruta_archivo):
                    # Actualizar el grafo en memoria
                    grafo_dict, coords_dict = self.db.obtener_grafo_completo_con_coords()
                    self.grafo.grafo = grafo_dict
                    self.grafo.coordenadas = {ciudad: (datos["lat"], datos["lng"]) 
                                            for ciudad, datos in coords_dict.items()
                                            if datos["lat"] is not None and datos["lng"] is not None}
                    self.grafo.ciudades = list(self.grafo.grafo.keys())
                    
                    # Actualizar listas de ciudades en la interfaz
                    self.combo_origen.config(values=self.grafo.listar_ciudades())
                    self.combo_destino.config(values=self.grafo.listar_ciudades())
                    
                    # Limpiar la ruta actual
                    self.ruta_actual = None
                    self.info_ruta_text.delete(1.0, tk.END)
                    
                    # Visualizar el grafo actualizado
                    self.visualizar_grafo()
                    
                    messagebox.showinfo("Éxito", "Grafo importado correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo importar el grafo desde el archivo JSON.")
    
    def exportar_json(self):
        """
        Exporta el grafo actual a un archivo JSON.
        
        Este método:
        1. Abre un diálogo para guardar el archivo JSON:
           - Establece la extensión por defecto como .json
           - Permite filtrar por archivos .json
           - Permite ver todos los archivos
        2. Si se selecciona una ubicación:
           - Exporta el grafo actual a un archivo JSON
           - Incluye tanto la estructura del grafo como las coordenadas
        3. Muestra mensajes de éxito o error según corresponda
        
        Nota: Este método se llama cuando el usuario presiona el botón "Exportar a JSON".
        """
        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar archivo JSON",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            if self.db.exportar_a_json(ruta_archivo):
                messagebox.showinfo("Éxito", f"Grafo exportado correctamente a {ruta_archivo}.")
            else:
                messagebox.showerror("Error", "No se pudo exportar el grafo a un archivo JSON.")

    def on_closing(self):
        """
        Maneja el cierre de la aplicación.
        
        Este método:
        1. Cierra la conexión con la base de datos:
           - Libera los recursos del sistema
           - Asegura que todos los datos se guarden correctamente
        2. Destruye la ventana principal de la aplicación
        
        Nota: Este método se llama cuando el usuario intenta cerrar la ventana principal
        de la aplicación, ya sea haciendo clic en el botón de cerrar o usando atajos
        de teclado como Alt+F4.
        """
        self.db.cerrar()
        self.root.destroy()


if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.
    
    Este bloque:
    1. Crea la ventana principal de la aplicación:
       - Inicializa el sistema de ventanas de Tkinter
       - Configura el título y tamaño de la ventana
    2. Crea una instancia de la aplicación:
       - Inicializa la interfaz gráfica
       - Carga el grafo desde la base de datos
       - Configura los eventos y widgets
    3. Configura el manejo del cierre de la ventana:
       - Asocia el evento de cierre con el método on_closing
       - Asegura que se cierre correctamente la conexión a la base de datos
    4. Inicia el bucle principal de eventos:
       - Maneja la interacción del usuario
       - Actualiza la interfaz
       - Mantiene la aplicación en ejecución
    
    Nota: Este bloque solo se ejecuta cuando el archivo se ejecuta directamente,
    no cuando se importa como módulo.
    """
    root = tk.Tk()
    app = AplicacionRutas(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()