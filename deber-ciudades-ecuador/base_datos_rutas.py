import sqlite3
import json

class BaseDatosRutas:
    
    def __init__(self, ruta_db='rutas_ecuador.db'):
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None
        self.conectar()
        self.crear_tablas()
    
    def conectar(self):
        try:
            self.conexion = sqlite3.connect(self.ruta_db)
            self.cursor = self.conexion.cursor()
            print(f"Conexión establecida con {self.ruta_db}")
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
    
    def crear_tablas(self):
        try:
            # Modificamos la tabla ciudades para incluir coordenadas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciudades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                latitud REAL DEFAULT NULL,
                longitud REAL DEFAULT NULL
            )
            ''')
            
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
            
            # Verificar si las columnas latitud y longitud existen, si no, agregarlas
            # Esta verificación es necesaria para bases de datos existentes
            try:
                self.cursor.execute("SELECT latitud, longitud FROM ciudades LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE ciudades ADD COLUMN latitud REAL DEFAULT NULL")
                self.cursor.execute("ALTER TABLE ciudades ADD COLUMN longitud REAL DEFAULT NULL")
                print("Columnas de coordenadas agregadas a la tabla ciudades")
            
            self.conexion.commit()
            print("Tablas creadas correctamente")
        except sqlite3.Error as e:
            print(f"Error al crear las tablas: {e}")
    
    def agregar_ciudad(self, nombre, latitud=None, longitud=None):
        try:
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
        try:
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
        try:
            self.cursor.execute("SELECT latitud, longitud FROM ciudades WHERE nombre = ?", (nombre,))
            resultado = self.cursor.fetchone()
            return resultado if resultado else (None, None)
        except sqlite3.Error as e:
            print(f"Error al obtener coordenadas de {nombre}: {e}")
            return (None, None)
    
    def agregar_ruta(self, origen, destino, distancia, origen_lat=None, origen_lng=None, destino_lat=None, destino_lng=None):
        try:
            origen_id = self.agregar_ciudad(origen, origen_lat, origen_lng)
            destino_id = self.agregar_ciudad(destino, destino_lat, destino_lng)
            
            self.cursor.execute("""
            INSERT OR REPLACE INTO rutas (origen_id, destino_id, distancia)
            VALUES (?, ?, ?)
            """, (origen_id, destino_id, distancia))
            
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
        try:
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (origen,))
            origen_id = self.cursor.fetchone()
            
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (destino,))
            destino_id = self.cursor.fetchone()
            
            if not origen_id or not destino_id:
                print("Ciudad de origen o destino no encontrada")
                return False
            
            self.cursor.execute("""
            DELETE FROM rutas WHERE origen_id = ? AND destino_id = ?
            """, (origen_id[0], destino_id[0]))
            
            self.cursor.execute("""
            DELETE FROM rutas WHERE origen_id = ? AND destino_id = ?
            """, (destino_id[0], origen_id[0]))
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al eliminar ruta {origen}-{destino}: {e}")
            return False
    
    def eliminar_ciudad(self, nombre):
        try:
            # Primero obtenemos el ID de la ciudad
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (nombre,))
            resultado = self.cursor.fetchone()
            if not resultado:
                print(f"La ciudad {nombre} no existe")
                return False
            
            ciudad_id = resultado[0]
            
            # Eliminar todas las rutas asociadas con esta ciudad
            self.cursor.execute("DELETE FROM rutas WHERE origen_id = ? OR destino_id = ?", (ciudad_id, ciudad_id))
            
            # Eliminar la ciudad
            self.cursor.execute("DELETE FROM ciudades WHERE id = ?", (ciudad_id,))
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al eliminar ciudad {nombre}: {e}")
            return False
    
    def obtener_distancia(self, origen, destino):
        try:
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
        try:
            self.cursor.execute("SELECT nombre FROM ciudades ORDER BY nombre")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al listar ciudades: {e}")
            return []
    
    def listar_ciudades_con_coordenadas(self):
        try:
            self.cursor.execute("SELECT nombre, latitud, longitud FROM ciudades ORDER BY nombre")
            return [{"nombre": row[0], "latitud": row[1], "longitud": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al listar ciudades con coordenadas: {e}")
            return []
    
    def listar_conexiones(self, ciudad):
        try:
            self.cursor.execute("""
            SELECT c_destino.nombre, r.distancia
            FROM rutas r
            JOIN ciudades c_origen ON r.origen_id = c_origen.id
            JOIN ciudades c_destino ON r.destino_id = c_destino.id
            WHERE c_origen.nombre = ?
            """, (ciudad,))
            
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Error al listar conexiones de {ciudad}: {e}")
            return {}
    
    def obtener_grafo_completo(self):
        grafo = {}
        
        try:
            ciudades = self.listar_ciudades()
            
            for ciudad in ciudades:
                grafo[ciudad] = self.listar_conexiones(ciudad)
            
            return grafo
        except sqlite3.Error as e:
            print(f"Error al obtener grafo completo: {e}")
            return {}
    
    def obtener_grafo_completo_con_coords(self):
        grafo = {}
        coords = {}
        
        try:
            # Obtener todas las ciudades con sus coordenadas
            self.cursor.execute("SELECT nombre, latitud, longitud FROM ciudades")
            for nombre, lat, lon in self.cursor.fetchall():
                coords[nombre] = {"lat": lat, "lng": lon}
                grafo[nombre] = {}
            
            # Obtener todas las conexiones
            self.cursor.execute("""
            SELECT c_origen.nombre, c_destino.nombre, r.distancia
            FROM rutas r
            JOIN ciudades c_origen ON r.origen_id = c_origen.id
            JOIN ciudades c_destino ON r.destino_id = c_destino.id
            """)
            
            for origen, destino, distancia in self.cursor.fetchall():
                grafo[origen][destino] = distancia
            
            return grafo, coords
        except sqlite3.Error as e:
            print(f"Error al obtener grafo completo con coordenadas: {e}")
            return {}, {}
    
    def importar_grafo(self, grafo_dict, coords_dict=None):
        try:
            self.cursor.execute("DELETE FROM rutas")
            self.cursor.execute("DELETE FROM ciudades")
            self.conexion.commit()
            
            for origen, destinos in grafo_dict.items():
                lat, lng = None, None
                if coords_dict and origen in coords_dict:
                    lat = coords_dict[origen].get("lat")
                    lng = coords_dict[origen].get("lng")
                
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
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Verificar si es el formato antiguo o el nuevo con coordenadas
            if isinstance(datos, dict) and not ("grafo" in datos and "coords" in datos):
                # Formato antiguo, solo grafo
                return self.importar_grafo(datos)
            else:
                # Formato nuevo con coordenadas
                return self.importar_grafo(datos.get("grafo", {}), datos.get("coords", {}))
        except Exception as e:
            print(f"Error al importar desde JSON: {e}")
            return False
    
    def exportar_a_json(self, ruta_archivo):
        try:
            grafo_dict, coords_dict = self.obtener_grafo_completo_con_coords()
            
            datos = {
                "grafo": grafo_dict,
                "coords": coords_dict
            }
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al exportar a JSON: {e}")
            return False
    
    def cerrar(self):
        if self.conexion:
            self.conexion.close()
            print("Conexión a la base de datos cerrada")


if __name__ == "__main__":
    db = BaseDatosRutas('rutas_ecuador_test.db')
    
    # Ejemplo con coordenadas
    db.agregar_ciudad("Quito", -0.1807, -78.4678)
    db.agregar_ciudad("Ambato", -1.2391, -78.6273)
    db.agregar_ciudad("Latacunga", -0.9304, -78.6155)
    db.agregar_ciudad("Riobamba", -1.6635, -78.6535)
    
    db.agregar_ruta("Quito", "Ambato", 111)
    db.agregar_ruta("Quito", "Latacunga", 89)
    db.agregar_ruta("Ambato", "Riobamba", 54)
    
    print("Ciudades en la base de datos:")
    print(db.listar_ciudades())
    
    print("\nCiudades con coordenadas:")
    ciudades_con_coords = db.listar_ciudades_con_coordenadas()
    for ciudad in ciudades_con_coords:
        print(f"{ciudad['nombre']}: ({ciudad['latitud']}, {ciudad['longitud']})")
    
    print("\nConexiones desde Quito:")
    print(db.listar_conexiones("Quito"))
    
    distancia = db.obtener_distancia("Quito", "Ambato")
    print(f"\nDistancia entre Quito y Ambato: {distancia} km")
    
    grafo, coords = db.obtener_grafo_completo_con_coords()
    print("\nGrafo completo con coordenadas:")
    print(json.dumps({"grafo": grafo, "coords": coords}, indent=2))
    
    db.exportar_a_json('grafo_test.json')
    print("\nGrafo exportado a grafo_test.json")
    
    db.cerrar()