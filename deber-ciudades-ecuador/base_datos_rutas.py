# Importación de la librería sqlite3 para trabajar con bases de datos SQLite
# SQLite es una base de datos ligera que almacena datos en un archivo local
import sqlite3

# Importación de la librería json para trabajar con archivos JSON
# Se utiliza para importar/exportar datos en formato JSON
import json

class BaseDatosRutas:
    """
    Clase que maneja la base de datos de rutas entre ciudades del Ecuador.
    Permite almacenar ciudades con sus coordenadas geográficas y las rutas
    que las conectan, incluyendo la distancia entre ellas.
    """

    def __init__(self, ruta_db='rutas_ecuador.db'):
        """
        Constructor de la clase BaseDatosRutas.

        Args:
            ruta_db (str): Ruta del archivo de la base de datos. Por defecto es 'rutas_ecuador.db'

        Inicializa la conexión a la base de datos y crea las tablas necesarias
        si no existen.
        """
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None
        self.conectar()
        self.crear_tablas()

    def conectar(self):
    
        """
        Método para conectar a la base de datos.

        Establece una conexión con la base de datos SQLite especificada en self.ruta_db.
        Inicializa tanto la conexión como el cursor que se usará para ejecutar consultas.
        Si hay algún error durante la conexión, lo captura y muestra un mensaje.
        """
        try:
            # Establece la conexión con la base de datos
            self.conexion = sqlite3.connect(self.ruta_db)
            # Crea un cursor para ejecutar consultas SQL
            self.cursor = self.conexion.cursor()
            print(f"Conexión establecida con {self.ruta_db}")
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def crear_tablas(self):
    
        """
        Método para crear las tablas necesarias en la base de datos.
        
        Crea dos tablas principales:
        1. 'ciudades': Almacena información de cada ciudad incluyendo sus coordenadas
        2. 'rutas': Almacena las conexiones entre ciudades y sus distancias
        
        También verifica y agrega las columnas de coordenadas si no existen.
        """
        try:
            # Crear tabla de ciudades con sus coordenadas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciudades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                latitud REAL DEFAULT NULL,
                longitud REAL DEFAULT NULL
            )
            ''')
            
            # Crear tabla de rutas con referencias a las ciudades
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rutas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origen_id INTEGER NOT NULL,
                destino_id INTEGER NOT NULL,
                distancia INTEGER NOT NULL,
                FOREIGN KEY (origen_id) REFERENCES ciudades (id),
                FOREIGN KEY (destino_id) REFERENCES ciudades (id),
                UNIQUE (origen_id, destino_id)
            )
            ''')
            
            # Verificar si las columnas de coordenadas existen, si no, agregarlas
            try:
                self.cursor.execute("SELECT latitud, longitud FROM ciudades LIMIT 1")
            except sqlite3.OperationalError:
                # Agregar columnas de coordenadas si no existen
                self.cursor.execute("ALTER TABLE ciudades ADD COLUMN latitud REAL DEFAULT NULL")
                self.cursor.execute("ALTER TABLE ciudades ADD COLUMN longitud REAL DEFAULT NULL")
                print("Columnas de coordenadas agregadas a la tabla ciudades")
            
            # Guardar los cambios en la base de datos
            self.conexion.commit()
            print("Tablas creadas correctamente")
        except sqlite3.Error as e:
            print(f"Error al crear las tablas: {e}")
    
    def agregar_ciudad(self, nombre, latitud=None, longitud=None):
        """
        Método para agregar una nueva ciudad a la base de datos.
        
        Args:
            nombre (str): Nombre de la ciudad a agregar
            latitud (float, optional): Latitud geográfica de la ciudad
            longitud (float, optional): Longitud geográfica de la ciudad
            
        Returns:
            int or None: ID de la ciudad si se agregó correctamente, None si hubo error
        """
        try:
            # Intentar insertar la ciudad, ignorando si ya existe
            self.cursor.execute(
                "INSERT OR IGNORE INTO ciudades (nombre, latitud, longitud) VALUES (?, ?, ?)", 
                (nombre, latitud, longitud)
            )
            self.conexion.commit()
            
            # Si la ciudad ya existía pero sin coordenadas, actualizamos
            if latitud is not None and longitud is not None:
                self.cursor.execute(
                    "UPDATE ciudades SET latitud = ?, longitud = ? WHERE nombre = ? AND (latitud IS NULL OR longitud IS NULL)",
                    (latitud, longitud, nombre)
                )
                self.conexion.commit()
            
            # Obtener el ID de la ciudad (sea recién insertada o existente)
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (nombre,))
            ciudad_id = self.cursor.fetchone()[0]
            return ciudad_id
        except sqlite3.Error as e:
            print(f"Error al agregar ciudad {nombre}: {e}")
            return None
    
    def actualizar_coordenadas(self, nombre, latitud, longitud):
        """
        Método para actualizar las coordenadas geográficas de una ciudad existente.
        
        Args:
            nombre (str): Nombre de la ciudad a actualizar
            latitud (float): Nueva latitud de la ciudad
            longitud (float): Nueva longitud de la ciudad
            
        Returns:
            bool: True si la actualización fue exitosa, False si hubo error
        """
        try:
            # Actualizar las coordenadas de la ciudad especificada
            self.cursor.execute(
                "UPDATE ciudades SET latitud = ?, longitud = ? WHERE nombre = ?",
                (latitud, longitud, nombre)
            )
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar coordenadas de {nombre}: {e}")
            return False
    
    def obtener_coordenadas(self, nombre):
        """
        Método para obtener las coordenadas geográficas de una ciudad.
        
        Args:
            nombre (str): Nombre de la ciudad a consultar
            
        Returns:
            tuple: (latitud, longitud) si la ciudad existe, (None, None) si no existe o hay error
        """
        try:
            # Consultar las coordenadas de la ciudad especificada
            self.cursor.execute("SELECT latitud, longitud FROM ciudades WHERE nombre = ?", (nombre,))
            resultado = self.cursor.fetchone()
            return resultado if resultado else (None, None)
        except sqlite3.Error as e:
            print(f"Error al obtener coordenadas de {nombre}: {e}")
            return (None, None)
            
    def agregar_ruta(self, origen, destino, distancia, origen_lat=None, origen_lng=None, destino_lat=None, destino_lng=None):
        """
        Método para agregar una nueva ruta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen
            destino (str): Nombre de la ciudad de destino
            distancia (int): Distancia en kilómetros entre las ciudades
            origen_lat (float, optional): Latitud de la ciudad de origen
            origen_lng (float, optional): Longitud de la ciudad de origen
            destino_lat (float, optional): Latitud de la ciudad de destino
            destino_lng (float, optional): Longitud de la ciudad de destino
            
        Returns:
            bool: True si la ruta se agregó correctamente, False si hubo error
        """
        try:
            # Agregar o actualizar las ciudades con sus coordenadas
            origen_id = self.agregar_ciudad(origen, origen_lat, origen_lng)
            destino_id = self.agregar_ciudad(destino, destino_lat, destino_lng)
            
            # Insertar la ruta de ida (origen -> destino)
            self.cursor.execute("""
            INSERT OR REPLACE INTO rutas (origen_id, destino_id, distancia)
            VALUES (?, ?, ?)
            """, (origen_id, destino_id, distancia))
            
            # Insertar la ruta de vuelta (destino -> origen)
            self.cursor.execute("""
            INSERT OR REPLACE INTO rutas (origen_id, destino_id, distancia)
            VALUES (?, ?, ?)
            """, (destino_id, origen_id, distancia))
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al agregar ruta {origen}-{destino}: {e}")
            return False
    
    def eliminar_ruta(self, origen, destino):
        """
        Método para eliminar una ruta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen
            destino (str): Nombre de la ciudad de destino
            
        Returns:
            bool: True si la ruta se eliminó correctamente, False si hubo error
        """
        try:
            # Obtener los IDs de las ciudades
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (origen,))
            origen_id = self.cursor.fetchone()
            
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (destino,))
            destino_id = self.cursor.fetchone()
            
            # Verificar que ambas ciudades existan
            if not origen_id or not destino_id:
                print("Ciudad de origen o destino no encontrada")
                return False
            
            # Eliminar la ruta de ida (origen -> destino)
            self.cursor.execute("""
            DELETE FROM rutas WHERE origen_id = ? AND destino_id = ?
            """, (origen_id[0], destino_id[0]))
            
            # Eliminar la ruta de vuelta (destino -> origen)
            self.cursor.execute("""
            DELETE FROM rutas WHERE origen_id = ? AND destino_id = ?
            """, (destino_id[0], origen_id[0]))
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al eliminar ruta {origen}-{destino}: {e}")
            return False
    
    def eliminar_ciudad(self, nombre):
        """
        Método para eliminar una ciudad y todas sus rutas asociadas de la base de datos.
        
        Args:
            nombre (str): Nombre de la ciudad a eliminar
            
        Returns:
            bool: True si la ciudad se eliminó correctamente, False si hubo error o la ciudad no existe
        """
        try:
            # Obtener el ID de la ciudad a eliminar
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (nombre,))
            resultado = self.cursor.fetchone()
            if not resultado:
                print(f"La ciudad {nombre} no existe")
                return False
            
            ciudad_id = resultado[0]
            
            # Eliminar todas las rutas que involucran a esta ciudad (tanto como origen como destino)
            self.cursor.execute("DELETE FROM rutas WHERE origen_id = ? OR destino_id = ?", (ciudad_id, ciudad_id))
            
            # Eliminar la ciudad de la tabla ciudades
            self.cursor.execute("DELETE FROM ciudades WHERE id = ?", (ciudad_id,))
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al eliminar ciudad {nombre}: {e}")
            return False
    
    def obtener_distancia(self, origen, destino):
        """
        Método para obtener la distancia entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen
            destino (str): Nombre de la ciudad de destino
            
        Returns:
            int or None: Distancia en kilómetros si existe la ruta, None si no existe o hay error
        """
        try:
            # Consultar la distancia entre las dos ciudades
            self.cursor.execute("""
            SELECT r.distancia
            FROM rutas r
            JOIN ciudades c_origen ON r.origen_id = c_origen.id
            JOIN ciudades c_destino ON r.destino_id = c_destino.id
            WHERE c_origen.nombre = ? AND c_destino.nombre = ?
            """, (origen, destino))
            
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else None
        except sqlite3.Error as e:
            print(f"Error al obtener distancia {origen}-{destino}: {e}")
            return None
    
    def listar_ciudades(self):
        """
        Método para obtener la lista de todas las ciudades en la base de datos.
        
        Returns:
            list: Lista de nombres de ciudades ordenados alfabéticamente
        """
        try:
            # Consultar todos los nombres de ciudades ordenados alfabéticamente
            self.cursor.execute("SELECT nombre FROM ciudades ORDER BY nombre")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al listar ciudades: {e}")
            return []
    
    def listar_ciudades_con_coordenadas(self):
        """
        Método para obtener la lista de todas las ciudades con sus coordenadas geográficas.
        
        Returns:
            list: Lista de diccionarios con información de cada ciudad:
                    [{"nombre": str, "latitud": float, "longitud": float}, ...]
        """
        try:
            # Consultar todas las ciudades con sus coordenadas
            self.cursor.execute("SELECT nombre, latitud, longitud FROM ciudades ORDER BY nombre")
            return [{"nombre": row[0], "latitud": row[1], "longitud": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al listar ciudades con coordenadas: {e}")
            return []
    
    def listar_conexiones(self, ciudad):
        """
        Método para obtener todas las conexiones (rutas) desde una ciudad específica.
        
        Args:
            ciudad (str): Nombre de la ciudad de la cual se quieren obtener las conexiones
            
        Returns:
            dict: Diccionario con las ciudades conectadas y sus distancias:
                    {"ciudad_destino": distancia, ...}
        """
        try:
            # Consultar todas las rutas que parten desde la ciudad especificada
            self.cursor.execute("""
            SELECT c_destino.nombre, r.distancia
            FROM rutas r
            JOIN ciudades c_origen ON r.origen_id = c_origen.id
            JOIN ciudades c_destino ON r.destino_id = c_destino.id
            WHERE c_origen.nombre = ?
            """, (ciudad,))
            
            # Convertir los resultados en un diccionario
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Error al listar conexiones de {ciudad}: {e}")
            return {}
    
    def obtener_grafo_completo(self):
        """
        Método para obtener una representación completa del grafo de ciudades y rutas.
        
        Returns:
            dict: Diccionario que representa el grafo completo, donde:
                    - Las claves son nombres de ciudades
                    - Los valores son diccionarios con las ciudades conectadas y sus distancias
                    Ejemplo: {"Quito": {"Ambato": 111, "Latacunga": 89}, ...}
        """
        grafo = {}
        
        try:
            # Obtener lista de todas las ciudades
            ciudades = self.listar_ciudades()
            
            # Para cada ciudad, obtener sus conexiones
            for ciudad in ciudades:
                grafo[ciudad] = self.listar_conexiones(ciudad)
            
            return grafo
        except sqlite3.Error as e:
            print(f"Error al obtener grafo completo: {e}")
            return {}
    
    def obtener_grafo_completo_con_coords(self):
        """
        Método para obtener una representación completa del grafo incluyendo coordenadas.
        
        Returns:
            tuple: (grafo, coords) donde:
                    - grafo: Diccionario con la estructura de conexiones
                    - coords: Diccionario con las coordenadas de cada ciudad
                    Ejemplo: ({"Quito": {"Ambato": 111}}, {"Quito": {"lat": -0.18, "lng": -78.46}})
        """
        grafo = {}
        coords = {}
        
        try:
            # Obtener todas las ciudades con sus coordenadas
            self.cursor.execute("SELECT nombre, latitud, longitud FROM ciudades")
            for nombre, lat, lon in self.cursor.fetchall():
                coords[nombre] = {"lat": lat, "lng": lon}
                grafo[nombre] = {}
            
            # Obtener todas las conexiones entre ciudades
            self.cursor.execute("""
            SELECT c_origen.nombre, c_destino.nombre, r.distancia
            FROM rutas r
            JOIN ciudades c_origen ON r.origen_id = c_origen.id
            JOIN ciudades c_destino ON r.destino_id = c_destino.id
            """)
            
            # Construir el grafo con las conexiones
            for origen, destino, distancia in self.cursor.fetchall():
                grafo[origen][destino] = distancia
            
            return grafo, coords
        except sqlite3.Error as e:
            print(f"Error al obtener grafo completo con coordenadas: {e}")
            return {}, {}
    
    def importar_grafo(self, grafo_dict, coords_dict=None):
        """
        Método para importar un grafo completo a la base de datos.
        
        Args:
            grafo_dict (dict): Diccionario que representa el grafo a importar
            coords_dict (dict, optional): Diccionario con las coordenadas de las ciudades
            
        Returns:
            bool: True si la importación fue exitosa, False si hubo error
        """
        try:
            # Limpiar las tablas existentes
            self.cursor.execute("DELETE FROM rutas")
            self.cursor.execute("DELETE FROM ciudades")
            self.conexion.commit()
            
            # Importar cada ciudad y sus conexiones
            for origen, destinos in grafo_dict.items():
                # Obtener coordenadas si están disponibles
                lat, lng = None, None
                if coords_dict and origen in coords_dict:
                    lat = coords_dict[origen].get("lat")
                    lng = coords_dict[origen].get("lng")
                
                # Agregar cada conexión
                for destino, distancia in destinos.items():
                    dest_lat, dest_lng = None, None
                    if coords_dict and destino in coords_dict:
                        dest_lat = coords_dict[destino].get("lat")
                        dest_lng = coords_dict[destino].get("lng")
                    
                    self.agregar_ruta(origen, destino, distancia, lat, lng, dest_lat, dest_lng)
            
            return True
        except sqlite3.Error as e:
            print(f"Error al importar grafo: {e}")
            return False

    def importar_desde_json(self, ruta_archivo):
        """
        Método para importar un grafo desde un archivo JSON.
        
        Args:
            ruta_archivo (str): Ruta del archivo JSON a importar
            
        Returns:
            bool: True si la importación fue exitosa, False si hubo error
        """
        try:
            # Leer el archivo JSON
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Verificar el formato del JSON y llamar al método de importación apropiado
            if isinstance(datos, dict) and not ("grafo" in datos and "coords" in datos):
                # Formato antiguo: solo grafo sin coordenadas
                return self.importar_grafo(datos)
            else:
                # Formato nuevo: grafo con coordenadas
                return self.importar_grafo(datos.get("grafo", {}), datos.get("coords", {}))
        except Exception as e:
            print(f"Error al importar desde JSON: {e}")
            return False
    
    def exportar_a_json(self, ruta_archivo):
        """
        Método para exportar el grafo completo con coordenadas a un archivo JSON.
        
        Args:
            ruta_archivo (str): Ruta donde se guardará el archivo JSON
            
        Returns:
            bool: True si la exportación fue exitosa, False si hubo error
        """
        try:
            # Obtener el grafo completo con coordenadas
            grafo_dict, coords_dict = self.obtener_grafo_completo_con_coords()
            
            # Crear la estructura de datos para exportar
            datos = {
                "grafo": grafo_dict,
                "coords": coords_dict
            }
            
            # Escribir el archivo JSON con formato legible
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al exportar a JSON: {e}")
            return False
    
    def cerrar(self):
        """
        Método para cerrar la conexión con la base de datos.
        
        Este método debe ser llamado cuando ya no se necesite la conexión
        para liberar los recursos del sistema.
        """
        if self.conexion:
            self.conexion.close()
            print("Conexión a la base de datos cerrada")


if __name__ == "__main__":
    """
    Bloque principal de ejecución del script.
    
    Este código se ejecuta cuando el archivo se corre directamente (no cuando se importa como módulo).
    Contiene ejemplos de uso de la clase BaseDatosRutas:
    1. Creación de una base de datos de prueba
    2. Inserción de ciudades con coordenadas
    3. Creación de rutas entre ciudades
    4. Consultas básicas
    5. Exportación a JSON
    """
    # Crear una instancia de la base de datos de prueba
    db = BaseDatosRutas('rutas_ecuador_test.db')
    
    # Agregar algunas ciudades principales del Ecuador con sus coordenadas
    db.agregar_ciudad("Quito", -0.1807, -78.4678)
    db.agregar_ciudad("Ambato", -1.2391, -78.6273)
    db.agregar_ciudad("Latacunga", -0.9304, -78.6155)
    db.agregar_ciudad("Riobamba", -1.6635, -78.6535)
    
    # Crear rutas entre las ciudades con sus distancias en kilómetros
    db.agregar_ruta("Quito", "Ambato", 111)
    db.agregar_ruta("Quito", "Latacunga", 89)
    db.agregar_ruta("Ambato", "Riobamba", 54)
    
    # Mostrar las ciudades en la base de datos
    print("Ciudades en la base de datos:")
    print(db.listar_ciudades())
    
    # Mostrar las ciudades con sus coordenadas
    print("\nCiudades con coordenadas:")
    ciudades_con_coords = db.listar_ciudades_con_coordenadas()
    for ciudad in ciudades_con_coords:
        print(f"{ciudad['nombre']}: ({ciudad['latitud']}, {ciudad['longitud']})")
    
    # Mostrar las conexiones desde Quito
    print("\nConexiones desde Quito:")
    print(db.listar_conexiones("Quito"))
    
    # Obtener y mostrar la distancia entre Quito y Ambato
    distancia = db.obtener_distancia("Quito", "Ambato")
    print(f"\nDistancia entre Quito y Ambato: {distancia} km")
    
    # Obtener y mostrar el grafo completo con coordenadas
    grafo, coords = db.obtener_grafo_completo_con_coords()
    print("\nGrafo completo con coordenadas:")
    print(json.dumps({"grafo": grafo, "coords": coords}, indent=2))
    
    # Exportar el grafo a un archivo JSON
    db.exportar_a_json('grafo_test.json')
    print("\nGrafo exportado a grafo_test.json")
    
    # Cerrar la conexión con la base de datos
    db.cerrar()