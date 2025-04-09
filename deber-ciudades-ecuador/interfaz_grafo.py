import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from grafo_ecuador import GrafoEcuador
from base_datos_rutas import BaseDatosRutas

class AplicacionRutas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Rutas de Ecuador")
        self.root.geometry("1200x700")
        
        self.db = BaseDatosRutas('rutas_ecuador.db')
        
        self.grafo = GrafoEcuador()
        
        self.sincronizar_grafo_bd()
        
        self.ciudad_origen_var = tk.StringVar()
        self.ciudad_destino_var = tk.StringVar()
        self.algoritmo_var = tk.StringVar(value="Búsqueda A*")
        self.mapa_real_var = tk.BooleanVar(value=True)
        
        self.ruta_actual = None
        self.ciudad_seleccionada = None
        self.ultima_figura = None
        
        self.configurar_interfaz()
    
    def sincronizar_grafo_bd(self):
        ciudades = self.db.listar_ciudades()
        
        if not ciudades:
            # Inicializa la BD con el grafo predeterminado
            grafo_dict = self.grafo.grafo
            coords_dict = {ciudad: {"lat": lat, "lng": lng} 
                          for ciudad, (lat, lng) in self.grafo.coordenadas.items()}
            
            self.db.importar_grafo(grafo_dict, coords_dict)
            messagebox.showinfo("Información", "Base de datos inicializada con el grafo predeterminado.")
        else:
            # Cargar grafo y coordenadas desde la BD
            grafo_dict, coords_dict = self.db.obtener_grafo_completo_con_coords()
            self.grafo.grafo = grafo_dict
            self.grafo.coordenadas = {ciudad: (datos["lat"], datos["lng"]) 
                                    for ciudad, datos in coords_dict.items() 
                                    if datos["lat"] is not None and datos["lng"] is not None}
            self.grafo.ciudades = list(self.grafo.grafo.keys())
    
    def configurar_interfaz(self):
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        panel_izquierdo = ttk.Frame(panel_principal, width=300)
        panel_principal.add(panel_izquierdo, weight=1)
        
        panel_derecho = ttk.Frame(panel_principal)
        panel_principal.add(panel_derecho, weight=3)
        
        self.notebook = ttk.Notebook(panel_izquierdo)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Búsqueda
        panel_busqueda = ttk.Frame(self.notebook)
        self.notebook.add(panel_busqueda, text="Búsqueda")
        
        ttk.Label(panel_busqueda, text="Seleccione la ciudad de origen:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_origen = ttk.Combobox(panel_busqueda, textvariable=self.ciudad_origen_var, 
                                     values=self.grafo.listar_ciudades())
        self.combo_origen.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(panel_busqueda, text="Seleccione la ciudad de destino:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_destino = ttk.Combobox(panel_busqueda, textvariable=self.ciudad_destino_var, 
                                      values=self.grafo.listar_ciudades())
        self.combo_destino.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(panel_busqueda, text="Seleccione el algoritmo de búsqueda:").pack(pady=(10, 5), anchor=tk.W)
        algoritmos = ["Búsqueda en Amplitud", "Búsqueda en Profundidad", 
                     "Búsqueda de Costo Uniforme", "Búsqueda A*"]
        self.combo_algoritmo = ttk.Combobox(panel_busqueda, textvariable=self.algoritmo_var, 
                                        values=algoritmos, state="readonly")
        self.combo_algoritmo.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(panel_busqueda, text="Usar mapa real", variable=self.mapa_real_var,
                       command=self.actualizar_visualizacion).pack(pady=5)
        
        ttk.Button(panel_busqueda, text="Buscar Ruta", command=self.buscar_ruta).pack(pady=20)
        
        self.marco_info = ttk.LabelFrame(panel_busqueda, text="Información de la Ruta")
        self.marco_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_ruta_text = tk.Text(self.marco_info, height=10, wrap=tk.WORD)
        self.info_ruta_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de Gestión
        panel_gestion = ttk.Frame(self.notebook)
        self.notebook.add(panel_gestion, text="Gestión")
        
        marco_ciudades = ttk.LabelFrame(panel_gestion, text="Gestión de Ciudades")
        marco_ciudades.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_ciudades, text="Agregar Ciudad", 
                  command=self.agregar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_ciudades, text="Editar Ciudad", 
                  command=self.editar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_ciudades, text="Eliminar Ciudad", 
                  command=self.eliminar_ciudad).pack(fill=tk.X, padx=5, pady=5)
        
        marco_rutas = ttk.LabelFrame(panel_gestion, text="Gestión de Rutas")
        marco_rutas.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_rutas, text="Agregar Conexión", 
                  command=self.agregar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_rutas, text="Editar Conexión", 
                  command=self.editar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_rutas, text="Eliminar Conexión", 
                  command=self.eliminar_conexion).pack(fill=tk.X, padx=5, pady=5)
        
        marco_bd = ttk.LabelFrame(panel_gestion, text="Gestión de Base de Datos")
        marco_bd.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_bd, text="Importar desde JSON", 
                  command=self.importar_json).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_bd, text="Exportar a JSON", 
                  command=self.exportar_json).pack(fill=tk.X, padx=5, pady=5)
        
        # Panel de ayuda para interacción con mapa
        marco_ayuda = ttk.LabelFrame(panel_gestion, text="Ayuda Mapa Interactivo")
        marco_ayuda.pack(fill=tk.X, padx=5, pady=5)
        
        ayuda_text = (
            "- Haga clic en una ciudad para ver información\n"
            "- Para seleccionar origen/destino, haga clic y use 'Establecer como...' en el menú\n"
            "- Use las herramientas de navegación para zoom y desplazamiento\n"
            "- Active 'Usar mapa real' para ver ubicaciones geográficas reales"
        )
        ttk.Label(marco_ayuda, text=ayuda_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # Panel derecho para el mapa
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
        
        self.visualizar_grafo()
    
    def on_click_mapa(self, event):
        if event.xdata is None or event.ydata is None or event.button != 1:  # Solo click izquierdo
            return
        
        # Buscar la ciudad más cercana al clic
        usar_mapa_real = self.mapa_real_var.get()
        ciudad_cercana = self.encontrar_ciudad_cercana(event.xdata, event.ydata, usar_mapa_real)
        
        if ciudad_cercana:
            self.ciudad_seleccionada = ciudad_cercana
            self.mostrar_menu_ciudad(event)
    
    def encontrar_ciudad_cercana(self, x, y, usar_mapa_real):
        """Encuentra la ciudad más cercana a las coordenadas del clic."""
        ciudad_mas_cercana = None
        distancia_minima = float('inf')
        
        G = nx.Graph()
        for origen in self.grafo.grafo:
            G.add_node(origen)
        
        if usar_mapa_real:
            pos = {ciudad: (lon, lat) for ciudad, (lat, lon) in self.grafo.coordenadas.items() 
                  if ciudad in self.grafo.grafo}
        else:
            pos = nx.spring_layout(G, seed=42)
        
        for ciudad, (px, py) in pos.items():
            distancia = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
            if distancia < distancia_minima:
                distancia_minima = distancia
                ciudad_mas_cercana = ciudad
        
        # Umbral para considerar que está lo suficientemente cerca
        umbral = 0.05 if usar_mapa_real else 0.1
        return ciudad_mas_cercana if distancia_minima < umbral else None
    
    def mostrar_menu_ciudad(self, event):
        """Muestra un menú contextual al hacer clic en una ciudad."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Ciudad: {self.ciudad_seleccionada}", state=tk.DISABLED)
        menu.add_separator()
        menu.add_command(label="Establecer como Origen", command=self.establecer_como_origen)
        menu.add_command(label="Establecer como Destino", command=self.establecer_como_destino)
        menu.add_separator()
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
            """Establece la ciudad seleccionada como origen."""
            if self.ciudad_seleccionada:
                self.ciudad_origen_var.set(self.ciudad_seleccionada)
                self.notebook.select(0)  # Cambiar a la pestaña de búsqueda
    
    def establecer_como_destino(self):
        """Establece la ciudad seleccionada como destino."""
        if self.ciudad_seleccionada:
            self.ciudad_destino_var.set(self.ciudad_seleccionada)
            self.notebook.select(0)  # Cambiar a la pestaña de búsqueda
    
    def on_hover_mapa(self, event):
        """Muestra información al pasar el cursor sobre una ciudad."""
        if event.xdata is None or event.ydata is None:
            return
        
        usar_mapa_real = self.mapa_real_var.get()
        ciudad = self.encontrar_ciudad_cercana(event.xdata, event.ydata, usar_mapa_real)
        
        if ciudad:
            # Actualizar el cursor para indicar que se puede hacer clic
            self.canvas.get_tk_widget().config(cursor="hand2")
            
            # Mostrar tooltip (simplificado - en una implementación real usaría un tooltip apropiado)
            self.ax.set_title(f"Ciudad: {ciudad}")
            self.canvas.draw_idle()
        else:
            # Restaurar cursor normal
            self.canvas.get_tk_widget().config(cursor="")
            
            # Restaurar título original
            if self.ruta_actual:
                self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador - Ruta Encontrada")
            else:
                self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
            self.canvas.draw_idle()
    
    def ver_conexiones(self):
        """Muestra las conexiones de la ciudad seleccionada."""
        if not self.ciudad_seleccionada:
            return
        
        conexiones = self.grafo.listar_conexiones(self.ciudad_seleccionada)
        if not conexiones:
            messagebox.showinfo("Conexiones", f"La ciudad {self.ciudad_seleccionada} no tiene conexiones.")
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Conexiones desde {self.ciudad_seleccionada}")
        ventana.geometry("400x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        ttk.Label(ventana, text=f"Conexiones desde {self.ciudad_seleccionada}:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        frame = ttk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        treeview = ttk.Treeview(frame, columns=("ciudad", "distancia"), show="headings")
        treeview.heading("ciudad", text="Ciudad")
        treeview.heading("distancia", text="Distancia (km)")
        treeview.column("ciudad", width=200)
        treeview.column("distancia", width=100)
        
        for ciudad, distancia in sorted(conexiones.items()):
            treeview.insert("", "end", values=(ciudad, distancia))
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=scrollbar.set)
        
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    
    def editar_ciudad_seleccionada(self):
        """Edita la ciudad actualmente seleccionada en el mapa."""
        if self.ciudad_seleccionada:
            self.editar_ciudad(self.ciudad_seleccionada)
    
    def buscar_ruta(self):
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
        """Actualiza la visualización del grafo con la configuración actual."""
        self.visualizar_grafo(self.ruta_actual)
    
    def visualizar_grafo(self, ruta=None):
        """Visualiza el grafo en el panel derecho."""
        self.ax.clear()
        
        usar_mapa_real = self.mapa_real_var.get()
        self.grafo.visualizar_grafo(ruta, usar_mapa_real=usar_mapa_real, ax=self.ax)
        
        if ruta:
            self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador - Ruta Encontrada")
        else:
            self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
        
        self.canvas.draw()
    
    def agregar_ciudad(self):
        """Abre un diálogo para agregar una nueva ciudad con coordenadas."""
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
        """Abre un diálogo para editar una ciudad existente."""
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
        """Elimina una ciudad seleccionada del grafo y de la base de datos."""
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
        """Abre un diálogo para agregar una nueva conexión entre ciudades."""
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
        """Abre un diálogo para editar una conexión existente."""
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
            origen = origen_var.get()
            if origen in self.grafo.grafo:
                destinos = list(self.grafo.grafo[origen].keys())
                destino_combo.config(values=destinos)
                destino_var.set("")
                distancia_var.set("")
        
        def actualizar_distancia(event=None):
            origen = origen_var.get()
            destino = destino_var.get()
            if origen in self.grafo.grafo and destino in self.grafo.grafo[origen]:
                distancia_var.set(str(self.grafo.grafo[origen][destino]))
        
        origen_combo.bind("<<ComboboxSelected>>", actualizar_destinos)
        destino_combo.bind("<<ComboboxSelected>>", actualizar_distancia)
        
        def guardar():
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
        """Elimina una conexión del grafo y de la base de datos."""
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
            origen = origen_var.get()
            if origen in self.grafo.grafo:
                destinos = list(self.grafo.grafo[origen].keys())
                destino_combo.config(values=destinos)
                destino_var.set("")
        
        origen_combo.bind("<<ComboboxSelected>>", actualizar_destinos)
        
        def eliminar():
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
        """Importa un grafo desde un archivo JSON a la base de datos."""
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
        """Exporta el grafo a un archivo JSON."""
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
        """Función que se ejecuta al cerrar la aplicación."""
        self.db.cerrar()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionRutas(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()