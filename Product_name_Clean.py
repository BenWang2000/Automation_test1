import requests
import psycopg2
import torch
import json

#This script is cleaning the product_name column by this rule:
# 1. make sure the product_name does not include the brand name
# 2. make sure the product_name does not include the sub_category name/content
# 3. make sure the product_name does not include the 'Camera' word 



# Database connection parameters
db_params = {
    'database': 'commently',
    'user': 'postgres',
    'password': 'hungryNept@1234',
    'host': '54.159.0.118',  
    'port': 5432,  
}


#clean the brand name in product_name column#
def brand_name_filter(product_name, brand):
    if brand in product_name:
        return product_name.replace(brand, '').strip()
    return product_name


#clean the category name in product_name column#
def category_name_filter(product_name, category_name):
    if category_name in product_name:
        return product_name.replace(category_name, '').strip()
    return product_name


#clean the 'Camera' in product_name column#
def camera_include_filter(product_name):
    Camera_name = 'Camera'
    if Camera_name in product_name:
        return product_name.replace(Camera_name, '').strip()
    return product_name

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute("SELECT * FROM public.\"Cameras\"")
    records = cur.fetchall()
    index = 0

    for index, record in enumerate(records):
        index += 1

        product_name = record[4]
        brand = record[3]
        record_id = record[0]
        sub_category = record[2]


        product_name_new = brand_name_filter(product_name, brand)
        product_name_new = category_name_filter(product_name_new, sub_category)
        product_name_new = camera_include_filter(product_name_new)

        cur.execute(
            'UPDATE public."Cameras" SET "product_name" = %s WHERE id = %s',
            (product_name_new, record_id)
        )
    # Commit the changes to the database
    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()

#how to use this script: change the index abou product_name that you want clean and then run the script
#Example: for product_name: Nikon Z 9 Camera, after script: Z 9 #


