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


def scrape(query_range, college="harvard college", filename="alumni_emails.csv"):
    '''
    Goes through the directory page by page and gets all available emails (as well as all 
    without listed emails but with contact ability.)

    Args:
    query_range: a list with all pages to hit. This number corresponds to the startRow list in the URL.
    '''
    last_person = query_range[-1] + 50
    

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://community.alumni.harvard.edu")

    # resetting cookies: uncomment line below (line 29) and comment out following instructions on line 31 
    # pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

    #if you need to reset cookies, comment out chunk: line starting below with 'cookies' (#32) until line 76 (right before 'driver.close()')
    #once you double checked cookies.pkl is no longer empty, uncomment the chunk and comment out line 29 then re run script! 
    cookies=pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    '''
    error_file = open('error_tabs', 'a+', newline='')
    error_writer = csv.writer(error_file)

    no_email_file = open('no-emails.csv', 'a+', newline='')
    # no_email_writer should be no_email_file
    no_email_writer = csv.writer(no_email_file)

    email_file = open('emails.csv', 'a+', newline='')
    email_writer = csv.writer(email_file)
    '''
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
    alumni_covered = 1

    for query_num in query_range:
        try:
            print("Scraping from page row {:>10}".format(query_num))
            query_mapping["startRow"] = query_num
            params = "/query?" + urlencode(query_mapping)   
            driver.get("https://community.alumni.harvard.edu" + params)
            
            cards = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(
                (By.XPATH, 
                "//*[@class='col-xs-20 visible-xs-block visible-sm-inline-block visible-md-inline-block visible-lg-inline-block outer-person-card']"
                )))

            # print(len(cards)) # debug purposes
            
            for card in cards:
                error = "" # for debugging
                
                alumnus = {
                    "name" : "",
                    "degrees" : "",
                    "email" : "",
                    "location" : "",
                    "link" : "",
                }

                # might wrap some of the error catching in order to make it more concise...
                try:
                    anchor = WebDriverWait(card, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
                    alumnus["name"] = anchor.text
                    alumnus["link"] = anchor.get_attribute("href")

                    degrees = WebDriverWait(card, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "card__degrees")))
                    
                    
                    alumnus["degrees"] = ";".join(degrees.text.split("\n")) 
                    
                    location = WebDriverWait(card, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "current-location")))
                    alumnus["location"] = location.text #location

                    open_button = WebDriverWait(card, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "buttons")))
                    open_button.click()

                    modal = None 
                    email = None
                    close_button = None

                    modal = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "modal")))
                    close_button = WebDriverWait(modal, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "close")))
                    text = modal.find_element_by_tag_name("dd").text.split('<')
                   
                    close_button.click()

                    if len(text) == 2:
                        email = text[1].strip(">").strip()
                        alumnus["email"] = email
                except TimeoutException:
                    error += "element took too long, "
                except ElementClickInterceptedException:
                    error += "something blocks element"
                except ElementNotInteractableException:
                    error += "element doesn't seem to work"
                finally:

                
                if error != "":
                    error += str(alumnus)

                alumni_batch.append( alumnus )
                print(f"Alumni {alumni_covered}/{last_person} in college {college}:", error)
                alumni_covered += 1

            if getsizeof(alumni_batch) > 100000:
                print(f"Writing {len(alumni_batch)} to disk!")
                for row in alumni_batch:
                    alumni_writer.writerow(row)
                    alumni_batch = []
        
        except UnexpectedAlertPresentException:
            print(
                "Session might be logged out. Try resaving cookies and start script again.")
            driver.close()
            break
    
    driver.close()

    for row in alumni_batch:
        print(f"Writing {len(alumni_batch)} to disk!")
        alumni_writer.writerow(row)
        alumni_batch = []
        
    alumni_file.close()
    
    
    

 


parser = argparse.ArgumentParser(description='Determine specifics of how to run the script.')
parser.add_argument('-f', '--filename', type=str, help='File name of CSV to save to')
parser.add_argument('-c', '--college', type=str, help='Query tab to end at')
parser.add_argument("query_start", type=str, help='Query tab to start at')
parser.add_argument("query_end", type=str, help='Query tab to end at')



if __name__ == "__main__":

    args = parser.parse_args()
    print(args)
    scrape(range(int(args.query_start), int(args.query_end) + 1, 50), college=args.college, filename=args.filename)
    

    
