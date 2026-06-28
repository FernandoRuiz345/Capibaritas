import requests
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd

class amazom:
    def __init__(self, producto, idioma="ES", max_resultados=500):
        self.producto = producto
        self.idioma = idioma
        self.max_resultados = max_resultados
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        self.resultados = []
    
    # Genera el enlace de búsqueda con página específica
    def link(self, pagina=1):
        return f"https://www.amazon.com/s?k={self.producto.replace(' ', '+')}&language={self.idioma}&page={pagina}"
    
    # Realiza el scraping de los productos en Amazon en múltiples páginas
    def realizar_scraping(self):
        self.resultados = []
        pagina = 1
        
        while len(self.resultados) < self.max_resultados:
            url = self.link(pagina)
            print(f"Scraping página {pagina}...")
            
            try:
                respuesta = requests.get(url, headers=self.headers)
                respuesta.raise_for_status()  # Verifica si la respuesta es exitosa
                soup = BeautifulSoup(respuesta.text, "html.parser")
                productos = soup.select("div[data-component-type='s-search-result']")
                
                # Si no hay productos en esta página, terminamos
                if not productos:
                    print(f"No se encontraron más productos en la página {pagina}")
                    break
                
                # Procesar productos de la página actual
                for item in productos:
                    if len(self.resultados) >= self.max_resultados:
                        break
                    
                    id_producto = item.get("data-asin")
                    
                    # Obtener precio
                    precio_element = item.select_one("span.a-price span.a-offscreen")
                    precio = precio_element.text.strip() if precio_element else None
                    
                    # Obtener estrellas
                    estrellas_element = item.select_one("span.a-icon-alt")
                    estrellas = estrellas_element.text.strip() if estrellas_element else None
                    
                    # Link del producto
                    link = f"https://www.amazon.com/-/es/dp/{id_producto}/" if id_producto else None
                    
                    self.resultados.append({
                        'id': id_producto,
                        'precio': precio,
                        'estrellas': estrellas,
                        'link': link
                    })
                
                print(f"Productos obtenidos hasta ahora: {len(self.resultados)}")
                
                # Esperar un poco entre peticiones para no sobrecargar el servidor
                time.sleep(2)
                
                pagina += 1
                
            except Exception as e:
                print(f"Error en la página {pagina}: {e}")
                break
        
        print(f"Scraping completado. Total de productos: {len(self.resultados)}")
        return self.resultados
    
    # Visualiza los resultados del scraping en una tabla de texto
    def datos(self):
        try:
            if not self.resultados:
                self.realizar_scraping()
            return pd.DataFrame(self.resultados)
        except ImportError:
            print("Pandas no está instalado. Usa el método crear_tabla() en su lugar.")
            return None
    
    # Guarda los resultados del scraping en un archivo CSV
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
    
    # Mostrar estadísticas de los resultados
    def estadisticas(self):
        if not self.resultados:
            self.realizar_scraping()
        
        df = pd.DataFrame(self.resultados)
        print(f"\n--- ESTADÍSTICAS ---")
        print(f"Total de productos: {len(df)}")
        print(f"Productos con precio: {df['precio'].notna().sum()}")
        print(f"Productos con estrellas: {df['estrellas'].notna().sum()}")
        print(f"Productos con ID: {df['id'].notna().sum()}")
        
        if df['precio'].notna().sum() > 0:
            precios_limpios = df['precio'].dropna().str.replace('$', '').str.replace(',', '')
            precios_numericos = pd.to_numeric(precios_limpios, errors='coerce')
            print(f"Precio mínimo: ${precios_numericos.min():.2f}")
            print(f"Precio máximo: ${precios_numericos.max():.2f}")
            print(f"Precio promedio: ${precios_numericos.mean():.2f}")

# Ejemplo de uso
if __name__ == "__main__":
    # Para obtener 100 productos
    print("=== Scraping de Amazon - 100 productos ===")
    producto = "parlantes bluetooth"
    
    # Crear instancia con límite de 100 productos
    amazon_scraper = amazom(producto, max_resultados=100)
    
    # Realizar scraping
    resultados = amazon_scraper.realizar_scraping()
    
    # Mostrar primeros 10 productos
    print("\n=== PRIMEROS 10 PRODUCTOS ===")
    df = amazon_scraper.datos()
    if df is not None:
        print(df.head(10))
    
    
    # Guardar en CSV
    amazon_scraper.guardar_csv()
    
