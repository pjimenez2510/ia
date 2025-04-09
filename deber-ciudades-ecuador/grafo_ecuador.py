# Importación de la librería json para trabajar con archivos JSON
# Se utiliza para cargar y guardar el grafo en formato JSON
import json

# Importación de heapq para implementar colas de prioridad
# Se utiliza en los algoritmos de búsqueda de rutas más cortas
import heapq

# Importación de math para operaciones matemáticas
# Se utiliza para calcular distancias en línea recta entre ciudades
import math

# Importación de deque de collections para implementar colas
# Se utiliza en los algoritmos de búsqueda en amplitud
from collections import deque

# Importación de matplotlib.pyplot para visualización de gráficos
# Se utiliza para dibujar el grafo y las rutas
import matplotlib.pyplot as plt

# Importación de networkx para manipulación de grafos
# Se utiliza para crear y manipular la estructura del grafo
import networkx as nx

# Importación de to_rgba de matplotlib.colors para manejo de colores
# Se utiliza para personalizar la visualización del grafo
from matplotlib.colors import to_rgba

"""
    Clase que representa el grafo de ciudades del Ecuador y sus conexiones.
    
    Esta clase permite:
    - Almacenar ciudades con sus coordenadas geográficas
    - Representar las conexiones entre ciudades y sus distancias
    - Implementar algoritmos de búsqueda de rutas
    - Visualizar el grafo y las rutas encontradas
"""
class GrafoEcuador:
    """
        Constructor de la clase GrafoEcuador.
        
        Args:
            grafo_json (str or dict, optional): Ruta a un archivo JSON o diccionario con el grafo.
                Si es None, se carga el grafo por defecto con las principales ciudades del Ecuador.
        
        Inicializa el grafo con las coordenadas por defecto de las ciudades del Ecuador
        y carga el grafo desde el archivo JSON si se proporciona.
    """
    def __init__(self, grafo_json=None):
        # Coordenadas por defecto de ciudades del Ecuador (latitud, longitud)
        self.coordenadas = {
            "Ambato": (-1.2391, -78.6273),
            "Azogues": (-2.7402, -78.8467),
            "Babahoyo": (-1.8017, -79.5343),
            "Cuenca": (-2.9001, -79.0059),
            "Esmeraldas": (0.9592, -79.6539),
            "Guaranda": (-1.5908, -79.0012),
            "Guayaquil": (-2.1894, -79.8891),
            "Ibarra": (0.3517, -78.1223),
            "Latacunga": (-0.9304, -78.6155),
            "Loja": (-3.9931, -79.2042),
            "Macas": (-2.3046, -78.1192),
            "Machala": (-3.2582, -79.9607),
            "Nueva Loja": (0.0876, -76.8920),
            "Portoviejo": (-1.0546, -80.4545),
            "Puyo": (-1.4854, -77.9960),
            "Quito": (-0.1807, -78.4678),
            "Riobamba": (-1.6635, -78.6535),
            "Tena": (-0.9940, -77.8159),
            "Tulcán": (0.8124, -77.7172),
            "Zamora": (-4.0678, -78.9551),
            "Aloag": (-0.4583, -78.5809),
            "Sto. Domingo": (-0.2522, -79.1716),
            "Baños": (-1.3926, -78.4258),
            "Bahía de Caraquez": (-0.5975, -80.4239),
            "Baeza": (-0.4605, -77.8887),
            "Rumichaca": (0.8187, -77.6657),
            "Macara": (-4.3773, -79.9434),
            "Huaquillas": (-3.4766, -80.2297),
            "Manta": (-0.9676, -80.7089),
            "Otavalo": (0.2343, -78.2610),
            "Salinas": (-2.2013, -80.9765),
            "San Lorenzo": (1.2864, -78.8361),
            "Quevedo": (-1.0287, -79.4632),
            "Quininde": (0.3147, -79.4701),
            "Pte. San Miguel": (1.1117, -77.5822),
            "Pto. Putumayo": (0.0000, -75.0000),  
            "Pto. Morona": (-2.9000, -77.7500),   
            "Muisne": (0.6099, -80.0210),
            "Pedernales": (0.0731, -80.0532)
        }
        
        # Cargar el grafo desde el archivo JSON o usar el grafo por defecto
        if grafo_json is None:
            self.grafo = self.cargar_grafo_completo()
        elif isinstance(grafo_json, dict):
            if "grafo" in grafo_json and "coords" in grafo_json:
                self.grafo = grafo_json["grafo"]
                self.coordenadas = {ciudad: (datos["lat"], datos["lng"]) 
                                   for ciudad, datos in grafo_json["coords"].items() 
                                   if datos["lat"] is not None and datos["lng"] is not None}
            else:
                self.grafo = grafo_json
        else:
            try:
                with open(grafo_json, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                if "grafo" in datos and "coords" in datos:
                    self.grafo = datos["grafo"]
                    self.coordenadas = {ciudad: (datos["coords"][ciudad]["lat"], datos["coords"][ciudad]["lng"]) 
                                       for ciudad in datos["coords"] 
                                       if datos["coords"][ciudad]["lat"] is not None and datos["coords"][ciudad]["lng"] is not None}
                else:
                    self.grafo = datos
            except Exception as e:
                print(f"Error al cargar el grafo desde JSON: {e}")
                self.grafo = {}
        
        # Lista de ciudades en el grafo
        self.ciudades = list(self.grafo.keys())
    
    """
        Carga el grafo completo por defecto con las principales ciudades del Ecuador y sus conexiones.
        
        Returns:
            dict: Un diccionario que representa el grafo, donde las claves son las ciudades
            y los valores son diccionarios con las ciudades conectadas y sus distancias en kilómetros.
            
        El grafo incluye las principales ciudades del Ecuador y sus conexiones por carretera,
        con las distancias aproximadas entre ellas.
    """
    def cargar_grafo_completo(self):
        # Mantiene el grafo por defecto
        return {
            "Ambato": {"Azogues": 280, "Babahoyo": 212, "Cuenca": 321, "Esmeraldas": 371, "Guaranda": 92, 
                      "Guayaquil": 277, "Ibarra": 254, "Latacunga": 41, "Loja": 529, "Baños": 40, 
                      "Quito": 111, "Riobamba": 54, "Puyo": 102},
            "Azogues": {"Ambato": 280, "Babahoyo": 231, "Cuenca": 41, "Guaranda": 260, 
                       "Guayaquil": 209, "Riobamba": 227, "Machala": 194},
            "Babahoyo": {"Ambato": 212, "Azogues": 231, "Cuenca": 272, "Guaranda": 123, 
                        "Guayaquil": 63, "Riobamba": 177, "Quevedo": 103, "Sto. Domingo": 205},
            "Cuenca": {"Ambato": 321, "Azogues": 41, "Babahoyo": 272, "Guayaquil": 250, 
                      "Loja": 253, "Machala": 194, "Riobamba": 272},
            "Esmeraldas": {"Ambato": 371, "Quito": 318, "Sto. Domingo": 177, "Quininde": 98},
            "Guaranda": {"Ambato": 92, "Azogues": 260, "Babahoyo": 123, "Guayaquil": 185,
                        "Riobamba": 107},
            "Guayaquil": {"Ambato": 277, "Azogues": 209, "Babahoyo": 63, "Cuenca": 250, 
                         "Machala": 200, "Quevedo": 175, "Salinas": 173},
            "Ibarra": {"Ambato": 254, "Quito": 115, "Tulcán": 127, "Otavalo": 26},
            "Latacunga": {"Ambato": 41, "Quito": 89, "Riobamba": 95, "Aloag": 56},
            "Loja": {"Ambato": 529, "Cuenca": 253, "Machala": 253, "Zamora": 57},
            "Quito": {"Ambato": 111, "Ibarra": 115, "Latacunga": 89, "Otavalo": 106, 
                     "Riobamba": 188, "Sto. Domingo": 133, "Baeza": 108},
            "Riobamba": {"Ambato": 54, "Azogues": 227, "Babahoyo": 177, "Cuenca": 272, 
                        "Guaranda": 107, "Latacunga": 95, "Quito": 188, "Baños": 62},
            "Sto. Domingo": {"Ambato": 194, "Babahoyo": 205, "Esmeraldas": 177, 
                           "Quito": 133, "Quevedo": 113, "Quininde": 130},
            "Machala": {"Cuenca": 194, "Guayaquil": 200, "Loja": 253, "Huaquillas": 74},
            "Baños": {"Ambato": 40, "Riobamba": 62, "Puyo": 60, "Tena": 139},
            "Puyo": {"Ambato": 102, "Baños": 60, "Tena": 85, "Macas": 135},
            "Tena": {"Ambato": 180, "Baños": 139, "Puyo": 85, "Quito": 186, "Baeza": 52},
            "Tulcán": {"Ibarra": 127, "Quito": 238, "Rumichaca": 3},
            "Otavalo": {"Ibarra": 26, "Quito": 106},
            "Quevedo": {"Babahoyo": 103, "Guayaquil": 175, "Sto. Domingo": 113, "Portoviejo": 188},
            "Portoviejo": {"Quevedo": 188, "Manta": 45, "Bahía de Caraquez": 65},
            "Manta": {"Portoviejo": 45, "Bahía de Caraquez": 89},
            "Bahía de Caraquez": {"Portoviejo": 65, "Manta": 89, "Pedernales": 120},
            "Pedernales": {"Bahía de Caraquez": 120, "Sto. Domingo": 193},
            "Salinas": {"Guayaquil": 173},
            "Huaquillas": {"Machala": 74},
            "Baeza": {"Quito": 108, "Tena": 52, "Nueva Loja": 149},
            "Nueva Loja": {"Baeza": 149, "Pte. San Miguel": 89},
            "Pte. San Miguel": {"Nueva Loja": 89, "Pto. Putumayo": 140},
            "Pto. Putumayo": {"Pte. San Miguel": 140},
            "Macas": {"Puyo": 135, "Pto. Morona": 184},
            "Pto. Morona": {"Macas": 184},
            "Zamora": {"Loja": 57},
            "Quininde": {"Esmeraldas": 98, "Sto. Domingo": 130, "Muisne": 145},
            "Muisne": {"Quininde": 145, "Esmeraldas": 98},
            "Aloag": {"Latacunga": 56, "Quito": 30},
            "Rumichaca": {"Tulcán": 3},
            "Macara": {"Loja": 195}
        }
    
    """
        Guarda el grafo actual en un archivo JSON.
        
        Args:
            ruta_archivo (str): Ruta del archivo donde se guardará el grafo.
            
        El archivo JSON contendrá tanto el grafo como las coordenadas de las ciudades,
        permitiendo su posterior carga y reconstrucción.
    """
    def guardar_grafo(self, ruta_archivo):
        datos = {
            "grafo": self.grafo,
            "coords": {ciudad: {"lat": lat, "lng": lng} for ciudad, (lat, lng) in self.coordenadas.items()}
        }
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"Grafo guardado en {ruta_archivo}")
    
    """
        Agrega una nueva conexión entre dos ciudades en el grafo.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            distancia (float): Distancia en kilómetros entre las ciudades.
            
        La conexión se agrega en ambas direcciones (origen->destino y destino->origen)
        para mantener la simetría del grafo.
    """
    def agregar_conexion(self, origen, destino, distancia):
        if origen not in self.grafo:
            self.grafo[origen] = {}
            self.ciudades.append(origen)
        
        if destino not in self.grafo:
            self.grafo[destino] = {}
            self.ciudades.append(destino)
        
        self.grafo[origen][destino] = distancia
        self.grafo[destino][origen] = distancia
        
        print(f"Conexión agregada: {origen} - {destino} = {distancia} km")
    
    """
        Agrega una nueva ciudad al grafo con sus coordenadas geográficas.
        
        Args:
            nombre (str): Nombre de la ciudad a agregar.
            latitud (float): Latitud de la ciudad en grados decimales.
            longitud (float): Longitud de la ciudad en grados decimales.
            
        Si la ciudad ya existe, se actualizan sus coordenadas.
    """
    def agregar_ciudad(self, nombre, latitud, longitud):
        if nombre not in self.coordenadas:
            self.coordenadas[nombre] = (latitud, longitud)
            
        if nombre not in self.grafo:
            self.grafo[nombre] = {}
            self.ciudades.append(nombre)
            print(f"Ciudad agregada: {nombre} en ({latitud}, {longitud})")
        else:
            print(f"Ciudad {nombre} actualizada con coordenadas ({latitud}, {longitud})")
    
    """
        Elimina una conexión entre dos ciudades del grafo.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        La conexión se elimina en ambas direcciones para mantener la consistencia del grafo.
    """
    def eliminar_conexion(self, origen, destino):
        if origen in self.grafo and destino in self.grafo[origen]:
            del self.grafo[origen][destino]
            print(f"Conexión eliminada: {origen} - {destino}")
        
        if destino in self.grafo and origen in self.grafo[destino]:
            del self.grafo[destino][origen]
    
    """
        Elimina una ciudad del grafo y todas sus conexiones.
        
        Args:
            nombre (str): Nombre de la ciudad a eliminar.
            
        Returns:
            bool: True si la ciudad fue eliminada exitosamente, False si la ciudad no existía.
            
        El método elimina la ciudad del grafo, sus coordenadas y todas las conexiones
        que otras ciudades tenían con ella.
    """
    def eliminar_ciudad(self, nombre):
        if nombre in self.grafo:
            # Eliminar todas las conexiones a esta ciudad
            for ciudad in self.grafo:
                if nombre in self.grafo[ciudad]:
                    del self.grafo[ciudad][nombre]
            
            # Eliminar la ciudad y sus conexiones
            del self.grafo[nombre]
            if nombre in self.coordenadas:
                del self.coordenadas[nombre]
            self.ciudades.remove(nombre)
            print(f"Ciudad eliminada: {nombre}")
            return True
        return False
    
    """
        Obtiene la distancia en kilómetros entre dos ciudades conectadas directamente.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            float or None: La distancia en kilómetros si existe una conexión directa,
            None si no hay conexión directa entre las ciudades.
    """
    def obtener_distancia(self, origen, destino):
        if origen in self.grafo and destino in self.grafo[origen]:
            return self.grafo[origen][destino]
        return None
    
    """
        Calcula la distancia en línea recta entre dos ciudades usando la fórmula de Haversine.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            float or None: La distancia en kilómetros en línea recta si ambas ciudades
            tienen coordenadas, None si alguna ciudad no tiene coordenadas.
            
        La fórmula de Haversine calcula la distancia entre dos puntos en una esfera
        usando sus coordenadas geográficas (latitud y longitud).
    """
    def obtener_distancia_linea_recta(self, origen, destino):
        """Calcula la distancia en línea recta entre dos ciudades usando la fórmula de Haversine."""
        if origen not in self.coordenadas or destino not in self.coordenadas:
            return None
        
        lat1, lon1 = self.coordenadas[origen]
        lat2, lon2 = self.coordenadas[destino]
        
        # Convertir a radianes
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radio de la Tierra en km
        
        return c * r
    
    """
        Obtiene una lista ordenada de todas las ciudades en el grafo.
        
        Returns:
            list: Lista de strings con los nombres de las ciudades ordenados alfabéticamente.
    """
    def listar_ciudades(self):
        return sorted(self.ciudades)
    
    """
        Obtiene un diccionario con todas las ciudades y sus coordenadas geográficas.
        
        Returns:
            dict: Diccionario donde las claves son los nombres de las ciudades y los valores
            son tuplas (latitud, longitud) con las coordenadas de cada ciudad.
            
        Si una ciudad no tiene coordenadas, se devuelve (None, None) como sus coordenadas.
    """
    def listar_ciudades_con_coordenadas(self):
        """Devuelve un diccionario con las ciudades y sus coordenadas."""
        return {ciudad: self.coordenadas.get(ciudad, (None, None)) for ciudad in self.ciudades}
    
    """
        Obtiene todas las conexiones directas de una ciudad específica.
        
        Args:
            ciudad (str): Nombre de la ciudad de la cual se desean obtener las conexiones.
            
        Returns:
            dict: Diccionario donde las claves son las ciudades conectadas y los valores
            son las distancias en kilómetros. Si la ciudad no existe, retorna un diccionario vacío.
    """
    def listar_conexiones(self, ciudad):
        if ciudad in self.grafo:
            return self.grafo[ciudad]
        return {}
    
    """
        Implementa el algoritmo de búsqueda en amplitud (BFS) para encontrar una ruta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            tuple: (ruta, distancia) donde:
                - ruta: Lista de ciudades que forman el camino desde origen hasta destino
                - distancia: Distancia total en kilómetros del camino
                Si no se encuentra ruta, retorna (None, 0)
                
        El algoritmo BFS explora todos los nodos vecinos antes de pasar a los nodos
        del siguiente nivel, garantizando encontrar el camino con el menor número de
        ciudades intermedias, pero no necesariamente el camino más corto en distancia.
        
        Características:
        - Complejidad temporal: O(V + E) donde V es el número de vértices y E el de aristas
        - Complejidad espacial: O(V)
        - Garantiza encontrar el camino con menos ciudades intermedias
        - No es óptimo en términos de distancia total
    """
    def busqueda_amplitud(self, origen, destino):
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
        
        # Cola para BFS: almacena (ciudad_actual, ruta_hasta_ahora, distancia_total)
        cola = deque([(origen, [origen], 0)])
        visitados = set([origen])
        
        while cola:
            actual, ruta, distancia = cola.popleft()
            
            if actual == destino:
                return ruta, distancia
            
            # Explorar todos los vecinos no visitados
            for vecino, dist in self.grafo[actual].items():
                if vecino not in visitados:
                    visitados.add(vecino)
                    nueva_ruta = ruta + [vecino]
                    nueva_distancia = distancia + dist
                    cola.append((vecino, nueva_ruta, nueva_distancia))
        
        return None, 0
    
    """
        Implementa el algoritmo de búsqueda en profundidad (DFS) para encontrar una ruta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            tuple: (ruta, distancia) donde:
                - ruta: Lista de ciudades que forman el camino desde origen hasta destino
                - distancia: Distancia total en kilómetros del camino
                Si no se encuentra ruta, retorna (None, 0)
                
        El algoritmo DFS explora un camino hasta el final antes de retroceder y probar
        otros caminos. No garantiza encontrar el camino más corto ni el más eficiente.
        
        Características:
        - Complejidad temporal: O(V + E) donde V es el número de vértices y E el de aristas
        - Complejidad espacial: O(V)
        - No garantiza encontrar el camino más corto
        - Puede encontrar una ruta más rápidamente que BFS en algunos casos
        - Útil para explorar todos los caminos posibles
    """
    def busqueda_profundidad(self, origen, destino):
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
    
        visitados = set()
        ruta = []
    
        def dfs(actual, camino, distancia):
            if actual == destino:
                ruta.extend(camino)
                return True, distancia
            
            visitados.add(actual)
            
            for vecino, dist in self.grafo[actual].items():
                if vecino not in visitados:
                    resultado, distancia_total = dfs(vecino, camino + [vecino], distancia + dist)
                    if resultado:
                        return True, distancia_total
            
            return False, 0
    
        resultado, distancia_total = dfs(origen, [origen], 0)
    
        if resultado:
            return ruta, distancia_total
        else:
            return None, 0
    
    """
        Implementa el algoritmo de búsqueda de costo uniforme (Dijkstra) para encontrar
        la ruta más corta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            tuple: (ruta, distancia) donde:
                - ruta: Lista de ciudades que forman el camino más corto desde origen hasta destino
                - distancia: Distancia total en kilómetros del camino más corto
                Si no se encuentra ruta, retorna (None, 0)
                
        El algoritmo de Dijkstra encuentra el camino más corto en términos de distancia
        total, explorando primero los caminos con menor costo acumulado.
        
        Características:
        - Complejidad temporal: O((V + E) log V) donde V es el número de vértices y E el de aristas
        - Complejidad espacial: O(V)
        - Garantiza encontrar el camino más corto en términos de distancia total
        - No puede manejar aristas con pesos negativos
        - Es óptimo para grafos con pesos positivos
    """
    def busqueda_costo_uniforme(self, origen, destino):
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
        
        # Cola de prioridad para Dijkstra: almacena (distancia_acumulada, ciudad_actual, ruta)
        cola_prioridad = [(0, origen, [origen])]
        visitados = set()
        
        while cola_prioridad:
            distancia, actual, ruta = heapq.heappop(cola_prioridad)
            
            if actual == destino:
                return ruta, distancia
            
            if actual in visitados:
                continue
            
            visitados.add(actual)
            
            # Explorar vecinos no visitados
            for vecino, dist in self.grafo[actual].items():
                if vecino not in visitados:
                    nueva_distancia = distancia + dist
                    nueva_ruta = ruta + [vecino]
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino, nueva_ruta))
        
        return None, 0
    
    """
        Implementa el algoritmo de búsqueda A* para encontrar la ruta más corta entre dos ciudades.
        
        Args:
            origen (str): Nombre de la ciudad de origen.
            destino (str): Nombre de la ciudad de destino.
            
        Returns:
            tuple: (ruta, distancia) donde:
                - ruta: Lista de ciudades que forman el camino más corto desde origen hasta destino
                - distancia: Distancia total en kilómetros del camino más corto
                Si no se encuentra ruta, retorna (None, 0)
                
        El algoritmo A* combina las ventajas de Dijkstra (garantía de optimalidad) con una
        heurística informada (distancia en línea recta) para mejorar la eficiencia de la búsqueda.
        
        Características:
        - Complejidad temporal: O((V + E) log V) donde V es el número de vértices y E el de aristas
        - Complejidad espacial: O(V)
        - Garantiza encontrar el camino más corto si la heurística es admisible
        - Más eficiente que Dijkstra al reducir el espacio de búsqueda
        - Utiliza la distancia en línea recta como heurística para guiar la búsqueda
        
        La heurística utilizada es la distancia en línea recta entre ciudades, que es admisible
        ya que nunca sobreestima la distancia real (la distancia real siempre es mayor o igual
        a la distancia en línea recta).
    """
    def busqueda_a_estrella(self, origen, destino):
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
        
        # Comprobar si tenemos coordenadas para ambas ciudades
        if origen not in self.coordenadas or destino not in self.coordenadas:
            # Si no tenemos coordenadas, caemos en Dijkstra
            return self.busqueda_costo_uniforme(origen, destino)
        
        # Cola de prioridad para A*: almacena (f, g, ciudad_actual, ruta)
        # donde f = g + h (costo total estimado)
        # g = costo real desde el origen
        # h = heurística (distancia en línea recta al destino)
        cola_prioridad = [(0, 0, origen, [origen])]
        visitados = set()
        g_valores = {origen: 0}  # Costo real desde el origen
        
        while cola_prioridad:
            _, g_actual, actual, ruta = heapq.heappop(cola_prioridad)
            
            if actual == destino:
                return ruta, g_actual
            
            if actual in visitados:
                continue
            
            visitados.add(actual)
            
            for vecino, dist in self.grafo[actual].items():
                nuevo_g = g_actual + dist
                
                # Si ya hemos encontrado un camino mejor a este nodo, continuamos
                if vecino in g_valores and g_valores[vecino] <= nuevo_g:
                    continue
                
                g_valores[vecino] = nuevo_g
                # Heurística: distancia en línea recta hasta el destino
                h = self.obtener_distancia_linea_recta(vecino, destino)
                if h is None:
                    h = 0  # Si no podemos calcular la heurística, usamos 0
                
                f = nuevo_g + h
                nueva_ruta = ruta + [vecino]
                heapq.heappush(cola_prioridad, (f, nuevo_g, vecino, nueva_ruta))
        
        return None, 0
    
    """
        Visualiza el grafo de ciudades y sus conexiones.
        
        Args:
            ruta (list, optional): Lista de ciudades que forman una ruta a resaltar.
            usar_mapa_real (bool, optional): Si es True, usa las coordenadas reales de las ciudades
                para posicionarlas en el mapa. Si es False, usa un layout automático.
            ax (matplotlib.axes.Axes, optional): Ejes de matplotlib donde dibujar el grafo.
                Si es None, se crea una nueva figura.
                
        Returns:
            matplotlib.axes.Axes: Los ejes donde se dibujó el grafo.
            
        El método permite visualizar el grafo de dos formas:
        1. Usando un layout automático (usar_mapa_real=False):
           - Las ciudades se distribuyen automáticamente para minimizar cruces
           - Se muestran las distancias en las aristas
           
        2. Usando coordenadas reales (usar_mapa_real=True):
           - Las ciudades se posicionan según sus coordenadas geográficas
           - Se dibuja un fondo simplificado del mapa de Ecuador
           - Las distancias se omiten para evitar sobrecarga visual
           
        Si se proporciona una ruta, esta se resalta en rojo y con mayor grosor.
    """
    def visualizar_grafo(self, ruta=None, usar_mapa_real=False, ax=None):
        # Crear un nuevo gráfico si no se proporcionó uno
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 10))
        
        G = nx.Graph()
        
        # Agregar nodos y aristas al grafo
        for origen, destinos in self.grafo.items():
            G.add_node(origen)
            for destino, distancia in destinos.items():
                G.add_edge(origen, destino, weight=distancia)
        
        if usar_mapa_real and all(ciudad in self.coordenadas for ciudad in self.grafo):
            # Usar posiciones geográficas reales para los nodos
            pos = {ciudad: (lon, lat) for ciudad, (lat, lon) in self.coordenadas.items()}
            
            # Fondo del mapa de Ecuador (simplificado)
            ax.set_facecolor('#e6f7ff')  # Color azul claro como fondo
            
            # Dibujar bordes aproximados de Ecuador
            ecuador_border = [
                (-81.0, 1.5),  # Esquina noroeste
                (-75.0, 1.5),  # Esquina noreste
                (-75.0, -5.0),  # Esquina sureste
                (-81.0, -5.0),  # Esquina suroeste
                (-81.0, 1.5)    # Cerrar el polígono
            ]
            lons, lats = zip(*ecuador_border)
            ax.fill(lons, lats, alpha=0.2, color='green')
            
        else:
            # Usar el layout de spring si no tenemos coordenadas o no queremos usarlas
            pos = nx.spring_layout(G, seed=42)
        
        # Dibujar los nodos
        nodos = nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', ax=ax)
        nodos.set_edgecolor('black')
        
        # Resaltar ruta si se proporciona
        if ruta and len(ruta) > 1:
            ruta_aristas = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
            
            otras_aristas = [(u, v) for u, v in G.edges() if (u, v) not in ruta_aristas and (v, u) not in ruta_aristas]
            nx.draw_networkx_edges(G, pos, edgelist=otras_aristas, width=1, alpha=0.3, ax=ax)
            
            nx.draw_networkx_edges(G, pos, edgelist=ruta_aristas, width=3, edge_color='r', ax=ax)
        else:
            nx.draw_networkx_edges(G, pos, width=1, ax=ax)
        
        # Etiquetar las ciudades
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif', ax=ax)
        
        # Etiquetar las aristas con distancias
        if not usar_mapa_real:  # Las etiquetas de aristas pueden abrumar en un mapa geográfico
            edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, ax=ax)
        
        ax.set_title("Grafo de Distancias entre Ciudades de Ecuador")
        ax.axis('off')
        
        plt.tight_layout()
        
        return ax
        
    """
        Crea una versión interactiva del grafo con funcionalidades adicionales.
        
        Args:
            ruta (list, optional): Lista de ciudades que forman una ruta a resaltar.
            
        Returns:
            tuple: (fig, ax) donde:
                - fig: La figura de matplotlib
                - ax: Los ejes donde se dibujó el grafo
                
        Esta versión interactiva del grafo incluye:
        - Visualización en mapa real por defecto
        - Posibilidad de hacer zoom y pan
        - Mejor visualización de las rutas resaltadas
        - Preparación para futuras funcionalidades interactivas como:
          * Tooltips con información de ciudades
          * Selección de rutas
          * Comparación de algoritmos
          
        Nota: Esta es una versión base que puede ser extendida con más funcionalidades
        interactivas según las necesidades específicas.
    """
    def visualizar_grafo_interactivo(self, ruta=None):
        fig, ax = plt.subplots(figsize=(15, 10))
        
        self.visualizar_grafo(ruta=ruta, usar_mapa_real=True, ax=ax)
        
        return fig, ax


if __name__ == "__main__":
    """
    Bloque principal de ejecución del programa.
    
    Este bloque demuestra las funcionalidades principales de la clase GrafoEcuador:
    1. Creación y carga del grafo
    2. Listado de ciudades disponibles
    3. Comparación de diferentes algoritmos de búsqueda de rutas
    4. Visualización del grafo y las rutas encontradas
    
    El ejemplo utiliza como caso de prueba la ruta entre Quito y Guayaquil,
    mostrando cómo cada algoritmo encuentra diferentes rutas y sus respectivas
    distancias totales.
    
    Se visualiza el grafo de dos formas:
    - Con mapa real: usando las coordenadas geográficas de las ciudades
    - Sin mapa real: usando un layout automático para mejor visualización de conexiones
    
    Este bloque sirve como:
    - Ejemplo de uso de la clase
    - Herramienta de demostración de los algoritmos
    - Punto de entrada para pruebas y experimentación
    """
    grafo = GrafoEcuador()
    
    print("Ciudades disponibles:")
    print(grafo.listar_ciudades())
    
    origen = "Quito"
    destino = "Guayaquil"
    
    # Comparar resultados de diferentes algoritmos
    ruta_bfs, distancia_bfs = grafo.busqueda_amplitud(origen, destino)
    print(f"\nBúsqueda en Amplitud (BFS) desde {origen} hasta {destino}:")
    print(f"Ruta: {' -> '.join(ruta_bfs)}")
    print(f"Distancia total: {distancia_bfs} km")
    
    ruta_dfs, distancia_dfs = grafo.busqueda_profundidad(origen, destino)
    print(f"\nBúsqueda en Profundidad (DFS) desde {origen} hasta {destino}:")
    print(f"Ruta: {' -> '.join(ruta_dfs)}")
    print(f"Distancia total: {distancia_dfs} km")
    
    ruta_ucs, distancia_ucs = grafo.busqueda_costo_uniforme(origen, destino)
    print(f"\nBúsqueda de Costo Uniforme (Dijkstra) desde {origen} hasta {destino}:")
    print(f"Ruta: {' -> '.join(ruta_ucs)}")
    print(f"Distancia total: {distancia_ucs} km")
    
    ruta_astar, distancia_astar = grafo.busqueda_a_estrella(origen, destino)
    print(f"\nBúsqueda A* desde {origen} hasta {destino}:")
    print(f"Ruta: {' -> '.join(ruta_astar)}")
    print(f"Distancia total: {distancia_astar} km")
    
    # Visualizar el grafo con la ruta más corta usando A*
    print("\nVisualizando el grafo con la ruta más corta (A*)...")
    plt.figure(figsize=(15, 10))
    grafo.visualizar_grafo(ruta_astar, usar_mapa_real=True)
    plt.show()
    
    # Mostrar la diferencia entre visualización con y sin mapa real
    plt.figure(figsize=(15, 10))
    grafo.visualizar_grafo(ruta_astar, usar_mapa_real=False)
    plt.show()