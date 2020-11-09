from bs4 import BeautifulSoup
from selenium import webdriver
from os.path  import basename
import time
import csv
import requests
import os
import glob
import pandas as pd
import argparse

# Preparación del navegador y aceptación de politica de cookies
def prepare_environtment(driver, url):
    driver.implicitly_wait(30)
    driver.get(url)
    time.sleep(2)
    driver.find_elements_by_class_name("accept-cookie")[0].click()

# Permite cambiar la URL del navegador y obtener una nueva pagina para parsear
def change_url(driver, url):
    driver.get(url)
    time.sleep(args.sleep_time_url)
    return BeautifulSoup(driver.page_source,"html5lib")

# Dado una pagina de producto -> obtener todas las características que consideramos relevantes
def get_product_detail_info(page):
    product = {}
    product['timestamp'] = time.time()
    product['company_name'] = 'pccomponentes'
    product['name'] = page.find("div", class_="ficha-producto__encabezado").find("div", class_="articulo").h1.strong.text
    try:
        product['brand_name'] = page.find("div", class_="ficha-producto__datos-de-compra").a.text
    except:
        product['brand_name'] = 'undefined'
    product['category'] = page.find("div", class_="navegacion-secundaria__migas-de-pan").findAll("a")[-1].text
    product['product_number'] = page.find("span", id="codigo-articulo-pc").parent.find("span").text
    product['price'] = float(page.find("div", class_="ficha-producto__encabezado").find("div", class_="priceBlock")['data-baseprice'])
    try:
        product['score'] = float(page.find("div", id="ficha-producto-opinones").find("div", class_="percentage").text)
    except:
        product['score'] = 0
    try:
        product['image_url'] = 'https:' + page.find("img", class_="pc-com-zoom")['src']
    except:
        product['image_url'] = 'undefined'
    try:
        product['reviews'] = int(page.find("div", class_="ficha-producto__encabezado").find("span", class_="acciones").a.text.replace(' Opiniones', '').replace('\n',''))
    except:
        product['reviews'] = 0
    return product

# Permite recorrer todas las url de productos y ir obteniendo sus características
def obtain_all_products(driver, urls):
    products = []
    for i, url in enumerate(urls):
        page = change_url(driver, url)
        product = get_product_detail_info(page)
        products.append(product)
        if i % 50 == 0:
            print('Products downloaded: ' + str(i))
    return products

# Filtrar los productos por las categorias del dataset
def filter_products_by_categories(products):
    products_filtered = []
    selected_categories = ['Procesadores', 'Discos Duros', 'Fuentes Alimentación', 'Memoria RAM', 'Placas Base', 'Tarjetas de Sonido', 'Tarjetas Gráficas', 'Torres']
    for product in products:
        if product['category'] in selected_categories:
            products_filtered.append(product)
    return products_filtered

# Función para obtener 1 imagen
def download_image(category, image_url):
    try:
        os.makedirs(os.path.join('.','images', category))
    except:
        pass
    file_path = os.path.join('.','images', category, basename(image_url))
    with open(file_path, "wb") as f:
        f.write(requests.get(image_url).content)
    return file_path

# Permite recorrer todas las url de los productos e ir obteniendo las imagenes
def download_product_images(products):
    sleep_time = 0.25
    sleep_time_inc = 0.1
    sleep_time_max = sleep_time * 20
    count_success = 0
    for i, product in enumerate(products):
        try:
            product['image_url_dataset'] = download_image(product['category'], product['image_url'])
            count_success += 1
            if sleep_time > 0.25 and count_success > 10:
                sleep_time -= sleep_time_inc
        except:
            product['image_url_dataset'] = product['image_url']
            sleep_time += sleep_time_inc
            count_success = 0
            if sleep_time > sleep_time_max:
                sleep_time = sleep_time_max
        if i % 50 == 0:
            print('Images downloaded: ' + str(i))
        time.sleep(sleep_time)
    return products

# Dada una lista de productos con sus caracteristicas -> genera un nuevo documento CSV con todos los productos
def to_csv(products, name_csv):
    with open(name_csv, 'w', newline='') as csvfile:
        fieldnames = ['timestamp','company_name','name', 'brand_name', 'category','product_number', 'price', 'score', 'image_url','image_url_dataset','reviews']
        productwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
        productwriter.writeheader()
        for product in products:
            productwriter.writerow(product)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-stu', '--sleep_time_url', nargs='?', const=0.25, type=float, help="Sets the process timeout when the URL changes.")
    parser.add_argument('-nsc', '--num_scrap_chunk', nargs='?', const=500, type=int, help="Size of chunks to work.")
    parser.add_argument('-pi', '--products_init', nargs='?', const=0, type=int, help="Starting point to start scraping products.")
    parser.add_argument('-nd', '--name_dataset', nargs='?', const='dataset_pccomponentes.csv', type=str, help="Name for csv file.")
    args = parser.parse_args()

    if args.num_scrap_chunk == None: args.num_scrap_chunk = 500
    if args.products_init == None: args.products_init = 0
    if args.sleep_time_url == None: args.sleep_time_url = 0.25
    if args.name_dataset == None: args.name_dataset = 'dataset_pccomponentes.csv'

    # Preparación del entorno para poder recorrer la tienda
    print('Preparing environment to launch requests.')
    driver = webdriver.Chrome()
    prepare_environtment(driver, 'https://www.pccomponentes.com/')

    # Obtención de todas las url de productos desde el sitemap
    print('Get components sitemap from PcComponentes.')
    sitemap_products = change_url(driver, 'https://www.pccomponentes.com/sitemap_articles_components.xml')
    urls_clean = list(map(lambda x: x.text, sitemap_products.findAll("loc",text=True)))

    items_in_shop = len(urls_clean)

    for i in range(args.products_init,items_in_shop, args.num_scrap_chunk):
        j = i+args.num_scrap_chunk
        print('Downloading chunk with urls between ' + str(i) + ' and ' + str(j))
        # Obtención de todas las características de los productos de la tienda por chunks
        products_chunk = obtain_all_products(driver, urls_clean[i:j])
        # Seleccionar solo aquellos productos que interesan para el dataset
        products_chunk_filtered = filter_products_by_categories(products_chunk)
        # Descargar la imagen principal de cada producto de la tienda del chunk
        products_chunk_images = download_product_images(products_chunk_filtered)
        # Generación parcial del dataset
        to_csv(products_chunk_images, 'pccomponentes_products_' + str(i) + '_' + str(j) + '.csv')

    print('Joining all the partial files into a single one.')
    os.chdir("./")
    all_csv_filenames = [i for i in glob.glob('*.{}'.format('csv'))]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_csv_filenames])
    combined_csv.to_csv(args.name_dataset, index=False, encoding='utf-8')
