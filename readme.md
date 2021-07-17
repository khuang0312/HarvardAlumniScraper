# Harvard Alumni Directory Scraper
## Summary
During my time working for Harvard Forward (2021 season), a nonprofit seeking to elect progressive alumni to the Harvard Board of Overseers, I was provided an existing scraper to tweak. I ended up doing a massive overhaul of the scraper.

The scraper probably won't work anymore if they have done any restructuring of site elements. However, I think the code is an good example of using Selenium to gather data from a website. I was able to scrape hundreds of pages containing over 96,000 alumni using this program.

## Setup
* Set up a venv (virtual environment) using Python 3.8.
* Use the requirements.txt to get the necessary dependencies.
* To get a new cookies.pkl in order to keep the scraper from being forced to log out, uncomment lines 84 to 87 in scraper.py, then run scraper.py. Log in with an Harvard alumni's account.
* The number in this example command tells you the "query tab" you start at. Refer to URLs of the directory search result pages to get an idea.<br/>
  `python scraper.py -f "target.csv" -c "harvard college" 0`
* bat_maker.py has a list of available codes you can use. bat_maker.py is used to generate batch scripts for automating the running of scraper.py. 
* The output CSVs of scraper.py should have name, degrees, email, location, links.

## Reflections
This scraper definitely could benefit from some multithreading. There were so many pages that I had to had multiple terminal running multiple instances of this scraper. There might have been a way to not use Selenium as well. At least to some extent.

## What I Learned
* Selenium
* Web scraping (website security measures like CSRF)
* Basic batch scripting (Windows)
* Using a decorator for error handling (Python)
