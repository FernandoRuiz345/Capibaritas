

# Verificar si la página de Amazon es accesible

import requests
url = "https://www.amazon.com"
#facilita la solicitud para que parezca que proviene de un navegador 
#web real y no de un script automatizado, lo que ayuda a evitar bloqueos 
# o restricciones por parte del servidor web.
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

# Seleecion de un producto de Amazon y extracción de datos.

import requests
from bs4 import BeautifulSoup
import csv

class amazom:
    def __init__(self, producto, idioma="ES"):
        self.producto = producto
        self.idioma = idioma
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        self.resultados = []
        
    def link(self):
        return f"https://www.amazon.com/s?k={self.producto.replace(' ', '+')}&language={self.idioma}"
    
    def realizar_scraping(self):
        url = self.link()
        respuesta = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(respuesta.text, "html.parser")
        productos = soup.select("div[data-component-type='s-search-result']")
        
        self.resultados = []
        for item in productos:
            id_producto = item.get("data-asin")
            
            # Obtener precio
            precio_element = item.select_one("span.a-price span.a-offscreen")
            precio = precio_element.text.strip() if precio_element else None
            
            # Obtener estrellas
            estrellas_element = item.select_one("span.a-icon-alt")
            estrellas = estrellas_element.text.strip() if estrellas_element else None
            
            #link
            link_element = item.select_one("a.a-link-normal")
            link = f"https://www.amazon.com/-/es/dp/{id_producto}/" if id_producto else None

            self.resultados.append({
                'id': id_producto,
                'precio': precio,
                'estrellas': estrellas,
                'link': link
            })
        
        return self.resultados
    
    def datos(self):
        try:
            import pandas as pd
            if not self.resultados:
                self.realizar_scraping()
            return pd.DataFrame(self.resultados)
        except ImportError:
            print("Pandas no está instalado. Usa el método crear_tabla() en su lugar.")
            return None
        
    def guardar_csv(self, nombre_archivo=None):
        if not nombre_archivo:
            nombre_archivo = f"{self.producto.replace(' ', '_')}_amazon.csv"
        
        if not self.resultados:
            print("No hay datos para guardar. Realizando scraping...")
            self.realizar_scraping()
        
        try:
            with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
                campos = self.resultados[0].keys()
                writer = csv.DictWriter(archivo, fieldnames=campos)
                writer.writeheader()
                writer.writerows(self.resultados)
            print(f"Datos guardados en: {nombre_archivo}")
        except Exception as e:
            print(f"Error guardando CSV: {e}")
    
print("Resultados del scraping:")

producto = "parlantes bluetooth"
print(amazom(producto).datos())

# CREACION DEL ARCHIVO CSV CON LOS DATOS DEL PRODUCTO
amazom(producto).guardar_csv()






    
    

























