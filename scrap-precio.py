import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import sys
import argparse

def normalizar_texto(texto):
    """
    Normaliza el texto para facilitar las comparaciones
    """
    # Convertir a minúsculas
    texto = texto.lower()
    # Eliminar caracteres especiales y acentos
    texto = re.sub(r'[^\w\s-]', '', texto)
    # Reemplazar múltiples espacios por uno solo
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def validar_titulo(titulo, marca, modelo):
    """
    Verifica si el título contiene la marca y el modelo
    """
    # Normalizar todos los textos
    titulo_norm = normalizar_texto(titulo)
    marca_norm = normalizar_texto(marca)
    modelo_norm = normalizar_texto(modelo)
    
    # Verificar si la marca está en el título
    if marca_norm not in titulo_norm:
        return False
    
    # Preparar variaciones comunes del modelo
    modelo_sin_guion = modelo_norm.replace('-', '')
    modelo_con_espacio = modelo_norm.replace('-', ' ')
    
    # Verificar si alguna variación del modelo está en el título
    if (modelo_norm in titulo_norm or 
        modelo_sin_guion in titulo_norm or 
        modelo_con_espacio in titulo_norm):
        return True
    
    return False

def buscar_producto(marca, modelo):
    """
    Busca un producto en MercadoLibre Argentina y devuelve los primeros 5
    precios encontrados con estilo y estructura específica, validando que
    correspondan al producto deseado.
    
    Args:
        marca (str): Marca del producto
        modelo (str): Modelo del producto
    
    Returns:
        tuple: (lista_primeros_5_precios, url_busqueda)
    """
    # Construir la URL de búsqueda
    query = f"{marca} {modelo}"
    query_encoded = query.replace(' ', '%20')
    url = f"https://listado.mercadolibre.com.ar/{query_encoded}"
    
    # Configurar headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    
    try:
        # Realizar la petición HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar todos los contenedores de productos
        contenedores_productos = soup.find_all('div', class_='ui-search-result__wrapper')
        
        precios_validos = []
        
        # Para cada contenedor, extraer título y precio
        for contenedor in contenedores_productos:
            try:
                # Extraer título
                titulo_elemento = contenedor.find('h3', class_='poly-component__title-wrapper')
                if not titulo_elemento:
                    continue
                    
                titulo_link = titulo_elemento.find('a', class_='poly-component__title')
                if not titulo_link:
                    continue
                    
                titulo = titulo_link.text.strip()
                
                # Validar si el título corresponde al producto buscado
                if not validar_titulo(titulo, marca, modelo):
                    continue
                
                # Extraer precio principal (el de font-size:24px)
                bloque_precio = contenedor.find('span', class_='andes-money-amount andes-money-amount--cents-superscript', attrs={'style': lambda value: value and 'font-size:24px' in value.replace(" ", "")})
                if not bloque_precio:
                    continue
                    
                fraccion = bloque_precio.find('span', class_='andes-money-amount__fraction')
                if not fraccion:
                    continue
                    
                precio_texto = fraccion.text.strip()
                precio_limpio = int(precio_texto.replace('.', ''))
                
                precios_validos.append(precio_limpio)
                
                # Si ya tenemos 5 precios válidos, terminamos
                if len(precios_validos) >= 5:
                    break
                    
            except Exception as e:
                print(f"Error al procesar un producto: {str(e)}")
                continue
        
        # Completar la lista hasta 5 elementos si es necesario
        while len(precios_validos) < 5:
            precios_validos.append("")
            
        return precios_validos, url
        
    except Exception as e:
        print(f"Error al buscar {marca} {modelo}: {str(e)}")
        return ["Error"] * 5, url

def procesar_excel(ruta_entrada, ruta_salida):
    """
    Procesa un archivo Excel con productos y busca sus precios en MercadoLibre Argentina
    
    Args:
        ruta_entrada (str): Ruta al archivo Excel de entrada
        ruta_salida (str): Ruta donde guardar el archivo Excel de salida
    """
    try:
        # Cargar el archivo Excel conservando todas las columnas
        df = pd.read_excel(ruta_entrada)
        
        # Añadir columnas para los resultados 5 precios y URL
        df['Precio_1'] = None
        df['Precio_2'] = None
        df['Precio_3'] = None
        df['Precio_4'] = None
        df['Precio_5'] = None
        df['URL_Busqueda'] = None
        
        # Procesar cada producto
        total_productos = len(df)
        for i, row in df.iterrows():
            marca = row.iloc[0]  # Columna A (índice 0)
            modelo = row.iloc[1]  # Columna B (índice 1)
            print(f"Procesando {i+1}/{total_productos}: {marca} {modelo}")
            
            # Buscar el producto (devuelve 5 precios y URL)
            precios, url = buscar_producto(marca, modelo)
            
            # Guardar los resultados
            for j in range(5):
                df.at[i, f'Precio_{j+1}'] = precios[j] if j < len(precios) else ""
                
            df.at[i, 'URL_Busqueda'] = url
            
            # Guardar progreso parcial
            if ((i + 1) % 5 == 0) or (i == total_productos - 1):
                df.to_excel(ruta_salida, index=False)
                print(f"Progreso guardado ({i+1}/{total_productos})")
            
            # Pausa aleatoria para evitar ser bloqueado
            time.sleep(random.uniform(2, 5))
        
        print(f"Proceso completado. Resultados guardados en {ruta_salida}")
        return df
        
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return None
"""
def main():
    # Definir rutas de archivos
    ruta_entrada = input("Ingresa la ruta del archivo Excel con los productos: ")
    ruta_salida = input("Ingresa la ruta donde guardar el archivo con los resultados: ")
    
    # Verificar que las rutas sean válidas
    if not ruta_entrada.endswith(('.xlsx', '.xls')):
        ruta_entrada += '.xlsx'
    if not ruta_salida.endswith(('.xlsx', '.xls')):
        ruta_salida += '.xlsx'
    
    # Ejecutar el procesamiento
    print(f"Iniciando búsqueda de precios en MercadoLibre Argentina...")
    procesar_excel(ruta_entrada, ruta_salida)

if __name__ == "__main__":
    main()
"""

def main():
    # Verificar si hay argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Buscar precios de productos en MercadoLibre Argentina')
    parser.add_argument('--entrada', '-e', help='Ruta del archivo Excel con los productos')
    parser.add_argument('--salida', '-s', help='Ruta donde guardar el archivo con los resultados')
    args = parser.parse_args()
    
    # Si se proporcionaron argumentos, usarlos; de lo contrario, pedir al usuario
    if args.entrada and args.salida:
        ruta_entrada = args.entrada
        ruta_salida = args.salida
    else:
        ruta_entrada = input("Ingresa la ruta del archivo Excel con los productos: ")
        ruta_salida = input("Ingresa la ruta donde guardar el archivo con los resultados: ")
    
    # Verificar que las rutas sean válidas
    if not ruta_entrada.endswith(('.xlsx', '.xls')):
        ruta_entrada += '.xlsx'
    if not ruta_salida.endswith(('.xlsx', '.xls')):
        ruta_salida += '.xlsx'
    
    # Ejecutar el procesamiento
    print(f"Iniciando búsqueda de precios en MercadoLibre Argentina...")
    print(f"Archivo de entrada: {ruta_entrada}")
    print(f"Archivo de salida: {ruta_salida}")
    procesar_excel(ruta_entrada, ruta_salida)

if __name__ == "__main__":
    main()