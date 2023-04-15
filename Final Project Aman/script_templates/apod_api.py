'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''

import requests
import pytube

def main():
    # TODO: Add code to test the functions in this module
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """

    base_url = "https://api.nasa.gov/planetary/apod?api_key="
    api = "DEMO_KEY"   

    url = base_url + api + "&date=" + str(apod_date)

    print("Getting", apod_date, "APOD information from NASA") 

    response = requests.get(url)
    data = {}
    if response.status_code == 200:
        print('...success')
        data = response.json()
    else:
        print("Error calling API - status code:", response.status_code)
        exit()
    return data

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """

    if(apod_info_dict['media_type'] == 'image'):
        return apod_info_dict['hdurl']
    else:
        yt = pytube.YouTube(apod_info_dict['url'])
        thumbnail_url = yt.thumbnail_url
        return thumbnail_url


if __name__ == '__main__':
    main()