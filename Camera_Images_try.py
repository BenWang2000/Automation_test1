import requests
import psycopg2
import torch
import datetime
import json


#This is the script that collecting the camera pictures from Amazon and save their .jpg links on the table Cameras at Image_links column.#

#Some import features about the collected feature :#
# API Used: Rainforest API #
# Image came from: the first non-sponsor search result shop page at Amazon. How: by search "brand+product_name" at Amazon page to get#
# Table : Cameras. Column : Image_Links. Data type: jsonb #
#'How to use this Sccript' is at the end of this script#

# Database connection parameters
db_params = {
    'database': 'commently',
    'user': 'postgres',
    'password': 'hungryNept@1234',
    'host': '54.159.0.118',  
    'port': 5432,  
}

# Get the product asin by API, search term is 'brand' + 'product_name', asin is the UNIQUE product id at Amazon website. you can directly search "Amazon asin ######" to find the corresponding store page#

def get_amazon_search_product_id(product_name, brand_name):
    asin_list = []

    url = "https://api.rainforestapi.com/request"
    search_term = f'{product_name}' if brand_name in product_name else f'{brand_name} {product_name}'
    
    params = {
        'api_key': '98ACD50848644E4C83D507A76C219176',    #API key need to change/check every time using this script#
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'search_term': search_term,
        'exclude_sponsored': 'true'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        search_result = response.json()
        if 'search_results' in search_result:
            asin_found = False
            for item in search_result['search_results']:
                if 'asin' in item:
                    asin_list.append(item['asin'])
                    asin_found = True
                    break  
            if not asin_found:
                asin_list.append('N/A')
        else:
            asin_list.append('N/A')
    else:
        asin_list.append('N/A')
    
    return asin_list

# Use the asin_list to search and get the json format output of the store #

def get_amazon_search_image_results(asin):
    url = "https://api.rainforestapi.com/request"
    params = {
        'api_key': '98ACD50848644E4C83D507A76C219176',
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': asin
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data
    
#Filtered function that only choose all the product pictures .jpg links from the shop page#

def filter_variant_links(json_responses):
    filtered_responses = []
    for response in json_responses:
        filtered_links = []
        seen_links = set()
        product = response.get('product', {})
        images = product.get('images', [])
        for image in images:
            link = image.get('link', '')
            if 'variant' in image and '.jpg' in link and link not in seen_links:
                filtered_links.append({'variant': image['variant'], 'link': link})
                seen_links.add(link)
        variants = product.get('variants', [])
        for variant in variants:
            images = variant.get('images', [])
            for image in images:
                link = image.get('link', '')
                if 'variant' in image and '.jpg' in link and link not in seen_links:
                    filtered_links.append({'variant': image['variant'], 'link': link})
                    seen_links.add(link)
        filtered_responses.append(filtered_links)
    return filtered_responses
    
#Connect to database and update data#
try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("SELECT * FROM public.\"Cameras\"")
    records = cur.fetchall()
    index = 0               # using the table UNIQUE Btree index#

    for i, record in enumerate(records):
        index += 1
        if index < 237:
            continue
        if index > 240: 
            break

        product_name = record[4]
        brand = record[3]
        record_id = record[0]

        asin_list = get_amazon_search_product_id(product_name, brand)
        json_responses = []

        for asin in asin_list:
            if asin != 'N/A':
                product_data = get_amazon_search_image_results(asin)
                json_responses.append(product_data)
            else:
                filtered_links_json = 'N/A'
                cur.execute(
                    'UPDATE public."Cameras" SET "Image_links" = %s WHERE id = %s',
                    (filtered_links_json, record_id)
                )
                break

        if json_responses:
            filtered_links = filter_variant_links(json_responses)
            filtered_links_json = json.dumps(filtered_links)
            cur.execute(
                'UPDATE public."Cameras" SET "Image_links" = %s WHERE id = %s',
                (filtered_links_json, record_id)
            )

    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()


#How to use this script: 1. change the API key, make sure the key is active 2. change the index to make sure the rows u want to save# 

#Example : the data will be saved in this format, for product name "Nikon Z 9" at the Image_llink column, it will be a json formate data with content:# 
#[{"link": "https://m.media-amazon.com/images/I/71hS+ps+v5L._AC_SL1000_.jpg", "variant": "MAIN"}, {"link": "https://m.media-amazon.com/images/I/41QkjNmc8aL._AC_.jpg", "variant": "PT01"}, {"link": "https://m.media-amazon.com/images/I/41e5t1LjOPL._AC_.jpg", "variant": "PT02"}, {"link": "https://m.media-amazon.com/images/I/41R-eEw8d+L._AC_.jpg", "variant": "PT03"}, {"link": "https://m.media-amazon.com/images/I/711uqbc4bLL._AC_SL1500_.jpg", "variant": "MAIN"}]#

#Interpretation: Search "Nikon Z 9" at Amazon.com, with Deartment 'ALL', the first outcome without 'sponsored' tag, the shop links is here : https://www.amazon.com/Nikon-Flagship-Professional-Full-Frame-mirrorless/dp/B09KHC4XCT/ref=sr_1_3?crid=1JE1B8UZE9FQK&dib=eyJ2IjoiMSJ9.AXeNX0DkoLNNX_nn-r7mwQJnDNqbYAgWxJkwXk9Qt6OfzfAgsYXK3wAmDLG2fAuI0sQ_QUXqbKMA64cOA0S8zIKHgqIaB_BBA8uifSQ4t7NgP3_eDpPyNyiZ_XPTGH0ezQiGOPzNd_-_xHlYK8BC7cQ1PoJJzBQ-M_Zq_Uqm9He_aAQKq9IOd6-USBjkqTru5jpGHlNGyRbSfYemLLq74ZAlNYBQJqAwAPldAHXkag8.UOd3d7WITToyvP6Fx7m8q1zX-mCfJ9VQ2bHVfQKJ3oA&dib_tag=se&keywords=Nikon+Z+9&qid=1719602767&sprefix=nikon+z+9%2Caps%2C92&sr=8-3 #
#the links in the json formate data at 'Image_links' column(which 4 total here) are every picture links in the product part# 


