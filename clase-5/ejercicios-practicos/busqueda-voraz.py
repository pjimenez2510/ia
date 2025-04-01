import heapq

def greedy_bfs(graph, start, goal, heuristic):
    open_set = [(heuristic[start], start)]
    visited = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        print(current) 
        if current == goal:
            return f"Camino encontrado: {current}"
        
        visited.add(current)
        
        for neighbor in graph[current]:
            if neighbor not in visited:
                heapq.heappush(open_set, (heuristic[neighbor], neighbor))
                
    return "No se encontró un camino"

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F', 'G'],
    'D': [],
    'E': ['F',],
    'F': [],
}

heuristic = {'A': 6, 'B': 4, 'C': 5, 'D': 2, 'E': 3, 'F': 0}

print(greedy_bfs(graph, 'A', 'F', heuristic))