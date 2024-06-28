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


class ImmowebScraper:


    def parse_property(self, property_json):
        pr = property_json.get('property')
        type = pr['type']
        bedroomCount = pr['bedroomCount']
        district = pr['location']['district']
        sqm = pr['netHabitableSurface']
        price_info = property_json.get('price')
        
        if type != "APARTMENT_GROUP":
            price = price_info['mainValue']
        else:
            pr1 = price_info['minRangeValue']
            pr2 = price_info['maxRangeValue']
            price = (pr1 + pr2) / 2
        
        if type.find("GROUP") == -1:
            self.dataset["sqmeter2"].append(sqm)
            self.dataset["type"].append(type)
            self.dataset["price"].append(price)
            self.dataset["district"].append(district)
            self.dataset["bedroomCount"].append(bedroomCount)

    def find_classified_script(self, url):
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            scripts = soup.find_all('script')

            needed_script = None
            for script in scripts:
                if 'window.classified =' in script.text:
                    needed_script = script
                    break
            
            if needed_script:
                start_index = needed_script.text.find('{')
                end_index = needed_script.text.rfind('}') + 1
                json_data = needed_script.text[start_index:end_index]
                clean_json_data = json_data.replace('\\/', '/').replace('"true"', 'true')
                return json.loads(clean_json_data)
        
        return None

    def scrape(self):
        base_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&priceType=SALE_PRICE&page={}'
        
        for page in range(1, self.pages + 1):
            page_url = base_url.format(page)
            try:
                response = self.session.get(page_url)
                if response.status_code == 200:
                    property_urls = self.get_property_urls(page_url)
                    for property_url in property_urls:
                        property_json = self.find_classified_script(property_url)
                        if property_json:
                            self.parse_property(property_json)
                    print(f"Page {page} processed successfully.")
                else:
                    print(f"Error with status code {response.status_code} on page {page}.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request error on page {page}: {e}")
        
        df = pd.DataFrame(self.dataset)
        df.to_csv('data_from_file.csv', index=False, sep=';')

    def get_property_urls(self, url):
        content = self.session.get(url, headers=self.headers).text
        soup = BeautifulSoup(content, 'html.parser')
        property_urls = []
        
        results = soup.find_all('div', class_='card--result__body')
        for result in results:
            link = result.find('a', href=True)
            if link:
                property_url = link['href']
                property_urls.append(property_url)
        
        return property_urls

# Usage
if __name__ == "__main__":
    headers = {
        'User-Agent': 'myuser',
    }
    pages = 1  

    scraper = ImmowebScraper(headers, pages)
    scraper.scrape()
    print("Data saved to data_from_file.csv")