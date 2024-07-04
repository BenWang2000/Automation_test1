import requests
import psycopg2
import torch
import datetime
import json

#This is the script to collect search outcomes of product_names on Youtube. The data output will be a json format list which contain plenty elements with same features. features will be found under the function 'transform_data'#
##

#get the related Youtube search output json_urls #

def get_json_url(query):
    video_links = []
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube",
        "q": query,
        "api_key": "LmmHDSsAa33WNDDQrVgP2hUx"
    }

    response = requests.get(url, params=params)
    data = response.json()
    json_url = data["search_metadata"]["json_url"]
    video_links.append(json_url)
    return video_links

def format_views(views):
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    else:
        return str(views)
    
def transform_data(api_response):
    transformed_data = []
    for index, video in enumerate(api_response["videos"], start=1):
        transformed_data.append({
            "Youtube_index": video.get("id", ""),
            "title": video.get("title", ""),
            "description": video.get("description", ""),
            "Video_Cover": video.get("thumbnail", {}).get("rich", ""),
            "type": "video",
            "views": format_views(video.get("views", 0)),
            "link": video.get("link", ""),
            "Post_Time": video.get("published_time", ""),
            "source": "YouTube"
        })
    return transformed_data

def fetch_video_data(json_links):
    all_video_data = []
    
    for json_url in json_links:
        # Remove double quotes for the request
        json_url = json_url.strip('"')
        response = requests.get(json_url)
        data = response.json()
        VD_data = {"videos": data.get("videos", [])}
        all_video_data.append(VD_data)
    
    return all_video_data

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
    index = 0

    cur.execute('SELECT * FROM public."Cameras" ORDER BY id')
    records = cur.fetchall()
    cur.execute('SELECT * FROM public."CameraUserContent" ORDER BY id')
    users = cur.fetchall()
    index = 0

    for record, user in zip(records, users):
            index += 1
            product_name = record[4]
            user_id = user[0]

            video_json_list = get_json_url(product_name)
            video_data = fetch_video_data(video_json_list)
            filtered_video_data = transform_data({"videos": video_data})
            filtered_video_data_json = json.dumps(filtered_video_data)

            cur.execute(
                'UPDATE public."CameraUserContent" SET "video" = %s WHERE id = %s',
                (filtered_video_data_json, user_id)
            )


    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()






