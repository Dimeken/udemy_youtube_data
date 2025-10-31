import requests as re
import os
import json

from dotenv import load_dotenv
from datetime import date

load_dotenv(dotenv_path='./.env')

API_KEY = os.getenv('API_KEY')
CHANNEL_HANDLE = 'MrBeast'


def get_playlist_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'

        response = re.get(url)
        response.raise_for_status()

        data = response.json()

        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        
        print(channel_playlistId)
        return channel_playlistId
    
    except re.exceptions.RequestException as e:
        raise e
    
def get_video_ids(channel_playlist_id):
    video_ids = []
    page_token = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={channel_playlist_id}&key={API_KEY}'

    try:
        while True:
            url = base_url
            if page_token:
                url += f'&pageToken={page_token}'

            response = re.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            
            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return video_ids

    except re.exceptions.RequestException as e:
        raise e
    



def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id+batch_size]


    try:
        for batch in batch_list(video_ids, max_results):
            video_ids_str = ','.join(batch)
            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}'

            resp = re.get(url)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    'video_id': video_id,
                    'title': snippet['title'],
                    'publishedAt': snippet['publishedAt'],
                    'duration': contentDetails['duration'],
                    'viewCount': statistics.get('viewCount', None),
                    'likeCount': statistics.get('likeCount', None),
                    'commentCount': statistics.get('commentCount', None)
                }

                extracted_data.append(video_data)
        
        return extracted_data

    except re.exceptions.RequestException as e:
        raise e
    except Exception as e:
        raise e


def save_to_json(extracted_data):
    file_path = f'./data/youtube_data_{date.today()}.json'

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)




if __name__ == '__main__':
    max_results = 10
    channel_playlist_id = get_playlist_id()
    video_ids = get_video_ids(channel_playlist_id)
    print(f'video_ids: {video_ids}')
    extracted_data = extract_video_data(video_ids)
    save_to_json(extracted_data)

    print(extracted_data)

