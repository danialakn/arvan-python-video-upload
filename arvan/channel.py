
import requests


#-----------------------------------------------------------------------------------#
def get_channel_list(api_key):
    """
     Retrieves a list of all available channels from ArvanCloud VOD API.

     Args:
         api_key (str): The API key for authenticating with ArvanCloud.

     Returns:
         dict: The JSON response containing channel data.
     """
    response = requests.get(
        'https://napi.arvancloud.ir/vod/2.0/channels',
        headers={
            'Authorization': api_key,
        }
    )
    return response.json()

#--------------------------------------------------------------------------------------------#

def get_channel_id(channel_title, api_key):
    """
    Finds the ID of a channel by its title.

    Args:
        channel_title (str): The title of the channel to search for.
        api_key (str): The API key for authenticating with ArvanCloud.

    Returns:
        str or None: The ID of the channel if found, otherwise None.
    """
    ch_list = get_channel_list(api_key=api_key)
    for channel in ch_list['data']:
        if channel['title'] == channel_title:
            return channel['id']
    return None


#----------------------------------------------------------------------------------------------------#