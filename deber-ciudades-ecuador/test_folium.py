"""
Script de prueba para verificar la funcionalidad de Folium
"""
try:
    import folium
    from folium.plugins import MarkerCluster
    print("Folium importado correctamente")
    
    # Crear un mapa de prueba
    mapa = folium.Map(location=[-1.83, -78.18], zoom_start=7)
    
    # Agregar un marcador
    folium.Marker(
        location=[-0.1807, -78.4678],
        popup="Quito",
        tooltip="Quito",
        icon=folium.Icon(color='red')
    ).add_to(mapa)
    
    # Guardar el mapa
    ruta_archivo = "test_folium_map.html"
    print(f"Guardando mapa en {ruta_archivo}...")
    mapa.save(ruta_archivo)
    print(f"Mapa guardado como {ruta_archivo}")
    
    # Abrir el mapa en el navegador
    import webbrowser
    import os
    ruta_completa = os.path.realpath(ruta_archivo)
    print(f"Intentando abrir el navegador con: file://{ruta_completa}")
    webbrowser.open('file://' + ruta_completa)
    print("Navegador abierto con el mapa")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 