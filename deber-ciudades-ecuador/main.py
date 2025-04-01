import tkinter as tk
from interfaz_grafo import AplicacionRutas
import os
import sys
import json

def inicializar_sistema():
    """
    Inicializa el sistema, asegurando que todos los archivos necesarios estén disponibles.
    """
    # Verificar si existe el archivo de base de datos
    if not os.path.exists('rutas_ecuador.db'):
        print("Inicializando la base de datos...")
    
    # Verificar si existe el archivo JSON con el grafo
    if not os.path.exists('grafo_ecuador.json'):
        print("Creando archivo JSON con el grafo predeterminado...")
        from grafo_ecuador import GrafoEcuador
        grafo = GrafoEcuador()
        with open('grafo_ecuador.json', 'w', encoding='utf-8') as f:
            json.dump(grafo.grafo, f, ensure_ascii=False, indent=2)
    
    print("Sistema inicializado correctamente.")

def main():
    """
    Función principal que ejecuta la aplicación.
    """
    try:
        # Inicializar el sistema
        inicializar_sistema()
        
        # Crear y ejecutar la interfaz gráfica
        root = tk.Tk()
        app = AplicacionRutas(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presione Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()