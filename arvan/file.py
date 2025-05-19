import os
import base64
import requests
import re
from tusclient import client
from channel import get_channel_id
from watermark import get_watermark_id
#----------------------------------------------------------------------------------------------------#
def upload_video_to_arvan(api_key: str, video_path: str, channel_title: str) -> str:
    """
    Uploads a video file to ArvanCloud's temporary file storage using the TUS protocol.

    This function:
    - Retrieves the channel ID by its title.
    - Encodes the filename and filetype in base64 for metadata.
    - Requests an upload URL from ArvanCloud.
    - Uploads the video using the tus protocol with the tusclient library.

    Note:
        The uploaded video will be stored in ArvanCloud's *temporary files* section
        and must later be moved or processed if needed.

    Args:
        api_key (str): Your ArvanCloud API key.
        video_path (str): The full path to the video file to upload.
        channel_title (str): The title of the VOD channel in ArvanCloud.

    Returns:
        str: The uploaded file's unique `file_id` if successful.

    Raises:
        Exception: If any step fails (e.g., upload URL not received, file_id not found, etc).
    """

    # ---- Prepare file and metadata
    channel_id = get_channel_id(channel_title, api_key)
    file_size = os.path.getsize(video_path)
    file_name = os.path.basename(video_path)
    file_type = 'video/mp4'

    encoded_filename = base64.b64encode(file_name.encode()).decode()
    encoded_filetype = base64.b64encode(file_type.encode()).decode()
    metadata = f'filename {encoded_filename},filetype {encoded_filetype}'

    # ---- Request upload URL from ArvanCloud
    response = requests.post(
        f'https://napi.arvancloud.ir/vod/2.0/channels/{channel_id}/files',
        headers={
            'Authorization': api_key,
            'tus-resumable': '1.0.0',
            'upload-length': str(file_size),
            'upload-metadata': metadata,
        }
    )

    if response.status_code != 201:
        raise Exception(f"Failed to get upload URL: {response.status_code}, {response.text}")

    upload_url = response.headers.get('Location')
    if not upload_url:
        raise Exception("Upload URL not found in response headers")

    # ---- Extract file_id from URL
    match = re.search(r'/files/([^/]+)$', upload_url)
    file_id = match.group(1) if match else None
    if not file_id:
        raise Exception("file_id not found in upload URL")

    # ---- Check upload offset (optional)
    head_res = requests.head(upload_url, headers={'Authorization': api_key})
    upload_offset = head_res.headers.get('upload-offset', '0')

    # ---- Upload the file using tusclient
    tus_client = client.TusClient("https://napi.arvancloud.ir/")  # Dummy URL; only needed to initialize uploader
    tus_client.set_headers({
        'Authorization': api_key,
        'tus-resumable': '1.0.0',
        'Content-Type': 'application/offset+octet-stream',
    })

    with open(video_path, 'rb') as file_stream:
        uploader = tus_client.uploader(
            file_stream=file_stream,
            chunk_size=200 * 2048,
            url=upload_url,
            metadata={'filename': file_name, 'filetype': file_type}
        )
        uploader.upload()

    return file_id

#----------------------------------------------------------------------------------------#

def get_file_id(api_key, channel_title, file_title):

    """
    Retrieve the ID of a specific uploaded file in a given ArvanCloud channel by its filename.

    This function first fetches the channel ID based on the provided channel title,
    then retrieves the list of files (drafts) in that channel. It searches through
    the list to find a file whose filename matches the given file_title. If found,
    it returns the file's ID. If not found, it returns None.

    Parameters:
        api_key (str): The API key used for authorization with ArvanCloud.
        channel_title (str): The title of the channel to search in.
        file_title (str): The exact name of the file to find (e.g., "video.mp4").

    Returns:
        str or None: The ID of the file if found, otherwise None.

    Raises:
        Exception: May raise an exception internally from dependent functions (e.g., get_channel_id)
                  if the channel cannot be found or a network error occurs.
    """

    channel_id = get_channel_id(channel_title, api_key)

    response = requests.get(
        url=f'https://napi.arvancloud.ir/vod/2.0/channels/{channel_id}/files',
        headers={'Authorization': api_key}
    ).json()


    for file in response.get('data', []):
        if file.get('filename') == file_title:
            return file.get('id')

    return None  # اگر چیزی پیدا نشد


#----------------------------------------------------------------------------------------#
def save_as_video(api_key, channel_title, file_name=None, file_id=None, watermark_title=None,
                  watermark_area="FIX_TOP_LEFT"):
    """
    Creates and saves a video in an ArvanCloud VOD channel using a file (draft), optionally attaching a watermark.

    Parameters:
    ----------
    api_key : str
        Your ArvanCloud API key.
    channel_title : str
        The title of the VOD channel where the video will be saved.
    file_name : str, optional
        The name of the draft file (used if file_id is not directly provided).
    file_id : str, optional
        ID of the draft file to be converted to a video. If None, it will be looked up using file_name.
    watermark_title : str, optional
        Title of the watermark to apply to the video.
    watermark_area : str, optional
        Position of the watermark. Default is "FIX_TOP_LEFT".
        Possible values: "FIX_TOP_LEFT", "FIX_TOP_RIGHT", "FIX_BOTTOM_LEFT", "FIX_BOTTOM_RIGHT", etc.

    Returns:
    -------
    str or None
        Returns the created video ID if successful, otherwise None.
    """

    channel_id = get_channel_id(channel_title, api_key)

    if file_id is None:
        file_id = get_file_id(api_key, channel_title, file_name)

    watermark_id = None
    if watermark_title:
        watermark_id = get_watermark_id(api_key, channel_title, watermark_title)

    data = {
        "title": file_name,
        "description": file_name,
        "file_id": file_id,
        "convert_mode": "auto",
        "thumbnail_time": 10,
        "watermark_id": watermark_id,
        "watermark_area": watermark_area,
    }

    response = requests.post(
        url=f'https://napi.arvancloud.ir/vod/2.0/channels/{channel_id}/videos',
        headers={'Authorization': api_key},
        json=data
    )

    if response.status_code in (200, 201):
        video_data = response.json().get("data", {})
        video_id = video_data.get("id")
        return video_id
    else:
        return None
