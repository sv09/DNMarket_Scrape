# from google.colab import drive
# drive.mount('/content/drive')
#pip install beautifulsoup4


## Required Libraries
import os
from bs4 import BeautifulSoup
from bs4 import NavigableString
import csv
import pandas as pd


## Global variables
global pageSet
global content_map

pageSet = set()
content_map={}


## HELPER FUNCTIONS

## function returns an item's overall rating (if present) and an array of all the feedbacks
def getItemRatingAndFeedback(main, iFeedback):
  ratings = main.find_all('span', {'class': 'container'})
  if(len(ratings) >= 1):
    item_rating = ratings[0].text
  else:
    item_rating = ' '

  feedbacks = main.find_all('div', class_='feedbacks')
  if(len(feedbacks) >= 1):
    for row in feedbacks[0].find('table').tbody.find_all('tr'):
      if(len(row.find_all('td'))>1):
        iFeedback.append(row.find_all('td')[1].text)
  else:
    itr=0
    for i in main.find_all(True):
      if(i.name == 'h3' and i.text == 'item feedback'):
        itr += 1
      if(itr == 1 and i.name == 'table'):
        if(i.tbody):
          for row in i.tbody.find_all('tr'):
            if(len(row.find_all('td'))>1):
              iFeedback.append(row.find_all('td')[1].text)

  return item_rating.strip(), iFeedback


## function returns a vendor's overall rating (if present) and an array of all the feedbacks
def getVendorRatingAndFeedback(main, vFeedback):
  ratings = main.find_all('span', {'class': 'container'})
  if(len(ratings) > 1):
    vendor_rating = ratings[1].text
  else:
    vendor_rating = ' '

  feedbacks = main.find_all('div', class_='feedbacks')
  if(len(feedbacks) > 1):
    for row in feedbacks[1].find('table').tbody.find_all('tr'):
      if(len(row.find_all('td'))>1):
        vFeedback.append(row.find_all('td')[1].text)
  else:
    itr=0
    for i in main.find_all(True):
      if(i.name == 'h3' and i.text == 'vendor feedback'):
        itr += 1
      if(itr == 1 and i.name == 'table'):
        if(i.tbody):
          for row in i.tbody.find_all('tr'):
            if(len(row.find_all('td'))>1):
              vFeedback.append(row.find_all('td')[1].text)

  return vendor_rating.strip(), vFeedback


def getData(soup, pageName, iFeedback, vFeedback, folderName):
  main = soup.find('div', class_='body')
  if(main):
    body = main.find('div')

    if(body):
      id=''
      txt=''
      productName=''
      price=''
      description=''
      vendor=''
      shipsFrom_ = 'ships from:'
      shipsTo_ = 'ships to:'
      shipsFrom = 'ships from'
      shipsTo = 'ships to'
      shipping_desc = None
      shipping_delivery=None
      shipping_price=None

      item_rating, iFeedback = getItemRatingAndFeedback(main, iFeedback)
      vendor_rating, vFeedback = getVendorRatingAndFeedback(main, vFeedback)

      pr = body.find('div', class_='price_big')
      if(pr):
        price=pr.text

      for i in body.find_all(True):

        if(pageName != None):
          productName = pageName
        elif(i.name == 'h2'):
          productName = i.text

        if(i.text.split(' ')[0] == 'vendor:'):
          vals = i.text.split(' ')
          vendVal = vals[1].split('\n')
          vendor = vendVal[0]

        id = vendor + productName

        for p in i.find_all('p'):
          description += ' ' + p.text

        if shipsFrom in i.text.strip():
          txt = i.text.split('\t')

        for tr in i.find_all('tr'):
          for td in tr.find_all('td'):
            if(shipping_desc != None and shipping_delivery != None and shipping_price != None):
              continue
            if(shipping_desc == None):
              shipping_desc = td.text
            elif(shipping_delivery == None):
              shipping_delivery = td.text
            elif(shipping_price == None):
              shipping_price = td.text
      
        if(txt):
          source = ''
          destination = ''
          splt = txt[0].split('\n')
          for val in splt:
            if(shipsFrom_ in val):
              source += val.split(':')[1]
            elif(shipsFrom in val):
              source += val.split(' ')[1]
            if(shipsTo_ in val):
              destination += val.split(':')[1]
            elif(shipsTo in val):
              destination += val.split(' ')[1]

          content_map[id] = [productName, price, description, source, destination, shipping_desc, shipping_delivery, shipping_price, item_rating, iFeedback, vendor, vendor_rating, vFeedback, pageName, folderName]


## Access path and data
os.chdir('/content/drive/MyDrive/silkroad2')

# i=0
# for folder in os.listdir('/content/drive/MyDrive/silkroad2'):
p_foldr='2014_01-03(2013)'
c_foldr='02'
for sub_folder in os.listdir(f'/content/drive/MyDrive/silkroad2/{p_foldr}/{c_foldr}'):
  filenames=[]
  for file in os.listdir(f'/content/drive/MyDrive/silkroad2/{p_foldr}/{c_foldr}/{sub_folder}/items'):
    filenames.append(os.path.join(f'/content/drive/MyDrive/silkroad2/{p_foldr}/{c_foldr}/{sub_folder}/items', file))
  
  for fname in filenames:
    path = fname
    elem = path.split('/')
    size = len(elem)
    page_name = elem[size-1].split('?')[0]
    file_name = elem[size-1]
    

    if page_name not in pageSet:
      pageSet.add(page_name)

      iFeedback = []
      vFeedback = []
      with open(path) as f:
        soup = BeautifulSoup(f.read())
      getData(soup, page_name, iFeedback, vFeedback, sub_folder)
    else:
      for key in content_map:
        if(key != None):
          value = content_map[key]
          if(value[13] == page_name):
            # iFeedback = value[9]
            iFeedback = []
            vFeedback = value[12]

      with open(path) as f:
        soup = BeautifulSoup(f.read())
      getData(soup, page_name, iFeedback, vFeedback, sub_folder)


# create csv file, add data, and save to google drive
os.chdir('/content/drive/MyDrive/Downloads/data')

output_file = open('dmData.csv', 'a')
csv_writer = csv.writer(output_file)
csv_writer.writerow(['ID', 'Product', 'Price', 'Description', 'Location_From', 'Location_To', 'Shipping_Description', 'Shipping_Est_Delivery', 'Shipping_Price', 'Item_Rating', 'Item_Feedback', 'Vendor Name', 'Vendor_Rating', 'Vendor_Feedback', 'PageName', 'FolderName'])

for key in content_map:
  if(key != None):
    value = content_map[key]
    csv_writer.writerow([key, value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7], value[8], value[9], value[10], value[11], value[12], value[13], value[14]])

output_file.close()
