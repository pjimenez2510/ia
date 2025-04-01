import requests
from collections import deque

# Configuración de la API
APP_ID = '1280695313341353'
APP_SECRET = '25499786ca94545d2081e13f8a0860bf'
ACCESS_TOKEN = 'fa92c306e4cd9f9afe1ba2cd57cb88ed'

def obtener_amigos_fb(user_id):
    url = f"https://graph.facebook.com/v19.0/{user_id}/friends"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,name'
    }
    response = requests.get(url, params=params)
    print(response.json())
    if response.status_code == 200:
        return [(amigo['id'], amigo['name']) for amigo in response.json()['data']]
    return []

def construir_grafo_fb(user_inicio, max_profundidad=2):
    grafo = {}
    cola = deque([(user_inicio, 0)])
    visitados = set()
    
    while cola:
        usuario_id, nivel = cola.popleft()
        if usuario_id not in visitados and nivel <= max_profundidad:
            visitados.add(usuario_id)
            amigos = obtener_amigos_fb(usuario_id)
            grafo[usuario_id] = [amigo[0] for amigo in amigos]
            
            for amigo_id, amigo_nombre in amigos:
                if amigo_id not in visitados:
                    cola.append((amigo_id, nivel + 1))
    
    return grafo

# Ejemplo de uso
grafo_facebook = construir_grafo_fb('patrickjimenez2510@gmail.com')
print(grafo_facebook)
