# Módulos de la biblioteca estándar
 # Biblioteca para crear la interfaz gráfica de usuario (GUI)
import tkinter as tk 
# Funcionalidades para interactuar con el sistema operativo y manejo de archivos
import os 
# Acceso a variables y funciones específicas del intérprete de Python
import sys 
# Funcionalidades para codificar y decodificar datos en formato JSON
import json 

# Módulos locales
# Clase principal que implementa la interfaz gráfica de la aplicación
from interfaz_grafo import AplicacionRutas 
# Clase que maneja la estructura de datos del grafo de ciudades
from grafo_ecuador import GrafoEcuador 
# Clase para gestionar la base de datos SQLite de rutas
from base_datos_rutas import BaseDatosRutas 

def inicializar_sistema():
    """
    Inicializa el sistema de rutas de Ecuador, asegurando que todos los archivos necesarios
    estén disponibles y que la base de datos contenga las coordenadas geográficas.
    
    Este método realiza las siguientes tareas:
    1. Verifica la existencia del archivo de base de datos 'rutas_ecuador.db'
    2. Verifica la existencia del archivo JSON 'grafo_ecuador.json'
    3. Si el archivo JSON no existe:
       - Crea una instancia de GrafoEcuador con datos predeterminados
       - Prepara los datos incluyendo coordenadas para el archivo JSON
       - Guarda el grafo en formato JSON
    4. Verifica si la base de datos tiene las columnas de coordenadas
    5. Actualiza las coordenadas faltantes en la base de datos
    6. Cierra la conexión a la base de datos
    
    Nota: Este método debe ser llamado al inicio de la aplicación para asegurar
    que todos los componentes necesarios estén disponibles y configurados correctamente.
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
    Actualiza las coordenadas geográficas faltantes en la base de datos utilizando
    las coordenadas predeterminadas del GrafoEcuador.
    
    Parámetros:
        db (BaseDatosRutas): Instancia de la base de datos a actualizar
    
    Proceso:
    1. Obtiene la lista de ciudades de la base de datos con sus coordenadas actuales
    2. Crea una instancia de GrafoEcuador para acceder a las coordenadas predeterminadas
    3. Para cada ciudad:
       - Verifica si faltan coordenadas (latitud o longitud)
       - Si faltan y existen en el grafo predeterminado, actualiza la base de datos
    4. Muestra un resumen de las actualizaciones realizadas
    
    Nota: Esta función es llamada durante la inicialización del sistema para asegurar
    que todas las ciudades tengan coordenadas válidas.
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
    Verifica que todas las bibliotecas necesarias para el funcionamiento del sistema
    estén instaladas correctamente.
    
    Dependencias verificadas:
    - tkinter: Para la interfaz gráfica de usuario
    - matplotlib: Para la visualización de grafos y mapas
    - networkx: Para el manejo y análisis de grafos
    
    Proceso:
    1. Define un diccionario con las dependencias y sus descripciones
    2. Intenta importar cada módulo
    3. Si alguna dependencia falta:
       - Muestra un mensaje de error con las dependencias faltantes
       - Proporciona instrucciones para instalarlas
       - Retorna False
    4. Si todas las dependencias están presentes, retorna True
    
    Retorna:
        bool: True si todas las dependencias están instaladas, False en caso contrario
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
    Función principal que ejecuta la aplicación de gestión de rutas de Ecuador.
    
    Esta función es el punto de entrada de la aplicación y maneja todo el ciclo de vida
    de la misma. Se encarga de:
    1. Verificar las dependencias necesarias
    2. Inicializar el sistema
    3. Crear y ejecutar la interfaz gráfica
    4. Manejar errores y excepciones
    
    Flujo de ejecución:
    1. Verifica las dependencias del sistema
       - Si faltan dependencias, muestra mensaje y termina
    2. Inicializa el sistema
       - Crea archivos necesarios si no existen
       - Configura la base de datos
       - Actualiza coordenadas faltantes
    3. Crea la ventana principal de la aplicación
    4. Configura el manejador de cierre de ventana
    5. Inicia el bucle principal de la interfaz gráfica
    
    Manejo de errores:
    - Captura y muestra cualquier excepción que ocurra durante la ejecución
    - Muestra el stack trace completo para facilitar la depuración
    - Espera a que el usuario presione Enter antes de cerrar en caso de error
    
    Nota: Esta función debe ser llamada solo cuando el script se ejecuta directamente,
    no cuando se importa como módulo.
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