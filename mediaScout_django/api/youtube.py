import json
import os
import zipfile
from dotenv import load_dotenv
from googleapiclient.discovery import build
from pytube import YouTube


load_dotenv()
service = build('youtube', 'v3', developerKey=os.getenv('API_KEY'))

def get_channel_upload_playlist(channel_id):
    # Get uploads playlist of channel
    channel_request = service.channels().list(
        part="contentDetails",
        id=channel_id,
        quotaUser=os.getenv('QUOTA_USER'), # To get the maximal request pro user
    )
    channel_response = channel_request.execute()
    return channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_all_new_channel_videos(channel_id: str, existing_video_ids: set):
    next_page_token = None
    fetched_videos = set()
    
    while True:

        request = service.playlistItems().list(
            part="contentDetails",
            playlistId=get_channel_upload_playlist(channel_id),
            maxResults=100,
            pageToken=next_page_token,
            quotaUser=os.getenv('QUOTA_USER'), 
        )

        response = request.execute()
        video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]

        batch = service.new_batch_http_request()
        for video_id in video_ids:
            request = service.videos().list(
                # Get liveStreamingDetails to filter out scheduled/live live streams
                part="liveStreamingDetails", 
                id=video_id,
                quotaUser=os.getenv('QUOTA_USER'),
            )
            # Use http batches to only send 1 request with multiple API calls
            batch.add(request, callback=lambda _, response, exception: handle_response(response, exception, existing_video_ids, fetched_videos))
        batch.execute()

        if 'nextPageToken' not in response:
            break
        next_page_token = response['nextPageToken']
    return fetched_videos

def handle_response(response, exception, saved_videos, fetched_videos):
    if exception is not None:
        print (exception)
    else:
        for item in response["items"]:
            if "liveStreamingDetails" not in item: # Filter out live streams
                video_id = item["id"]
                if video_id not in saved_videos:
                    fetched_videos.add(video_id)

def download_youtube_video(video_id):
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    streams = yt.streams.filter(progressive=True)
    lowest_resolution = None
    # Find lowest resolution downloadable
    for stream in streams:
        if lowest_resolution is None:
            lowest_resolution = stream
        elif stream.resolution < lowest_resolution.resolution:
            lowest_resolution = stream

    if lowest_resolution is None:
        return

    video_data = f'video_data_({yt.video_id}).mp4'
    video_info = f'video_info_({yt.video_id}).json'
    archive = f'{yt.video_id}.zip'
    data_path = f'{os.path.dirname(os.path.abspath(__file__))}{os.getenv("DATA_PATH")}'

    # Check if directory exists or not
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Change the current working directory
    if os.getcwd() != data_path:
        os.chdir(data_path)

    # Download video
    stream.download(filename=video_data)

    # Save the video information as a json file
    with open(video_info, 'w') as f:
        json.dump(get_youtube_video_info(yt), f)

    # Create a zip file and add the video file and json file
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(video_data)
        zip_file.write(video_info)
    
    # Delete unzipped files
    os.remove(video_data)
    os.remove(video_info)

    return video_info


def get_youtube_video_info(yt: YouTube):
    video_info = {
        'video_id': yt.video_id,
        'title': yt.title,
        'description': yt.description,
        'publish_date': yt.publish_date.strftime("%Y-%m-%d %H:%M:%S"),
        'length': yt.length
    }
    return video_info

def youtube_channel_id_valid(channel_id):
    request = service.channels().list(id=channel_id, part='snippet')
    response = request.execute()
    if 'items' in response:
        return True
    else:
        return False