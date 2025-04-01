import json
import heapq
from collections import deque
import matplotlib.pyplot as plt
import networkx as nx

class GrafoEcuador:
    def __init__(self, grafo_json=None):
        
        if grafo_json is None:
            self.grafo = {
                "Ambato": {"Azogues": 280, "Babahoyo": 212, "Cuenca": 321, "Esmeraldas": 371, "Guaranda": 92, 
                          "Guayaquil": 277, "Ibarra": 254, "Latacunga": 41, "Loja": 529, "Macas": 236, 
                          "Machala": 413, "Nueva Loja": 380, "Portoviejo": 356, "Pto. Fco. De Orellana": 354, 
                          "Puyo": 102, "Quito": 111, "Riobamba": 54, "Tena": 180, "Tulcán": 381, "Zamora": 586, 
                          "Aloag": 97, "Sto. Domingo": 194, "Baños": 40, "Bahía de Caraquez": 416, "Baeza": 219, 
                          "Rumichaca": 385, "Macara": 710, "Huaquillas": 428, "Manta": 385, "Otavalo": 230, 
                          "Salinas": 445, "San Lorenzo": 428, "Quevedo": 212, "Quininde": 280, "Pte. San Miguel": 406, 
                          "Pto. Putumayo": 564, "Pto. Morona": 445, "Muisne": 439, "Pedernales": 318},
            }
            self.grafo = self.cargar_grafo_completo()
        elif isinstance(grafo_json, dict):
            self.grafo = grafo_json
        else:
            try:
                with open(grafo_json, 'r', encoding='utf-8') as f:
                    self.grafo = json.load(f)
            except Exception as e:
                print(f"Error al cargar el grafo desde JSON: {e}")
                self.grafo = {}
        
        self.ciudades = list(self.grafo.keys())
    
    def cargar_grafo_completo(self):
        
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
    
    def guardar_grafo(self, ruta_archivo):
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.grafo, f, ensure_ascii=False, indent=2)
        print(f"Grafo guardado en {ruta_archivo}")
    
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
    
    def eliminar_conexion(self, origen, destino):
        
        if origen in self.grafo and destino in self.grafo[origen]:
            del self.grafo[origen][destino]
            print(f"Conexión eliminada: {origen} - {destino}")
        
        if destino in self.grafo and origen in self.grafo[destino]:
            del self.grafo[destino][origen]
    
    def obtener_distancia(self, origen, destino):
        
        if origen in self.grafo and destino in self.grafo[origen]:
            return self.grafo[origen][destino]
        return None
    
    def listar_ciudades(self):
        
        return sorted(self.ciudades)
    
    def listar_conexiones(self, ciudad):
        
        if ciudad in self.grafo:
            return self.grafo[ciudad]
        return {}
    
    def busqueda_amplitud(self, origen, destino):
        
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
        
        # Cola para BFS
        cola = deque([(origen, [origen], 0)])
        visitados = set([origen])
        
        while cola:
            actual, ruta, distancia = cola.popleft()
            
            if actual == destino:
                return ruta, distancia
            
            for vecino, dist in self.grafo[actual].items():
                if vecino not in visitados:
                    visitados.add(vecino)
                    nueva_ruta = ruta + [vecino]
                    nueva_distancia = distancia + dist
                    cola.append((vecino, nueva_ruta, nueva_distancia))
        
        return None, 0
    
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
    
    def busqueda_costo_uniforme(self, origen, destino):
        
        if origen not in self.grafo or destino not in self.grafo:
            return None, 0
        
        # Cola de prioridad para Dijkstra
        cola_prioridad = [(0, origen, [origen])]
        visitados = set()
        
        while cola_prioridad:
            distancia, actual, ruta = heapq.heappop(cola_prioridad)
            
            if actual == destino:
                return ruta, distancia
            
            if actual in visitados:
                continue
            
            visitados.add(actual)
            
            for vecino, dist in self.grafo[actual].items():
                if vecino not in visitados:
                    nueva_distancia = distancia + dist
                    nueva_ruta = ruta + [vecino]
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino, nueva_ruta))
        
        return None, 0
    
    def visualizar_grafo(self, ruta=None):
        
        G = nx.Graph()
        
        for origen, destinos in self.grafo.items():
            G.add_node(origen)
            for destino, distancia in destinos.items():
                G.add_edge(origen, destino, weight=distancia)
        
        pos = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(15, 10))
        
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
        
        if ruta and len(ruta) > 1:
            ruta_aristas = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
            
            otras_aristas = [(u, v) for u, v in G.edges() if (u, v) not in ruta_aristas and (v, u) not in ruta_aristas]
            nx.draw_networkx_edges(G, pos, edgelist=otras_aristas, width=1, alpha=0.3)
            
            nx.draw_networkx_edges(G, pos, edgelist=ruta_aristas, width=3, edge_color='r')
        else:
            nx.draw_networkx_edges(G, pos, width=1)
        
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
        
        edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        
        plt.axis('off')
        plt.title("Grafo de Distancias entre Ciudades de Ecuador")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    grafo = GrafoEcuador()
    
    print("Ciudades disponibles:")
    print(grafo.listar_ciudades())
    
    origen = "Quito"
    destino = "Guayaquil"
    
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
    
    print("\nVisualizando el grafo con la ruta más corta...")
    grafo.visualizar_grafo(ruta_ucs)