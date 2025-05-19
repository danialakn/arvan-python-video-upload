from channel import get_channel_id
import requests



#-------------------------------------------------------------------------------------#
def add_new_watermark(api_key: str, title: str, watermark_path: str, channel_title: str) -> dict:
    """
    Uploads and adds a new watermark image to a specific VOD channel in ArvanCloud.

    Args:
        api_key (str): Your ArvanCloud API key.
        title (str): Title for the watermark.
        watermark_path (str): Path to the watermark image file (PNG recommended).
        channel_title (str): Title of the VOD channel where the watermark should be added.

    Returns:
        dict: The JSON response from ArvanCloud API.

    Raises:
        Exception: If the upload fails or the response status code is not 201 (Created).
    """

    channel_id = get_channel_id(channel_title, api_key)

    with open(watermark_path, 'rb') as file:
        files = {
            'watermark': file
        }
        data = {
            'title': title
        }
        response = requests.post(
            url=f'https://napi.arvancloud.ir/vod/2.0/channels/{channel_id}/watermarks',
            headers={'Authorization': api_key},
            files=files,
            data=data
        )

    if response.status_code != 201:
        raise Exception(f"Failed to upload watermark: {response.status_code}, {response.text}")

    return response.json()
#-----------------------------------------------------------------------------------------#

def get_watermark_id(api_key: str, channel_title: str, watermark_name: str) -> str:
    """
    Retrieve the ID of a watermark from an ArvanCloud channel by its title.

    This function sends a GET request to ArvanCloud's API to list all watermarks
    for the specified channel, then searches for the watermark with the given title.

    Parameters:
        api_key (str): The API key for authenticating with ArvanCloud.
        channel_title (str): The title of the channel to search within.
        watermark_name (str): The title of the watermark to find.

    Returns:
        str: The ID of the watermark if found, otherwise None.

    Raises:
        Exception: If the API request fails.
    """
    channel_id = get_channel_id(channel_title, api_key)

    response = requests.get(
        url=f'https://napi.arvancloud.ir/vod/2.0/channels/{channel_id}/watermarks',
        headers={'Authorization': api_key}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve watermarks: {response.status_code}, {response.text}")

    watermarks = response.json().get('data', [])

    for watermark in watermarks:
        if watermark.get('title') == watermark_name:
            return watermark.get('id')

    return None  # If no watermark is found


#---------------------------------------------------------------------------------------#