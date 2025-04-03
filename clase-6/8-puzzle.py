
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

    