
import heapq

def greedy_best_first_search(graph, start, goal, h):
    open_set = [(h(start), start)]
    visited = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            return current
        
        visited.add(current)
        
        for neighbor in graph[current]:
            if neighbor not in visited:
                heapq.heappush(open_set, (h(neighbor), neighbor))
    
    return None
    


    