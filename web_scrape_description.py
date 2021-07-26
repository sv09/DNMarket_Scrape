## import required libraries
import pandas as pd
import csv
import requests
import sys
import webbrowser
from bs4 import BeautifulSoup
import time
import os
from collections import Counter

## base path
path = ""       #add the project base path here

## read the original datatset
original_data_filename = ""     #add the original data file(in .csv format) which is present at the path provided above
original_dataset_path = os.path.join(path, original_data_filename)
data_df = pd.read_csv(original_dataset_path, error_bad_lines=False)


## clean data
strip_df = data_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
clean_df = strip_df.replace('Undeclared', '')
clean_df = clean_df.replace('unknown', '')


## Create a new csv file to save the output
csvFile = "webScrape_product_description.csv"
csvPath = os.path.join(path, csvFile)
output_file = open(csvPath, 'a')
csv_writer = csv.writer(output_file)
csv_writer.writerow(['Product', 'Web_Description'])


## function to scrape web (google.com) for extracting the description for each product
def scrape_description(product):
    tot_tries = 11
    delay = 10800
    hrs = delay/3600
    prod = product.replace("-", " ")
    itr=1
    while tot_tries >= 1:
        res = requests.get('https://google.com/search?q='+''.join(prod))
        if res.status_code == 200:
            tot_tries = 0
        elif res.status_code == 429:
            if tot_tries == 1:
                res.raise_for_status()       
            tot_tries -= 1
            print("HTTPError: 429 - Too Many Requests; Will retry in %d hours..."% (hrs)) 
            time.sleep(delay)
            itr += 1

    soup = BeautifulSoup(res.text, 'html.parser')
    flag = False
    i=0
    j=0
    terms = []
    divs = soup.select('div')
    for d in divs:
        if d.get_text() == 'All results':
            flag = True
            i+=1
        else:
            i+=1
        if flag and i<len(divs)-1:
            if j > 20:
                break
            i+=1
            j+=1
            for term in divs[i].get_text().split():
                if 'Missing' in term:
                    break
                terms.append(term)
    return terms


## starter code
scrape_descr_df = pd.read_csv(csvPath)
for i in range(len(clean_df)):
    product = clean_df.iloc[i]['Product']
    check = scrape_descr_df.apply(lambda x: product in x.values, axis=1).any()  ## if a product name has already been checked for, skip that product
    if not check:
        time.sleep(1)   # delay of 1 second before each web request
        terms = scrape_description(product)
        prod_description = ''
        for word in terms:
            if ".com" in word or "www." in word:
                continue
            else:
                prod_description += word + ' '
                
        scrape_descr_df.loc[i, 'Product'] = product
        scrape_descr_df.loc[i, 'Web_Description'] = prod_description
        scrape_descr_df.to_csv(csvPath, encoding='utf-8', index=False)