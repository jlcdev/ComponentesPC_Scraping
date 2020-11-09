import requests
import time
import re
import csv
import configparser
import os
from os.path  import basename
from logging.config import fileConfig
from datetime import datetime
from bs4 import BeautifulSoup

# Read config file and init vars
def initialize():
    global companyName
    global target_urls
    global baseUrl
    global csvName
    global timeOut
    global minInterval
    global categories
    global score
    global responseTimeThreshold
    global headers
    global productPage
    global calcIntervalDelay 
    
    config = configparser.ConfigParser()
    config.read('properties.config')

    companyName=config['pcBox']['companyName']
    target_urls=eval(config['pcBox']['companyUrl'])
    baseUrl=config['pcBox']['baseUrl']
    csvName=config['pcBox']['csvName']
    timeOut=int(config['pcBox']['timeOut'])
    minInterval=float(config['pcBox']['minInterval'])
    csvName=config['pcBox']['csvName']
    categories=eval(config['pcBox']['category'])
    score=config['pcBox']['score']
    responseTimeThreshold=float(config['pcBox']['responseTimeThreshold'])
    # Simulate a Chrome 86 version WEB BROWSER
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control": "no-cache",
    "dnt": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    }

    # Will keep all products within a page
    productPage = []

    # No timeDelay between requests unless Site starts performing badly.
    calcIntervalDelay=0

    # Prepare dataSet in CSV file.
    with open(csvName, 'w', newline='') as csvfile:
        fieldnames = ['timestamp','company_name','name', 'brand_name', 'category','product_number', 'price', 'score', 'image_url','image_path']
        productwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)


# send_page_request function send HTTP request and control Response times.
# Input paramters: URL, header to be sent, timeOut and interval to wait before launching request.
# Return soup object with the page.
def send_page_request(url,headers,timeOut,interval):
    if (interval>0):
        time.sleep(interval) 
    t0 = time.time()
    try:
        page=requests.get(url,headers=headers,timeout=timeOut)
    except requests.exceptions.Timeout:
        print("Page TimeOut. Sleep for 5min")
        time.sleep(300)
        page=requests.get(url,headers=headers,timeout=timeOut)
        pass
    except requests.exceptions.RequestException:
        pass

    # Response_time in seconds     
    t1 = time.time() - t0
    # t1 is time elapsed in request. Needs to be compared with predefined threshold.
    if (t1>responseTimeThreshold):
        # Update Calculated Interval Delay as 3 times response times
        calcIntervalDelay=t1*3
    else:
        # Back to 0 if response times gets better - below predefined threshold
        calcIntervalDelay=0
    
    if page:
        try:
            soupContent = BeautifulSoup(page.content,"html5lib")
        except:
            print('Error. No valid page available.')
    
    return soupContent



# Get product detail for a particular product or item.
def get_products_pageDetail(soupContent):
    productDetail={}
    productRef=soupContent.find('p', attrs={'class':'referenciasf'})
    # Remove tabs or cr from strings
    productRefText = re.sub(r"[\n\t\r]*", "", productRef.get_text())
    productNumber=(productRefText.split(":")[1]).split()[0]
    productBrandName=(productRefText.split(":")[-1])
    productDetail['productNumber']=productNumber
    productDetail['productBrandName']=productBrandName

    return productDetail


# Get main product in soup object.
def get_products_page(soupContent):
    productList=[]
    for product in soupContent.findAll('div',attrs={'class':'col-xs-6 col-sm-4 col-md-3'}):
        # Get Image Area - Extract ProductDetailUrl and ImageUrl
        productImageArea=product.find('figure', attrs={'class':'product-image-area'})
        productDetailUrl=productImageArea.find('a', attrs={'class':'product-image'}).get('href')
        imageUrl=productImageArea.find('img').get('data-src')

        # Show ProductUrl,ProductName, Price, ImageUrl, Disponibilidad
        productName=product.find('h2', attrs={'class':'product-name'}).a.get('title')
        productName = re.sub(r"[\r\n\t]*", "", productName)

        productPrice=product.find('span', attrs={'class':'product-price'}).get_text()
        productPrice = re.sub(r"[\r\n\t€]*", "", productPrice)

        # Product Available string. Not part of current DataSet.
        productDisp=product.find('div', attrs={'class':'product-disponibilidad signica'}).get_text()
        productDisp = re.sub(r"[\r\n\t]*", "", productDisp)
    
        # Get Product Page Detail - productNumber y productBrandName
        soupDetail=send_page_request(baseUrl+productDetailUrl,headers,timeOut,minInterval+calcIntervalDelay)
        productDetail=get_products_pageDetail(soupDetail)
        
        #print(productDetailUrl)
        #print(productName)
        #print(productPrice)
        #print(imageUrl)
        #print(productDisp)
        #print("P/N:",productDetail['productNumber'])
        #print("BrandName:",productDetail['productBrandName'])
        #print("------------------")
    
        productList.append({
            'timestamp':time.time(),
            'company_name':companyName,
            'name':productName,
            'brand_name':productDetail['productBrandName'],
            'category':category,
            'product_number':productDetail['productNumber'],
            'price':productPrice,
            'score':score,
            'image_url':imageUrl,
            'image_path':imageUrl
        })
    return productList

# Write products dictionary to csv file
def to_csv(products, name_csv):
    with open(name_csv, 'a', newline='') as csvfile:
        fieldnames = ['timestamp','company_name','name', 'brand_name', 'category','product_number', 'price', 'score', 'image_url','image_path']
        productwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
        for product in products:
            productwriter.writerow(product)


# Download images based on URL.
def download_images(products):
    if len(products) < 1:
        return products
    url_list = list(map(lambda x: x['image_url'], products))
    path = './images/' + products[0]['category'] + '/'
    try:
        os.makedirs(path)
    except:
        print('path exist')
    for i, url in enumerate(url_list):
        with open(path+basename(url), "wb") as f:
            f.write(requests.get(url).content)
        products[i]['image_path'] = path+basename(url)
        time.sleep(0.5)
    return products


# Check pagination in Page.
# If pagination tag is found return list of subpages. If not, return False.
def get_pagination(soupContent):
    pagination=soupContent.find('ul',attrs={'class':'pagination'})
    subpages=[]
    initial=1
    if pagination:
        for subpage in pagination.findAll('a',attrs={'class':''}):
            #if it is a subpage add to list.
            if subpage.get_text():
                subpages.append(subpage['href'])
                print(subpage['href'])
                print(int(subpage.get_text()))
                i=initial
                initial +=1
                while i<int(subpage.get_text()):
                    subpages.append(subpage['href'].replace(subpage.get_text(),str(i)))
                    i += 1
        return subpages
    return False



# Main program
#Read config file and initialize vars
if __name__ == "__main__":
    initialize()
    #Current Time
    dateTimeObj = datetime.now()
    timeStamp = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
    print('Start Timestamp : ', timeStamp)

    # While there is a Category or Target Url in List that needs to be processed
    numberCategory=0
    while numberCategory < len(target_urls):
        target_url=target_urls[numberCategory]
        category=categories[numberCategory]
        print("Requesting Target URL: ",target_url)
        print("Category: ",category)
    
        soup=send_page_request(target_url,headers,timeOut,minInterval++calcIntervalDelay)
        if get_pagination(soup):
            for subpages in get_pagination(soup):
                soup=send_page_request(subpages,headers,timeOut,minInterval+calcIntervalDelay)
                productPage=get_products_page(soup)
                #productPage.append(get_products_page(soup))
                # Need to download images
                download_images(productPage)
                to_csv(productPage,csvName)
        else:
            # No need to iterate in sub-pages - No pagination found
            productPage=get_products_page(soup)
            # Need to download images
            download_images(productPage)
            to_csv(productPage,csvName)
        
        numberCategory += 1

    #Current TimeStamp
    dateTimeObj = datetime.now()
    timeStamp = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
    print('End Timestamp : ', timeStamp)
