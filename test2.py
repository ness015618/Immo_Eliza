import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def extract_json_from_function(data):
    start_index = data.find('{')
    end_index = data.rfind('}') + 1
    json_data = data[start_index:end_index]

    clean_json_data = json_data.replace('\\/', '/')
    clean_json_data = clean_json_data.replace('"true"', 'true') # string to bool

    return clean_json_data


# The functions I wrote
class Scraper:
    
    # other stuff by Mustafa
    
    def __init__(self):
        self.property_type = ""
        self.property_subtype = ""
        self.locality = ""
        self.price = 0
        self.sale_type = ""
        self.bedroom_count = 0
        self.living_area = 0
        self.equipped_kitchen = False
        self.is_furnished = False
        self.has_open_fire = False
        self.has_terrace = False
        self.terrace_area = 0
        self.has_garden = False
        self.garden_area = 0
        self.plot_surface = 0
        self.nb_facades = 0
        self.has_swimming_pool = False
        self.building_state = ""
    
    def get_property_type(self, window_classified_dict):
        self.property_type = window_classified_dict['property']['type']
        return self.property_type
    
    def get_property_subtype(self, window_classified_dict):
        self.property_subtype = window_classified_dict['property']['subtype']
        return self.property_subtype
    
    def get_sale_type(self, window_classified_dict):
        self.sale_type = window_classified_dict['transaction']['subtype']
        return self.sale_type
    
    def get_bedroom_count(self, window_classified_dict):
        self.bedroom_count = window_classified_dict['property']['bedroomCount']
        return self.bedroom_count
    
    def get_living_area(self, window_classified_dict):
        self.living_area = window_classified_dict['property']['netHabitableSurface']
        return self.living_area
  
    def get_equipped_kitchen(self, window_classified_dict):
        if window_classified_dict['property']['kitchen']['type'] == "INSTALLED": # !!!!! verify other options
            self.equipped_kitchen = True
        return self.equipped_kitchen
    
    def get_is_furnished(self, window_classified_dict):
        if window_classified_dict['transaction']['sale']['isFurnished'] == True:
            self.is_furnished = True
        return self.is_furnished
    
    def get_open_fire(self, window_classified_dict):
        if window_classified_dict['property']['fireplaceCount'] or window_classified_dict['property']['fireplaceExists']:
            self.has_open_fire = True
        return self.has_open_fire



headers = {
        'User-Agent': 'My Agent',
        'Authorization': 'MyToken'
    }

session = requests.Session()
session.headers.update(headers)
#url = "https://www.immoweb.be/en/classified/apartment/for-sale/lier/2500/20000906"
url = "https://www.immoweb.be/en/classified/house/for-sale/nassogne/6950/11485698"
content = session.get(url).text
# Parsing the HTML 
soup = BeautifulSoup(content, 'html.parser')
window_classified = soup.find("script",type="text/javascript").text
#print(window_classified)
clean_window_classified = extract_json_from_function(window_classified)
#print(clean_window_classified)
window_classified_dict = json.loads(clean_window_classified)
print("window_classified_dict WITH COMFORTABLE VIEW : \n", json.dumps(window_classified_dict, indent=4))


# Testing the functions
my_scraper = Scraper()
print(my_scraper.get_property_type(window_classified_dict))
print(my_scraper.get_property_subtype(window_classified_dict))
print(my_scraper.get_sale_type(window_classified_dict))
print(my_scraper.get_bedroom_count(window_classified_dict))
print(my_scraper.get_living_area(window_classified_dict))
print(my_scraper.get_equipped_kitchen(window_classified_dict))
print(my_scraper.get_is_furnished(window_classified_dict))
print(my_scraper.get_open_fire(window_classified_dict))