from copy import deepcopy
import heapq

estado_inicial = [
    [1, 2, 3],
    [4, 0, 5],
    [7, 8, 6]
]

estado_objetivo = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

def heuristica_manhattan(estado):
    '''Calcula la distancia de Manhattan entre el estado actual y el estado objetivo'''
    distancia = 0
    for i in range(3):
        for j in range(3):
            valor = estado[i][j]
            if valor != 0:
                fila_objetivo = (valor - 1) // 3
                col_objetivo = (valor - 1) % 3
                distancia += abs(i - fila_objetivo) + abs(j - col_objetivo)
    return distancia

def obtener_sucesores(estado):
    """Genera todos los estados sucesores válidos"""
    sucesores = []
    
    # Encontrar la posición del 0 (espacio vacío)
    for i in range(3):
        for j in range(3):
            if estado[i][j] == 0:
                fila_vacia, col_vacia = i, j
                break
    
    # Movimientos posibles: arriba, abajo, izquierda, derecha
    movimientos = [(-1, 0, "Arriba"), (1, 0, "Abajo"),
                  (0, -1, "Izquierda"), (0, 1, "Derecha")]
    
    for df, dc, accion in movimientos:
        nueva_fila = fila_vacia + df
        nueva_col = col_vacia + dc
        
        if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:
            # Crea una copia profunda del estado
            nuevo_estado = deepcopy(estado)
            # Realiza el movimiento
            nuevo_estado[fila_vacia][col_vacia], \
            nuevo_estado[nueva_fila][nueva_col] = \
            nuevo_estado[nueva_fila][nueva_col], \
            nuevo_estado[fila_vacia][col_vacia]
            
            sucesores.append((accion, nuevo_estado))
    
    return sucesores

def a_star(estado_inicial, estado_objetivo):
    """Implementación del algoritmo A* para el 8-puzzle"""
    frontera = []
    heapq.heappush(frontera, 
                  (0 + heuristica_manhattan(estado_inicial),
                   estado_inicial, []))
    visitados = set()
    
    while frontera:
        _, estado_actual, camino = heapq.heappop(frontera)
        
        # Convertir el estado a una tupla para poder
        # almacenarlo en el conjunto
        estado_actual_tupla = tuple(tuple(fila) for fila in estado_actual)
        
        if estado_actual_tupla not in visitados:
            visitados.add(estado_actual_tupla)
            
            if estado_actual == estado_objetivo:
                return camino
            
            for accion, sucesor in obtener_sucesores(estado_actual):
                nuevo_costo = len(camino) + 1
                heapq.heappush(frontera,
                              (nuevo_costo + heuristica_manhattan(sucesor),
                               sucesor,
                               camino + [accion]))
    
    return None             





# Resolución del puzzle
solucion = a_star(estado_inicial, estado_objetivo)

if solucion:
    print("Solución encontrada. Pasos:")
    for i, accion in enumerate(solucion, 1):
        print(f"Paso {i}: Mover {accion}")
    print("\nEstado final alcanzado:")
    #dibujar_puzzle(estado_objetivo)
else:
    print("No se encontró solución para este estado inicial.")