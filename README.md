# Componentes de PC - Práctica de webscraping

## Descripción
Este proyecto se ha realizado como un trabajo práctico WEB SCRAPING en el ámbito de la asignatura **Tipología y ciclo de vida de los datos** que forma parte del Máster en Ciencia de Datos de la **Universitat Oberta de Catalunya (UOC)** en España.

## Miembros del equipo

* Javier López Calderón
* José María Cano Hernández - https://github.com/jcanoh/ComponentesPC_Scraping

## Contenido del repositorio

* PDF/TCVD_PRAC1.pdf - Es el fichero **pdf** que contiene la parte documental del proyecto.
* dataSet/dataset.csv - Es el fichero **csv** que contiene el dataset obtenido durante la realización de la práctica.
* src-Notebook/*.ipynb - Son los ficheros en formato **python notebook** para realizar las tareas de scraping.
* src-Python/*.py - Son los ficheros en formato **python** para realizar las tareas de scraping.

## Cómo utilizar los ficheros de este proyecto

### Para realizar webscraping sobre PcComponentes:
#### Ejemplo de uso normal
```
python src-Python/scrap_pcc.py --sleep_time_url 0.25  --num_scrap_chunk 500 --products_init 0  --name_dataset dataset_pccomponentes.csv
```
*** NOTA: los argumentos se emplean para poder definir cómo se realiza el scraping, permitiendo minimizar el impacto sobre la tienda y, en caso de fallo, poder definir y reanudar desde el punto donde se ha quedado. ***
#### Ejemplo de uso compacto
```
python src-Python/scrap_pcc.py -stu 0.25  -nsc 500 -pi 0  -nd dataset_pccomponentes.csv
```

### Para realizar webscraping sobre PcBox:
#### Ejemplo de uso normal
```
python src-Python/webScrapingPcBox.py
```
*** NOTA: Toda la configuración se realiza mediante el fichero **properties.config**. ***

## Más información disponible en la Wiki del proyecto.
