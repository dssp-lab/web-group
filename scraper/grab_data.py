import os
import json
import sys
import requests
from scholarly.scholarly import scholarly
from habanero import Crossref
import feedparser
from lxml import html
import pandas as pd
import re

sys.path.append('scraper')
from mail_utils import send_email

# 📌 Carpeta donde se guardarán los JSON
DATA_FOLDER = "./data"

# 📌 Crear la carpeta si no existe
os.makedirs(DATA_FOLDER, exist_ok=True)


#Publications
cr = Crossref() 

def obtain_pubs_id(author_id):
    # Obtain profile by id
    author = scholarly.search_author_id(author_id)
    author = scholarly.fill(author)
    
    # Obtain publications
    publications = author.get('publications', [])
    return publications

# 📌 Authors dictionary (Name -> Google Scholar ID)
AUTHORS = {
    "Antonio G. Marques": "d05JMMkAAAAJ",
    "Samuel Rey": "fUy5BM4AAAAJ",
    "Andrei Buciulea":"66U0mA0AAAAJ",
    "Sergio Rozada": "MFQxsqYAAAAJ",
    "Víctor Tenorio": "4CWKOUoAAAAJ",
    "Oscar Escudero": "9fhAzz8AAAAJ",
    "Fernando Real": "O0ZSUNgAAAAJ"
}

# 🎯 Year range
START_YEAR = 2020
END_YEAR = 2030

# 📦 Dictionary to store the results
results = {name: [] for name in AUTHORS}

# 📝 JSON file
json_filename = os.path.join(DATA_FOLDER, "publications.json")

# 📥 Read existing file
if os.path.exists(json_filename):
    with open(json_filename, "r", encoding="utf-8") as json_file:
        prev_publications = json.load(json_file)
else:
    prev_publications = {}

# 🔄 Iterate over every author
for name, author_id in AUTHORS.items():
    publications = obtain_pubs_id(author_id)

    for pub in publications:
        year = pub.get('bib', {}).get('pub_year', '')

        # 🏷️ Date filter
        if year and START_YEAR <= int(year) <= END_YEAR:
            title = pub.get('bib', {}).get('title', 'N/A')
            authors = pub.get('bib', {}).get('authors', 'N/A')
            journal = pub.get('bib', {}).get('venue', 'N/A')  
            link = ""

            # 📌 Buscar en arXiv si el journal comienza con "arXiv"
            if journal.startswith("arXiv"):
                try:
                    title_query = '+'.join(title.split())
                    search_url = f"http://export.arxiv.org/api/query?search_query=ti:{title_query}&max_results=1"
                    response = requests.get(search_url, timeout=5)
                    feed = feedparser.parse(response.text)
                    link = feed.entries[0].id if feed.entries else ""
                except requests.exceptions.RequestException as e:
                    print(f"Error en arXiv para {title}: {e}")

            # 📌 Buscar en CrossRef
            doi = ""
            try:
                search_doi = cr.works(query=title)

                # Verificar si hay resultados
                if search_doi and "message" in search_doi and "items" in search_doi["message"] and search_doi["message"]["items"]:
                    paper = search_doi["message"]["items"][0]
                    found_title = paper.get("title", ["Unavailable"])[0]

                    # Comparar títulos y asignar DOI si coinciden
                    if title.lower() == found_title.lower():
                        doi = paper.get("DOI", "")
                        link = f"https://doi.org/{doi}" if doi else link
            except Exception as e:
                print(f"Error en CrossRef para {title}: {e}")

            # 📌 Si no hay DOI o link, obtener el de Google Scholar
            pub_id = pub.get('author_pub_id', None)
            if pub_id and not link:
                link = f"https://scholar.google.com/citations?view_op=view_citation&hl=es&citation_for_view={pub_id}"

            # 📌 Recuperar "Delete" de publicaciones previas
            delete_value = 0
            if name in prev_publications:
                for old_pub in prev_publications[name]:
                    if old_pub.get("Title") == title:
                        delete_value = old_pub.get("Delete", 0)
                        break

            # 📌 Guardar en los resultados
            results[name].append({
                "Title": title,
                "Authors": authors,
                "Journal": journal,
                "Year": int(year) if year.isdigit() else 0,
                "DOI": doi,
                "Link": link,
                "GitHub": "",
                "ArXiv": "",
                "Multimedia": "",
                "Delete": delete_value
            })


# 🔄 Sort publications
for name, publications in results.items():
    results[name] = sorted(publications, key=lambda x: x["Year"], reverse=True)

# 📝 Save results
#json_filename = os.path.join(DATA_FOLDER, "publications.json")
#with open(json_filename, "w", encoding="utf-8") as json_file:
#    json.dump(results, json_file, indent=4, ensure_ascii=False)

# 🧹 Unique pubs
unique_publications = {}
for author, publications in results.items():
    for pub in publications:
        title = pub['Title']
        if title not in unique_publications:
            unique_publications[title] = pub

# 🔄 Sort
sorted_unique_publications = sorted(
    unique_publications.values(), 
    key=lambda x: x["Year"], 
    reverse=True
)

# 📝 Save unique publications
unique_json_filename = os.path.join(DATA_FOLDER, "unique_publications.json")
with open(unique_json_filename, "w", encoding="utf-8") as json_file:
    json.dump(sorted_unique_publications, json_file, indent=4, ensure_ascii=False)


#Projects


# 📌 URLs de los perfiles
urls = [
    "https://gestion2.urjc.es/pdi/ver/antonio.garcia.marques",
    "https://gestion2.urjc.es/pdi/ver/samuel.rey.escudero",
    "https://gestion2.urjc.es/pdi/ver/andrei.buciulea",
    "https://gestion2.urjc.es/pdi/ver/victor.tenorio"
]

# 📌 Diccionario de resultados por autor
results = {url.split('/')[-1]: [] for url in urls}

# 📌 Nombre del archivo JSON
json_filename = os.path.join(DATA_FOLDER, "projects.json")
# 📥 Leer JSON previo si existe
if os.path.exists(json_filename):
    with open(json_filename, "r", encoding="utf-8") as json_file:
        prev_projects = json.load(json_file)
else:
    prev_projects = {}

# 📅 Intervalo de años de finalización que deseas filtrar
START_YEAR = 2020
END_YEAR = 2030

# 🔄 Iterar sobre cada URL
for url in urls:
    author = url.split('/')[-1]
    i = 1

    # Enviar solicitud GET a la URL
    response = requests.get(url)
    tree = html.fromstring(response.content)

    while True:
        try:
            # 📌 Construir el XPath del bloque actual
            base_xpath = f'//*[@id="accordion1"]/div[{i}]'

            # Extraer el contenido del div
            div_content = tree.xpath(base_xpath)
            if not div_content:
                break  # No hay más proyectos, salir del bucle

            # 📌 Extraer título
            title_xpath = base_xpath + '/div[1]/h4/a'
            title = tree.xpath(title_xpath)[0].text_content().strip()

            # 📌 Extraer detalles del proyecto
            detail_xpath = base_xpath + '/div[2]/div/p'
            detail_content = tree.xpath(detail_xpath)[0].text_content().strip()

            # 📌 Extraer investigadores
            detail_xpath_res = base_xpath + '/div[2]/div/p[2]'
            detail_content_res = tree.xpath(detail_xpath_res)[0].text_content().strip()

            detail_xpath_res = base_xpath + '/div[2]/div/ul'
            items = tree.xpath(detail_xpath_res)[0]
            names_researchers = [item.text_content().strip() for item in items]

            # 📌 Extraer información clave: años, financiación, etc.
            matches = re.findall(r'([^:]+):\s*([^:]*?)(?=\s{2,}|$)', detail_content)
            parsed_dict = {key.strip(): value.strip() for key, value in matches}

            # 📌 Obtener año de finalización
            end_year_str = parsed_dict.get("Año de finalización", "")
            end_year = int(end_year_str) if end_year_str.isdigit() else None

            # 📌 Verificar si está en el rango de años permitidos
            if end_year and not (START_YEAR <= end_year <= END_YEAR):
                i += 1  # Pasar al siguiente proyecto
                continue  # Saltar este proyecto

            # 📌 Verificar si ya existe en el JSON anterior para mantener la marca "Delete"
            delete_value = 0
            if author in prev_projects:
                for old_project in prev_projects[author]:
                    if old_project.get("Title") == title:
                        delete_value = old_project.get("Delete", 0)
                        break

            # 📌 Crear diccionario con la información del proyecto
            data_dict = {
                "Title": title,
                **parsed_dict,
                detail_content_res: names_researchers,
                "Delete": delete_value
            }

            # 📌 Agregar al JSON de resultados
            results[author].append(data_dict)



            # 📌 Incrementar índice para el siguiente proyecto
            i += 1

        except Exception as e:
            print(f"⚠️ Error en {author}, proyecto {i}: {e}")
            break  # Salir del bucle si hay error

# 📌 Guardar los proyectos en `projects.json`
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

# 🧹 **Generar JSON con proyectos únicos**
unique_projects = {}
for author, projects in results.items():
    for project in projects:
        title = project["Title"]
        if title not in unique_projects:
            unique_projects[title] = project  # Evita duplicados

# 🔄 **Ordenar los proyectos únicos por año de finalización**
sorted_unique_projects = sorted(
    unique_projects.values(),
    key=lambda x: int(x.get("Año de finalización", 0)) if x.get("Año de finalización", "").isdigit() else 0,
    reverse=True
)

# 📌 Guardar los proyectos únicos en `unique_projects.json`
unique_json_filename = os.path.join(DATA_FOLDER, "unique_projects.json")
with open(unique_json_filename, "w", encoding="utf-8") as json_file:
    json.dump(sorted_unique_projects, json_file, indent=4, ensure_ascii=False)


send_email("victor.030995@gmail.com", "Test email", "Test email")
