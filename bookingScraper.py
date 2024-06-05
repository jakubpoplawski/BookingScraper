from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import pathlib
from portability import resource_path

import re
import pandas as pd
import time


def load_settings():
    """The function loads the settings and creates saveback path.

    Args:
        None
    """
    
    with open(pathlib.Path(resource_path('Settings/settings.txt'))) as source:
        settings_dict = json.load(source)
    saveback_filepath = pathlib.Path(
        resource_path(
            f"SaveBacks/Results{settings_dict['destination']}.csv"))
    
    saveback_filepath = pathlib.Path(
        resource_path(f"SaveBacks/Results{settings_dict['destination']}.csv"))

    return settings_dict, saveback_filepath


def define_result_table():
    """The function creates a list of headers, and an empty list for 
    lists of results from each scraping loop.

    Args:
        None                
    """ 

    headers = ['Name', 'Old Price', 'Current Price', 
        'Normalized Price', 'Rate', 'Votes', 'Link', 'Link to loc.']
    rows = []
    return headers, rows


def build_url(destination, checkin_date, checkout_date, 
                          group_adults, no_rooms, group_children):
    """The function builds the url address for the search initiation 
    based on search parameters.

    Args:
        destination (str): Description of the user agent.
        checkin_date (str): Date in YYYY-MM-DD format.
        checkout_date (str): Date in YYYY-MM-DD format.
        group_adults (int): Number of adults.         
        no_rooms (int): Number of rooms.                 
        group_children (int): Number of children.                
    """ 

    url = f"https://www.booking.com/searchresults.pl.html"
    url += f"?ss={destination}"
    url += "&src=searchresults"
    url += "&dest_type=district"
    url += f"&checkin={checkin_date}"
    url += f"&checkout={checkout_date}"
    url += f"&group_adults={group_adults}"
    url += f"&no_rooms={no_rooms}"
    url += f"&group_children={group_children}"
    return url


def initialize_connection(user_agent):
    """The function creates a driver with applied user agent.

    Args:
        user_agent (str): Description of the user agent.
    """ 

    driverpath = pathlib.Path(resource_path('ChromeDriver/chromedriver.exe'))

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument(f"--user-agent={user_agent}")


    driver = webdriver.Chrome(service=Service(driverpath), 
                              options=chrome_options)

    return driver


def extract_data_from_box(box):
    """The function extracts and cleans data extracted from 
    a single box. The function return the results in a form
    of a list representing data of a single entry.

    Args:
        box (str): HTML code of a box element with a single result.
    """

    nights_pattern = re.compile("\d+(?= noc)")
    people_pattern = re.compile("\d+(?= dor)")    
    price_pattern = re.compile("\d+\s\d+|\d+(?= zł)")    
    opinions_pattern = re.compile("\d\s\d+|\d+(?= opi)")
    rate_pattern = re.compile('\d+.\d+(?=Oceniony)')

    name = box.find('div', {'data-testid': 'title'}).text
    current_price = box.find(
        'span', {'data-testid': 'price-and-discounted-price'}).text
    try:
        old_price = box.find(
            'span', {'class': 'c73ff05531 e84eb96b1f'}).text
        old_price_int = int(price_pattern.findall(
            old_price)[0].replace(" ", ""))
    except (AttributeError, IndexError):
        old_price = 'N/A' # not everywhere
        old_price_int = 'N/A'   
                
    price_context = box.find('div', {
        'data-testid': 'price-for-x-nights'}).text

    current_price_int = int(price_pattern.findall(
            current_price)[0].replace(" ", ""))


    nights = int(nights_pattern.findall(price_context)[0])
    people = int(people_pattern.findall(price_context)[0])   
    normalized_price = current_price_int/(nights*people)

    localization = box.find(
        'a', {'class': 'a83ed08757 f88a5204c2 a1ae279108 b98133fb50', 
                'target': '_blank'}).get('href')
    link = box.find('h3', class_ = 'aab71f8e4e').find('a').get('href')

    try:
        votes_rate = box.find(
            'div', {'data-testid': 'review-score'})        
        rate = float(rate_pattern.findall(votes_rate.find(
            'div', {'class': 'a3b8729ab1 d86cee9b25'}).text
            .replace(",", "."))[0])
        votes = int(opinions_pattern.findall(
            votes_rate.find(
            'div', {'class': 
                    'abf093bdfe f45d8e4c32 d935416c47'}).text)[0]
                    .replace(" ", ""))
    except AttributeError:
        rate = 'N/A'
        votes = 'N/A'
        
    return [name, old_price_int, current_price_int, normalized_price, 
            rate, votes, link, localization]


def click_refuse(driver, xpath_button_locator):
    """The function clicks on the refuse cookies button when detected.

    Args:
        xpath_button_locator (str): XPATH location of the button.
    """

    try:
        WebDriverWait(
            driver, 5).until(EC.element_to_be_clickable((
                By.XPATH, xpath_button_locator))).click()
    except:
        pass


def extract_boxes(driver, rows):
    """The function extract the avialable in the current scroll 
    boxes and extracts data from them.

    Args:
        driver (class): Driver object.
        rows (list): List of collected rows.
    """

    try:
        boxes_class = 'c82435a4b8 a178069f51 a6ae3c2b40 '
        boxes_class += 'a18aeea94d d794b7a0f7 f53e278e95 c6710787a4'

        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_= boxes_class)


        new_rows = list(map(extract_data_from_box, boxes))
        rows.extend(new_rows)
    except:
        pass


def scraping_loop(driver, expected_screen_scrolls, rows):
    """The function scrolls through the page and fires 
    the extract_boxes() function after every scroll to 
    collect data.

    Args:
        driver (class): Driver object.
        expected_screen_scrolls (int): number of screens to scan.
        rows (list): List of collected rows.
    """

    iteration_counter = 1

    incremental_screen_scroll = 1200
    while iteration_counter < expected_screen_scrolls:
        try:
            extract_boxes(driver, rows)
            driver.execute_script(
                f"window.scrollTo(0, {incremental_screen_scroll});")
            time.sleep(2)
            iteration_counter += 1
            incremental_screen_scroll += 1200
        except:
            continue


def prep_results(headers, rows, filepath):
    """The function prepares a DataFrame object to aggregate 
    and organize the collected data, cleaning it from duplicates.

    Args:
        headers (list): List of columns.
        rows (list): List of collected rows.
        filepath (str): Saveback location.
    """    

    result_table = pd.DataFrame(
        rows, columns = headers).drop_duplicates(subset='Link')

    # The zero column gets the name Index.
    result_table.to_csv(filepath, index_label='Index')


def main():
    settings_dict, saveback_filepath = load_settings()
    headers, rows = define_result_table()
    driver = initialize_connection(settings_dict['user_agent'])
    url = build_url(settings_dict['destination'],
                    settings_dict['checkin_date'],
                    settings_dict['checkout_date'],
                    settings_dict['group_adults'],
                    settings_dict['no_rooms'],
                    settings_dict['group_children'])

    driver.get(url)

    # Refusing cookies
    click_refuse(driver, '//*[@id="onetrust-reject-all-handler"]')

    # Closing a possible advert
    click_refuse(driver, '//button[@aria-label="Zamknij okno logowania."]')

    scraping_loop(driver, 
                  settings_dict["expected_screen_scrolls"], 
                  rows)

    prep_results(headers, rows, saveback_filepath)

    driver.quit()    


if __name__ == "__main__":
    main()
