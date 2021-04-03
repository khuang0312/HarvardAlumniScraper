# Original work done by Sally Matson
# Minor changes made by Emily Dich
# Overhauled by Kevin Huang
# Last modified: 4/2/2021

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import pickle
import csv
import argparse
import time
from sys import getsizeof
from urllib.parse import urlencode
from webdriver_manager.chrome import ChromeDriverManager



def handle_element_error(element_getter):
    '''A decorator made to wrap the code that gets the elements
    
    This anticipates all errors that could happen while waiting for an element
    And prints out some information about the element we were waiting for
    '''
    def error_wrapper(*args, **kwargs): # allows arbitrary arguments to be passed in
        # we pass in arbitrary arguments since element_getter requires lots of parameters
        element, desc = None, kwargs["desc"] # ensures we have a value to print when exceptions occur
        try:
            element, desc = element_getter(*args, **kwargs)
        except TimeoutException as e:
            print(type(e), desc)
        except ElementClickInterceptedException as e:
            print(type(e), desc)
        except ElementNotInteractableException:
            print(type(e), desc)
        finally:
            # if we need the desc after... # return element, desc
            return element
            
    return error_wrapper

def new_alumnus():
    '''Helper to create new alumni dicts
    '''
    return {
        "name" : "",
        "degrees" : "",
        "email" : "",
        "location" : "",
        "link" : "",
    }

@handle_element_error
def get_element(element_or_driver, seconds:int, expected_condition, by_search, name:str, desc="element"):
    '''element_or_driver - main WebDriver object used to browse or the element you are searching from
        by_search - the By object corresponding to the category of element you seek
        name - whatever id,.class, xpath is need for that element
        desc - something helpful for determining what failed...
    '''
    # this returns a tuple in case we need to preserve "desc" for future use
    return WebDriverWait(element_or_driver, seconds).until( expected_condition((by_search, name))), desc

    
def scrape(query_start, college="harvard college", filename="alumni_emails.csv"):
    '''
    Goes through the directory page by page and gets all available emails (as well as all 
    without listed emails but with contact ability.)

    Args:
    query_range: a list with all pages to hit. This number corresponds to the startRow list in the URL.
    '''
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://community.alumni.harvard.edu")

    # resetting cookies: uncomment line below (line 29) and comment out following instructions on line 31 
    # input("Hold to save stuff to disk")
    # pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

    #if you need to reset cookies, comment out chunk: line starting below with 'cookies' (#32) until line 76 (right before 'driver.close()')
    # once you double checked cookies.pkl is no longer empty, uncomment the chunk and comment out line 29 then re run script! 
    cookies=pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
  
    alumni_file = open(filename, "a+", newline='')
    alumni_writer = csv.DictWriter(alumni_file, fieldnames=["name", "degrees", "email", "location", "link"])
    alumni_writer.writeheader()

    # modify query mapping to get the query you want
    query_mapping = {
                "college" : college,
                "limit" : "50",
                "sortBy" : "classyear",
                "deceasedFlag" : "true"
    }

    alumni_batch = []

    try:
        print(f"Scraping from page starting at {query_start}")
        query_mapping["startRow"] = query_start
        params = "/query?" + urlencode(query_mapping)   
        driver.get("https://community.alumni.harvard.edu" + params)
            
        card_xpath = "//*[@class='col-xs-20 visible-xs-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block outer-person-card']"
        cards = get_element(driver, 2, EC.visibility_of_all_elements_located, By.XPATH, card_xpath, desc="profile_cards")
            
        # print(len(cards)) # debug purposes
        for card in cards:
            alumnus = new_alumnus()
            # keeps track of this person's position in the search parameters
            anchor = get_element(card, 10, EC.element_to_be_clickable, By.TAG_NAME, "a", desc="user link")
            if anchor:
                alumnus["name"] = anchor.text
                alumnus["link"] = anchor.get_attribute("href")

            degrees = get_element(card, 10, EC.element_to_be_clickable, By.CLASS_NAME, "card__degrees", desc="degrees")
            if degrees:
                alumnus["degrees"] = ",".join(degrees.text.split("\n")) 

            location = get_element(card, 5, EC.element_to_be_clickable, By.CLASS_NAME, "current-location", desc="location")
            if location:
                alumnus["location"] = location.text

            open_button = get_element(card, 5, EC.element_to_be_clickable, By.CLASS_NAME, "buttons", desc="email_button")
            if open_button:  
                open_button.click()

                modal = get_element(driver, 20, EC.element_to_be_clickable, By.CLASS_NAME, "modal", desc="form")
                close_button = get_element(driver, 20, EC.element_to_be_clickable, By.CLASS_NAME, "close", desc="close_button")
                    
                text = None
                if modal:
                    text = modal.find_element_by_tag_name("dd").text.split('<')

                if close_button:
                    close_button.click()

                if text:
                    if len(text) == 2:
                        email = text[1].strip(">").strip()
                        alumnus["email"] = email

            alumni_batch.append( alumnus )
            print(f"{len(alumni_batch)}/50 Alumni in batch starting at {query_start} in college \"{college}\": parameters visible", [i for i in alumnus if alumnus[i] != ""])
    except UnexpectedAlertPresentException:
        print("Session might be logged out. Try resaving cookies and start script again.")
        driver.close()
    
    
    driver.close()
    print(f"Writing {len(alumni_batch)} to disk!")
    for row in alumni_batch:
        alumni_writer.writerow(row)
        alumni_batch = []
    
        
    alumni_file.close()
    

parser = argparse.ArgumentParser(description='Determine specifics of how to run the script.')
parser.add_argument('-f', '--filename', type=str, help='File name of CSV to save to', default="alumni.csv")
parser.add_argument('-c', '--college', type=str, help='Query tab to end at. Is inclusive', default="harvard college")
parser.add_argument("query_start", type=int, help='Query tab to start at')

if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    scrape(args.query_start, college=args.college, filename=args.filename)
    

    
