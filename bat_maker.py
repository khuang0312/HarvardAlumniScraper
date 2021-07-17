# Kevin Huang
# Last modified: 4/2/2021

# This file is made for the sole purpose of creating batch files to call the scraper
# This goes in intervals of 50 mainly because that's the highest interval the site supports

# Because of the amount of alumni, making the commands by hand would be very cumbersome.
# Having larger intervals might also result in data lost because of the potential of things
# going wrong.

from sys import argv

def make_batch_commands(batch_file, filename:str, school:str, start=0, end=50):
    '''Automates the creation of batch files containing the calls to scrape
    '''    
    batch = 1
    for i in range(start, end + 1, 50):
        batch_file.write( f"python scrape.py -f \"{filename}{batch}.csv\" -c \"{school}\" {i}\n"  )
        batch += 1

if __name__ == '__main__':
    # schools maps the names of each graduate school to the numbers of start page and the final page
    # the way the directory is organized that each result page at most stores 50 alumni
    # the url is organized like ?start=0, meaning that students 0 to 50 are on that page

    # the starting numbers are picked because we found that the alumni at the time we scraped
    # start on different pages depending on the school.
    schools = {
        "general" : ["general_alumni", "harvard college", 0, 96800],
        "kennedy" : ["kennedy", "harvard kennedy school", 1050, 41500],
        "education" : ["education", "graduate school of education", 1250, 32200],
        "public_health" : ["public_health", "harvard t.h. chan school of public health", 1050, 19450],
        "business" : ["business", "harvard business school", 1800, 89950],
        "gsas" : ["gsas", "graduate school of arts and sciences", 4950, 46800],
        "law" : ["law", "harvard law school", 2200, 45950],
        "extension" : ["extension", "harvard extension school", 0, 20950],
        "medical_and_dental" : ["medical_and_dental", "harvard school of dental medicine,harvard medical school", 1600, 18550],
        "design" : ["design", "graduate school of design", 1000, 14450],
        "divinity" : ["divnity","harvard divinity school", 400, 8500]
    }
    
    school_name = input("Select school by key: ")

    if school_name in schools:
        filename = f"{school_name}_sheets.bat"
            
        with open(filename, 'w') as batch_file:
            params = schools[school_name]
            make_batch_commands(batch_file, params[0], params[1], params[2], params[3])
    else:
        print("Not a valid school! Try again!")