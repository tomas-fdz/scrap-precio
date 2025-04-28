# Buscador de Precios en MercadoLibre Argentina

Este proyecto es un **script en Python** que busca los precios de productos en MercadoLibre Argentina a partir de una lista de marcas y modelos en un archivo Excel.

El script hace scraping de los resultados, valida que los títulos coincidan con la marca y modelo indicados, y guarda los primeros 5 precios encontrados junto con la URL de búsqueda en un nuevo archivo Excel.

## Características

- 📄 Procesa archivos Excel (.xlsx, .xls).
- 🔎 Busca automáticamente los productos en MercadoLibre.
- ✅ Valida marca y modelo en los títulos para mayor precisión.
- 💰 Guarda los 5 primeros precios encontrados.
- 🌐 Guarda también la URL de búsqueda realizada.
- 🧹 Normaliza texto para mejorar coincidencias.
- 🛡️ Maneja errores y pausas aleatorias para evitar bloqueos.

## Requisitos

- Python 3.7 o superior
- Librerías de Python:
  - pandas
  - requests
  - beautifulsoup4
  - openpyxl (para escribir Excel)

Puedes instalar las dependencias con:

```bash
pip install -r requirements.txt


Formato del Excel de Entrada

El archivo de entrada debe tener:

    Columna A: Marca

    Columna B: Modelo

Ejemplo:
Marca	Modelo
Samsung	Galaxy A54
Apple	iPhone 13
Ejemplo de salida

El archivo de salida tendrá las siguientes columnas adicionales:

    Precio_1

    Precio_2

    Precio_3

    Precio_4

    Precio_5

    URL_Busqueda

Cada fila representará un producto con los precios encontrados.
Notas

    El scraping puede fallar si MercadoLibre cambia su estructura.

    Se realizan pausas aleatorias entre búsquedas para simular un comportamiento humano.

Licencia

Este proyecto es de uso libre para fines educativos y personales.
Autor: [Tu Nombre Aquí]