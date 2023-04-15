""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import datetime
import os
import image_lib
import apod_api
import hashlib
import inspect
import sys
import sqlite3
import string

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    print("Setting desktop to", apod_info["file_path"])
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])
        print("...success")
    else:
        print("Error: Couldn't set desktop to", apod_info["file_path"])


def is_valid_date(date_str):
    date1 = datetime.datetime(1995, 6, 16)
    date2 = datetime.datetime.today()
    try:
        # Attempt to parse the date string into a datetime object
        dateObject = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if(date1 > dateObject):
            print("Error: Date before APOD start date not allowed");
            return False
        elif(dateObject > date2):
            print("Error: APOD date cannot be in future");
            return False
        return True
        
    except ValueError:
        # The date string is not a valid date
        print("Error: Invalid date format or date out of range; Date entered :", date_str)
        return False


def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # TODO: Complete function body

    input_date = ""

    if(len(sys.argv) == 1):
        input_date = str(datetime.date.today())
        # input_date = "2023-04-10"
    else: 
        input_date = sys.argv[1]

    apod_date = datetime.date

    if(is_valid_date(input_date)):
        apod_date = date.fromisoformat(input_date)
    else:
        print("Script Execution Aborted")
        exit()

    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    # print(script_path)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """

    print(parent_dir)

    global image_cache_dir 
    image_cache_dir = parent_dir + r"\image_cache_dir"
    global image_cache_db 
    image_cache_db = parent_dir + r"\image_cache_dir\APOD.db"
    # TODO: Determine the path of the image cache directory
    # TODO: Create the image cache directory if it does not already exist
    print("Image cache directory:", image_cache_dir)
    if(os.path.exists(image_cache_dir)):
        print("Image cache directory already exists.")
    else:
        print("Image cache directory created.")
        os.makedirs(image_cache_dir)

    # TODO: Determine the path of image cache DB
    # TODO: Create the DB if it does not already exist
    print("Image cache DB:", image_cache_db)
    if(os.path.isfile(image_cache_db)):
        print('Image cache DB already exists.')
    else:
        conn = sqlite3.connect(image_cache_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE image_cache
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT,
              explaination TEXT, 
              file_path TEXT,
              sha256 TEXT)''')
        conn.commit()
        c.close()
        conn.close()
        print('Image cache DB created.')

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # TODO: Download the APOD information from the NASA API
    apod_data = apod_api.get_apod_info(apod_date)
    
    # TODO: Download the APOD image
    print("Downloading APOD image.")
    apod_img_url = apod_api.get_apod_image_url(apod_data)
    apod_img_data = image_lib.download_image(apod_img_url)
    print("...success")
    
    # TODO: Check whether the APOD already exists in the image cache
    print("Finding APOD image in image cache db.")
    hash_input = apod_data['title'] + apod_data['date']
    hash_output = hash(hash_input)

    apod_record_id = get_apod_id_from_db(hash_output)

    # TODO: Save the APOD file to the image cache directory
    if(apod_record_id == 0):
        apod_title = remove_special_characters(apod_data['title'])
        apod_img_save_path = determine_apod_file_path(apod_title, apod_img_data)
        image_lib.save_image_file(apod_img_data, apod_img_save_path)
        print("APOD image saved to image cache db.:", apod_img_save_path)
        
        # TODO: Add the APOD information to the DB
        apod_db_id = add_apod_to_db(apod_title, apod_data['explanation'], apod_img_save_path, hash_output)
        if(apod_db_id == 0):
            return 0
        else:
            return apod_db_id
    else:
        print("APOD image is already in cache.")
        return get_apod_id_from_db(hash_output)
        

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # TODO: Complete function body
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    print("Adding APOD to image cache DB")
    try:
        c.execute("INSERT into image_cache (title, explaination, file_path, sha256) values(?,?,?,?)", 
                (title, explanation, file_path, sha256))
        conn.commit()
        print('...success')
        return get_apod_id_from_db(sha256)
    except:
        print('Error: APOD not added to db.')
        return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body

    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("SELECT * FROM image_cache WHERE sha256=?", (image_sha256,))
    
    row = c.fetchone()
    
    if row:
        c.close()
        conn.close()
        return row[0]
    else:
        c.close()
        conn.close()
        return 0


def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body

    apod_img_save_path = image_cache_dir + "\\" + image_title + ".jpg"
    return apod_img_save_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    apod_info = {
        'title': '', 
        'explanation': '',
        'file_path': 'TBD',
    }

    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("SELECT * FROM image_cache WHERE id=?", (image_id,))
    
    row = c.fetchone()

    if row:
        apod_info['title'] = row[1]
        apod_info['explanation'] = row[2]
        apod_info["file_path"] = row[3]
    else:
        return 0

    c.close()
    conn.close()

    return apod_info

def remove_special_characters(input_string):
    # Define the set of allowed characters
    allowed_characters = string.ascii_letters + string.digits + ' '
    
    # Remove all characters that are not in the allowed set
    output_string = ''.join(c for c in input_string if c in allowed_characters)
    output_string = output_string.strip()
    output_string = output_string.replace(' ', '_')

    return output_string

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    return

def hash(input_str):
    # create a SHA-256 hash object
    hash_obj = hashlib.sha256()

    # update the hash object with the input string
    hash_obj.update(input_str.encode())

    # get the hexadecimal representation of the hash value
    hash_value = hash_obj.hexdigest()

    # print the hash value
    return hash_value

if __name__ == '__main__':
    main()