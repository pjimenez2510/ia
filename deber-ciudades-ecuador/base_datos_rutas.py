import sqlite3
import json
import os

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
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciudades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
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
            
            self.conexion.commit()
            print("Tablas creadas correctamente")
        except sqlite3.Error as e:
            print(f"Error al crear las tablas: {e}")
    
    def agregar_ciudad(self, nombre):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO ciudades (nombre) VALUES (?)", (nombre,))
            self.conexion.commit()
            
            # Obtener el ID de la ciudad (sea recién insertada o existente)
            self.cursor.execute("SELECT id FROM ciudades WHERE nombre = ?", (nombre,))
            ciudad_id = self.cursor.fetchone()[0]
            return ciudad_id
        except sqlite3.Error as e:
            print(f"Error al agregar ciudad {nombre}: {e}")
            return None
    
    def agregar_ruta(self, origen, destino, distancia):
        
        try:
            origen_id = self.agregar_ciudad(origen)
            destino_id = self.agregar_ciudad(destino)
            
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
    
    def importar_grafo(self, grafo_dict):
        
        try:
            self.cursor.execute("DELETE FROM rutas")
            self.cursor.execute("DELETE FROM ciudades")
            self.conexion.commit()
            
            for origen, destinos in grafo_dict.items():
                for destino, distancia in destinos.items():
                    self.agregar_ruta(origen, destino, distancia)
            
            return True
        except sqlite3.Error as e:
            print(f"Error al importar grafo: {e}")
            return False
    
    def importar_desde_json(self, ruta_archivo):
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                grafo_dict = json.load(f)
            
            return self.importar_grafo(grafo_dict)
        except Exception as e:
            print(f"Error al importar desde JSON: {e}")
            return False
    
    def exportar_a_json(self, ruta_archivo):
        
        try:
            grafo_dict = self.obtener_grafo_completo()
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(grafo_dict, f, ensure_ascii=False, indent=2)
            
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
    
    db.agregar_ruta("Quito", "Ambato", 111)
    db.agregar_ruta("Quito", "Latacunga", 89)
    db.agregar_ruta("Ambato", "Riobamba", 54)
    
    print("Ciudades en la base de datos:")
    print(db.listar_ciudades())
    
    print("\nConexiones desde Quito:")
    print(db.listar_conexiones("Quito"))
    
    distancia = db.obtener_distancia("Quito", "Ambato")
    print(f"\nDistancia entre Quito y Ambato: {distancia} km")
    
    grafo = db.obtener_grafo_completo()
    print("\nGrafo completo:")
    print(json.dumps(grafo, indent=2))
    
    db.exportar_a_json('grafo_test.json')
    print("\nGrafo exportado a grafo_test.json")
    
    db.cerrar()