import tkinter as tk
from interfaz_grafo import AplicacionRutas
import os
import sys
import json
from grafo_ecuador import GrafoEcuador
from base_datos_rutas import BaseDatosRutas

def inicializar_sistema():
    """
    Inicializa el sistema, asegurando que todos los archivos necesarios estén disponibles
    y que la base de datos contenga las coordenadas geográficas.
    """
    print("Inicializando el sistema de rutas de Ecuador...")
    
    # Verificar si existe el archivo de base de datos
    if not os.path.exists('rutas_ecuador.db'):
        print("Inicializando la base de datos...")
    
    # Verificar si existe el archivo JSON con el grafo
    if not os.path.exists('grafo_ecuador.json'):
        print("Creando archivo JSON con el grafo predeterminado y coordenadas...")
        
        # Crear una instancia de GrafoEcuador con datos predeterminados
        grafo = GrafoEcuador()
        
        # Preparar datos incluyendo coordenadas para el archivo JSON
        datos = {
            "grafo": grafo.grafo,
            "coords": {ciudad: {"lat": lat, "lng": lng} 
                      for ciudad, (lat, lng) in grafo.coordenadas.items()}
        }
        
        # Guardar en formato JSON
        with open('grafo_ecuador.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    # Verificar si la base de datos tiene las columnas de coordenadas
    db = BaseDatosRutas('rutas_ecuador.db')
    
    # Verificar si hay ciudades sin coordenadas y asignarlas desde el grafo predeterminado
    actualizar_coordenadas_faltantes(db)
    
    db.cerrar()
    
    print("Sistema inicializado correctamente.")

def actualizar_coordenadas_faltantes(db):
    """
    Actualiza las coordenadas faltantes en la base de datos utilizando
    las coordenadas predeterminadas del GrafoEcuador.
    """
    # Obtener ciudades de la base de datos
    ciudades = db.listar_ciudades_con_coordenadas()
    
    # Obtener coordenadas predeterminadas
    grafo = GrafoEcuador()
    
    # Verificar cada ciudad y actualizar si faltan coordenadas
    actualizadas = 0
    for ciudad in ciudades:
        nombre = ciudad["nombre"]
        lat = ciudad["latitud"]
        lng = ciudad["longitud"]
        
        # Si faltan coordenadas y están disponibles en el grafo predeterminado
        if (lat is None or lng is None) and nombre in grafo.coordenadas:
            default_lat, default_lng = grafo.coordenadas[nombre]
            if db.actualizar_coordenadas(nombre, default_lat, default_lng):
                actualizadas += 1
                print(f"Coordenadas actualizadas para {nombre}: ({default_lat}, {default_lng})")
    
    if actualizadas > 0:
        print(f"Se actualizaron coordenadas para {actualizadas} ciudades.")

def verificar_dependencias():
    """
    Verifica que todas las bibliotecas necesarias estén instaladas.
    """
    dependencias = {
        "tkinter": "Interfaz gráfica",
        "matplotlib": "Visualización de grafos",
        "networkx": "Manejo de grafos"
    }
    
    faltantes = []
    for modulo, descripcion in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(f"{modulo} ({descripcion})")
    
    if faltantes:
        print("ERROR: Faltan las siguientes dependencias para ejecutar la aplicación:")
        for dep in faltantes:
            print(f"  - {dep}")
        print("\nPuede instalarlas con pip:")
        print("pip install matplotlib networkx")
        return False
    
    return True

def main():
    """
    Función principal que ejecuta la aplicación.
    """
    try:
        # Verificar dependencias
        if not verificar_dependencias():
            input("Presione Enter para salir...")
            return
        
        # Inicializar el sistema
        inicializar_sistema()
        
        # Crear y ejecutar la interfaz gráfica
        root = tk.Tk()
        app = AplicacionRutas(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()