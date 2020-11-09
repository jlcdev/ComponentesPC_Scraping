import csv
import os
import argparse

def join_datasets(path1, path2, path3):
    os.chdir("./")
    fieldnames = ['timestamp','company_name','name', 'brand_name', 'category','product_number', 'price', 'score', 'image_url','image_url_dataset','reviews']
    with open(path1, mode='r', encoding='utf-8') as f1:
        with open(path2, mode='r', encoding='utf-8') as f2:
            products_f1 = [dict(zip(fieldnames,p)) for i,p in enumerate(csv.reader(f1)) if i!=0]
            products_f2 = [dict(zip(fieldnames,p)) for i,p in enumerate(csv.reader(f2)) if i!=0]
            products = products_f1 + products_f2
            with open(path3, 'w', newline='') as outfile:
                productwriter = csv.DictWriter(outfile, delimiter=',', fieldnames=fieldnames)
                productwriter.writeheader()
                for product in products:
                    productwriter.writerow(product)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p1', '--path1', nargs='?', const='./dataset_pccomponentes.csv', type=str, help="Path to pccomponentes csv.")
    parser.add_argument('-p2', '--path2', nargs='?', const='./dataset_pcbox.csv', type=str, help="Path to pcbox csv.")
    parser.add_argument('-p3', '--path3', nargs='?', const='./dataset.csv', type=str, help="Path for output csv.")
    args = parser.parse_args()

    if args.path1 == None: args.path1 = './dataset_pccomponentes.csv'
    if args.path2 == None: args.path2 = './dataset_pcbox.csv'
    if args.path3 == None: args.path3 = './dataset.csv'

    join_datasets(args.path1, args.path2, args.path3)