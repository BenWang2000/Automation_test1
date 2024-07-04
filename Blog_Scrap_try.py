import requests
import psycopg2
import torch
import datetime
import json
from bs4 import BeautifulSoup

#  Tarchar function # 
def scrape_data_techradar(search_term):
    # Construct the URL
    url = f'https://www.techradar.com/search?searchTerm={search_term.replace(" ", "+")}'
    
    response = requests.get(url)
    scraped_data = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all article links
        articles = soup.find_all('a', class_='article-link', href=True)

        # Extract and store the links
        for article in articles:
            url = article.get('href')

            # Find the header
            header = article.find('header')
            
            # Find the title
            title_tag = header.find('h3', class_='article-name')
            title = title_tag.text.strip() if title_tag else None

            # Extract the full text content
            full_text = article.text.strip()

            # Extract the author
            author_start = full_text.find("By")
            author_end = full_text.find("published", author_start)
            author = full_text[author_start:author_end].strip() if author_start != -1 and author_end != -1 else None

            # Extract the published time
            time_start = author_end
            time_end = full_text.find("\n", time_start)
            published_time = full_text[time_start:time_end].strip() if time_start != -1 and time_end != -1 else None

            # Extract the description
            desc_start = full_text.find("\n", time_end)
            description = full_text[desc_start:].strip() if desc_start != -1 else None

            item = {
                "Title": title,
                "URL": url,
                "Published Time": published_time,
                "Description": description,
                "Characters": "",
                "Views": "",
                "Source": "TechRadar",
            }
            scraped_data.append(item)
    else:
        print(f"Failed to retrieve the webpage for {search_term}. Status code: {response.status_code}")
    
    return scraped_data

def scrape_data_digitalcamera(search_term):
    # Construct the URL
    url = f'https://www.digitalcameraworld.com/search?searchTerm={search_term.replace(" ", "+")}'
    
    response = requests.get(url)
    scraped_data = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all article links
        articles = soup.find_all('a', class_='article-link', href=True)

        # Extract and store the links
        for article in articles:
            url = article.get('href')

            # Find the header
            header = article.find('header')
            
            # Find the title
            title_tag = header.find('h3', class_='article-name')
            title = title_tag.text.strip() if title_tag else None

            # Extract the full text content
            full_text = article.text.strip()

            # Extract the author
            author_start = full_text.find("By")
            author_end = full_text.find("published", author_start)
            author = full_text[author_start:author_end].strip() if author_start != -1 and author_end != -1 else None

            # Extract the published time
            time_start = author_end
            time_end = full_text.find("\n", time_start)
            published_time = full_text[time_start:time_end].strip() if time_start != -1 and time_end != -1 else None

            # Extract the description
            desc_start = full_text.find("\n", time_end)
            description = full_text[desc_start:].strip() if desc_start != -1 else None

            item = {
                "Title": title,
                "URL": url,
                "Published Time": published_time,
                "Description": description,
                "Views": "",
                "Characters": "",
                "Source": "DigitalCamera",
            }
            scraped_data.append(item)
    else:
        print(f"Failed to retrieve the webpage for {search_term}. Status code: {response.status_code}")
    
    return scraped_data

def scrape_data_photographylife(url='https://photographylife.com/camera-reviews'):
    # Send a GET request to the website
    response = requests.get(url)

    # Initialize an empty list to store the data
    data = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links on the page
        links = soup.find_all('a', href=True)

        # Extract and store the links
        for link in links:
            item = {
                "Title": link.text.strip(),
                "URL": link['href'],
                "Views": "",
                "Characters": "",
                "source": "PhotographyLife",
            }
            data.append(item)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    return data

def scrape_data_cameralabs(url = 'https://www.cameralabs.com/camera-reviews/'):
    # Send a GET request to the website
    response = requests.get(url)

    # Initialize an empty list to store the data
    data = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links on the page
        links = soup.find_all('a', href=True)

        # Extract and store the links
        for link in links:
            item = {
                "Title": link.text.strip(),
                "URL": link['href'],
                "Views": "",
                "Characters": "",
                "source": "PhotographyLife",
            }
            data.append(item)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    return data

#clear data output functions, define by whether product name in title# 

def contains_all_words(product_name, title):
    product_words = product_name.lower().strip().split()
    title_words = title.lower().strip()
    return all(word in title_words for word in product_words)

def find_blogs(product_name, json_data):
    matching_blogs = []
    seen_titles = set()
    for item in json_data:
        title = item['Title']
        if contains_all_words(product_name, title):
            if title not in seen_titles:
                matching_blogs.append(item)
                seen_titles.add(title)
    return matching_blogs

# Database connection parameters
db_params = {
    'database': 'commently',
    'user': 'postgres',
    'password': 'hungryNept@1234',
    'host': '54.159.0.118',  
    'port': 5432,  
}

try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    cur.execute('SELECT * FROM public."Cameras" ORDER BY id')
    records = cur.fetchall()
    cur.execute('SELECT * FROM public."CameraUserContent" ORDER BY id')
    users = cur.fetchall()
    index = 0

    for record, user in zip(records, users):
        index += 1

        product_name = record[4]
        user_id = user[0]

        # Scrape data and find blogs
        blog_techradar_list = find_blogs(scrape_data_techradar(product_name))
        blog_cameralabs_list = find_blogs(scrape_data_cameralabs(product_name))
        blog_photographylife_list = find_blogs(scrape_data_photographylife(product_name))
        blog_digitalcamera_list = find_blogs(scrape_data_digitalcamera(product_name))

        # Combine all blog lists into a single list
        combined_blog_list = blog_techradar_list + blog_cameralabs_list + blog_photographylife_list + blog_digitalcamera_list

        # Filter the data (assuming you have a function to transform the combined list)
        filtered_blog_data_json = json.dumps(combined_blog_list)

        # Update the database
        cur.execute(
            'UPDATE public."CameraUserContent" SET "blog" = %s WHERE id = %s',
            (filtered_blog_data_json, user_id)
        )

    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()





