import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        self.algoritmo_var = tk.StringVar(value="Búsqueda en Amplitud")
        
        self.ruta_actual = None
        
        self.configurar_interfaz()
    
    def sincronizar_grafo_bd(self):
        ciudades = self.db.listar_ciudades()
        
        if not ciudades:
            self.db.importar_grafo(self.grafo.grafo)
            messagebox.showinfo("Información", "Base de datos inicializada con el grafo predeterminado.")
        else:
            self.grafo.grafo = self.db.obtener_grafo_completo()
            self.grafo.ciudades = list(self.grafo.grafo.keys())
    
    def configurar_interfaz(self):
        panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        panel_izquierdo = ttk.Frame(panel_principal, width=300)
        panel_principal.add(panel_izquierdo, weight=1)
        
        panel_derecho = ttk.Frame(panel_principal)
        panel_principal.add(panel_derecho, weight=3)
        
        ttk.Label(panel_izquierdo, text="Seleccione la ciudad de origen:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_origen = ttk.Combobox(panel_izquierdo, textvariable=self.ciudad_origen_var, 
                                     values=self.grafo.listar_ciudades())
        self.combo_origen.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(panel_izquierdo, text="Seleccione la ciudad de destino:").pack(pady=(10, 5), anchor=tk.W)
        self.combo_destino = ttk.Combobox(panel_izquierdo, textvariable=self.ciudad_destino_var, 
                                      values=self.grafo.listar_ciudades())
        self.combo_destino.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(panel_izquierdo, text="Seleccione el algoritmo de búsqueda:").pack(pady=(10, 5), anchor=tk.W)
        algoritmos = ["Búsqueda en Amplitud", "Búsqueda en Profundidad", "Búsqueda de Costo Uniforme"]
        self.combo_algoritmo = ttk.Combobox(panel_izquierdo, textvariable=self.algoritmo_var, 
                                        values=algoritmos, state="readonly")
        self.combo_algoritmo.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(panel_izquierdo, text="Buscar Ruta", command=self.buscar_ruta).pack(pady=20)
        
        self.marco_info = ttk.LabelFrame(panel_izquierdo, text="Información de la Ruta")
        self.marco_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_ruta_text = tk.Text(self.marco_info, height=10, wrap=tk.WORD)
        self.info_ruta_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        marco_bd = ttk.LabelFrame(panel_izquierdo, text="Gestión de Base de Datos")
        marco_bd.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(marco_bd, text="Agregar Conexión", 
                  command=self.agregar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_bd, text="Eliminar Conexión", 
                  command=self.eliminar_conexion).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_bd, text="Importar desde JSON", 
                  command=self.importar_json).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(marco_bd, text="Exportar a JSON", 
                  command=self.exportar_json).pack(fill=tk.X, padx=5, pady=5)
        
        self.figura = plt.Figure(figsize=(7, 6))
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, panel_derecho)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.visualizar_grafo()
    
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
        
        self.info_ruta_text.insert(tk.END, "Ruta completa:\n")
        for i in range(len(ruta) - 1):
            dist = self.grafo.obtener_distancia(ruta[i], ruta[i+1])
            self.info_ruta_text.insert(tk.END, f"{ruta[i]} → {ruta[i+1]} ({dist} km)\n")
    
    def visualizar_grafo(self, ruta=None):
        self.ax.clear()
        
        G = nx.Graph()
        
        for origen, destinos in self.grafo.grafo.items():
            G.add_node(origen)
            for destino, distancia in destinos.items():
                G.add_edge(origen, destino, weight=distancia)
        
        pos = nx.spring_layout(G, seed=42)
        
        nx.draw_networkx_nodes(G, pos, node_size=300, node_color='lightblue', ax=self.ax)
        
        if ruta and len(ruta) > 1:
            ruta_aristas = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
            
            otras_aristas = [(u, v) for u, v in G.edges() if (u, v) not in ruta_aristas and (v, u) not in ruta_aristas]
            nx.draw_networkx_edges(G, pos, edgelist=otras_aristas, width=1, alpha=0.3, ax=self.ax)
            
            nx.draw_networkx_edges(G, pos, edgelist=ruta_aristas, width=3, edge_color='r', ax=self.ax)
        else:
            nx.draw_networkx_edges(G, pos, width=1, ax=self.ax)
        
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif', ax=self.ax)
        
        self.ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
        self.ax.axis('off')
        self.figura.tight_layout()
        
        self.canvas.draw()
    
    def agregar_conexion(self):
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
            
            if self.db.agregar_ruta(origen, destino, distancia):
                self.grafo.agregar_conexion(origen, destino, distancia)
                
                self.combo_origen.config(values=self.grafo.listar_ciudades())
                self.combo_destino.config(values=self.grafo.listar_ciudades())
                
                self.visualizar_grafo()
                
                messagebox.showinfo("Éxito", f"Conexión {origen} - {destino} agregada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo agregar la conexión a la base de datos.")
        
        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(ventana, text="Agregar Nueva Ciudad", command=self.agregar_nueva_ciudad).grid(
            row=4, column=0, columnspan=2, pady=5)
    
    def agregar_nueva_ciudad(self):
        nueva_ciudad = simpledialog.askstring("Nueva Ciudad", "Ingrese el nombre de la nueva ciudad:")
        if nueva_ciudad:
            ciudad_id = self.db.agregar_ciudad(nueva_ciudad)
            if ciudad_id:
                if nueva_ciudad not in self.grafo.grafo:
                    self.grafo.grafo[nueva_ciudad] = {}
                    self.grafo.ciudades.append(nueva_ciudad)
                
                self.combo_origen.config(values=self.grafo.listar_ciudades())
                self.combo_destino.config(values=self.grafo.listar_ciudades())
                
                messagebox.showinfo("Éxito", f"Ciudad {nueva_ciudad} agregada correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo agregar la ciudad a la base de datos.")
    
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
        ttk.Combobox(ventana, textvariable=origen_var, values=self.grafo.listar_ciudades()).grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Label(ventana, text="Ciudad de Destino:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Combobox(ventana, textvariable=destino_var, values=self.grafo.listar_ciudades()).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
        
        def eliminar():
            origen = origen_var.get()
            destino = destino_var.get()
            
            if not origen or not destino:
                messagebox.showerror("Error", "Debe seleccionar ciudades de origen y destino.")
                return
            
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la conexión {origen} - {destino}?"):
                if self.db.eliminar_ruta(origen, destino):
                    self.grafo.eliminar_conexion(origen, destino)
                    
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
                    self.grafo.grafo = self.db.obtener_grafo_completo()
                    self.grafo.ciudades = list(self.grafo.grafo.keys())
                    
                    self.combo_origen.config(values=self.grafo.listar_ciudades())
                    self.combo_destino.config(values=self.grafo.listar_ciudades())
                    
                    self.visualizar_grafo()
                    
                    messagebox.showinfo("Éxito", "Grafo importado correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo importar el grafo desde el archivo JSON.")
    
    def exportar_json(self):
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
        self.db.cerrar()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionRutas(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()