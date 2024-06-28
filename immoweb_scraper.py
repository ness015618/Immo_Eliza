import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

class ImmowebScraper:
    def __init__(self):
        self.headers = {}
        self.session = requests.Session()
        self.properties = []


    # Functions to get property data
    def get_property_type(self, window_classified_dict):
        return window_classified_dict['property']['type']
    
    def get_property_subtype(self, window_classified_dict):
        return window_classified_dict['property']['subtype']
    
    def get_locality(self, window_classified_dict):
        return window_classified_dict['property']['location'].get('locality', 'None')
    
    def get_price(self, window_classified_dict): # to correct
        if window_classified_dict['transaction']['sale']['price']:
            price = window_classified_dict['transaction']['sale']['price']
        else:
            min_price = window_classified_dict['price']['minRangeValue']
            max_price = window_classified_dict['price']['maxRangeValue']
            price = (min_price + max_price)/2
        return price
    
    def get_sale_type(self, window_classified_dict):
        return window_classified_dict['transaction']['subtype']
    
    def get_bedroom_count(self, window_classified_dict):
        if window_classified_dict['property']['bedroomCount']:
            bedroom_count = window_classified_dict['property']['bedroomCount']
        else:
            bedroom_count = "None"
        return bedroom_count
    
    def get_living_area(self, window_classified_dict):
        if window_classified_dict['property']['netHabitableSurface']:
            living_area = window_classified_dict['property']['netHabitableSurface']
        else:
            living_area = "None"
        return living_area
  
    def get_equipped_kitchen(self, window_classified_dict):
        equipped_kitchen = False
        try:
            if window_classified_dict['property']['kitchen']['type'] == "INSTALLED": # check other options
                equipped_kitchen = True
        except TypeError:
            equipped_kitchen = False
        return equipped_kitchen

    
    def get_is_furnished(self, window_classified_dict):
        is_furnished = False
        if window_classified_dict['transaction']['sale']['isFurnished'] == True:
            is_furnished = True
        return is_furnished
    
    def get_open_fire(self, window_classified_dict):
        has_open_fire = False
        if window_classified_dict['property']['fireplaceCount'] or window_classified_dict['property']['fireplaceExists']:
            has_open_fire = True
        return has_open_fire
    
    def get_terrace(self, window_classified_dict):
        has_terrace = False
        if window_classified_dict['property']['hasTerrace'] == True:
            has_terrace = True
        return has_terrace
    
    def get_terrace_area(self, window_classified_dict):
        terrace_area = 0
        if window_classified_dict['property']['hasTerrace'] == True:
            if window_classified_dict['property']['terraceSurface']:
                terrace_area = window_classified_dict['property']['terraceSurface']
            else:
                terrace_area = "None"
        return terrace_area
    
    def get_garden(self, window_classified_dict):
        has_garden = False
        if window_classified_dict['property']['hasGarden'] == True:
            has_garden = True
        return has_garden
    
    def get_garden_area(self, window_classified_dict):
        garden_area = 0
        if window_classified_dict['property']['hasGarden'] == True:
            garden_area = window_classified_dict['property']['gardenSurface']
        return garden_area
    
    def get_plot_surface(self, window_classified_dict):
        try: 
            plot_surface = window_classified_dict['property']['land']['surface']
        except TypeError:
            plot_surface = "None"
        return plot_surface
    
    def get_nb_facades(self, window_classified_dict):
        try : 
            if window_classified_dict['property']['building']['facadeCount']:
                nb_facades = window_classified_dict['property']['building']['facadeCount']
            else:
                nb_facades = "None"
        except TypeError:
            nb_facades = "None"
        return nb_facades

    def get_swimming_pool(self, window_classified_dict):
        has_swimming_pool = False
        if window_classified_dict['property']['hasSwimmingPool'] == True:
            has_swimming_pool = True
        return has_swimming_pool
    
    def get_building_state(self, window_classified_dict):
        try : 
            condition = window_classified_dict['property']['building']['condition']
        except TypeError:
             condition = "None"
        return condition

    def extract_json_from_function(self, data):
        """
        Put data into usable json
        """
        start_index = data.find('{')
        end_index = data.rfind('}') + 1
        json_data = data[start_index:end_index]
        clean_json_data = json_data.replace('\\/', '/').replace('"true"', 'true')
        return clean_json_data



    def get_property_data(self, window_classified_dict):
        """
        Get the actual data from the house
        """
        property_dataset = {
            "property_type": self.get_property_type(window_classified_dict),
            "property_subtype": self.get_property_subtype(window_classified_dict),
            "locality": self.get_locality(window_classified_dict),
            "price": self.get_price(window_classified_dict),
            "sale_type": self.get_sale_type(window_classified_dict),
            "bedroom_count": self.get_bedroom_count(window_classified_dict),
            "living_area": self.get_living_area(window_classified_dict),
            "equipped_kitchen": self.get_equipped_kitchen(window_classified_dict),
            "is_furnished": self.get_is_furnished(window_classified_dict),
            "has_open_fire": self.get_open_fire(window_classified_dict),
            "has_terrace": self.get_terrace(window_classified_dict),
            "terrace_area": self.get_terrace_area(window_classified_dict),
            "has_garden": self.get_garden(window_classified_dict),
            "garden_area": self.get_garden_area(window_classified_dict),
            "plot_surface": self.get_plot_surface(window_classified_dict),
            "nb_facades": self.get_nb_facades(window_classified_dict),
            "has_swimming_pool": self.get_swimming_pool(window_classified_dict),
            "building_state": self.get_building_state(window_classified_dict)
        }
        return property_dataset
        

    def get_data_from_page(self, url):
        """
        Was used to get data from click, but we need to change to take urls from research page
        call parse_property
        """
        content = self.session.get(url).text
        soup = BeautifulSoup(content, 'html.parser')

        divs = soup.find_all("div", class_="card--result__body")
        
        for div in divs:
            a_tag = div.find("a")
            click = a_tag.get('@click')
            
            

            if click.strip():
                try:
                    extracted_json = self.extract_json_from_function(click)
                    property_json = json.loads(extracted_json)
                    self.parse_property(property_json)
                except json.JSONDecodeError as e:
                    print("organize file failed -", e)

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

    def find_window_classified(self, property_url):
        response = self.session.get(property_url, headers=self.headers)
        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            window_classified = soup.find("script",type="text/javascript").text
            clean_window_classified = self.extract_json_from_function(window_classified)
            window_classified_dict = json.loads(clean_window_classified)
        return window_classified_dict
    
    def scrape(self):
        """ 
        We start with this
        call get_data_from_page
        """
        
        self.headers = {
        'User-Agent': 'My Agent',
        'Authorization': 'MyToken'
        }
        
        self.session.headers.update(self.headers)
        
        #url = "https://www.immoweb.be/en/classified/house/for-sale/nassogne/6950/11485698"
        #url = "https://www.immoweb.be/en/classified/apartment/for-sale/lier/2500/20000906"
        page = 1
        base_url = f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={page}&orderBy=relevance"
        for page in range(1,334):
            page_url = base_url.format(page)
            try:
                response = self.session.get(page_url)
                if response.status_code == 200:
                    property_urls = self.get_property_urls(page_url)
                    #print(property_urls, len(property_urls)) # Debugging
                    for property_url in property_urls:
                        window_classified_dict = self.find_window_classified(property_url)
                        #print(json.dumps(window_classified_dict, indent=4)) # Debugging
                        property_dataset = self.get_property_data(window_classified_dict)
                        self.properties.append(property_dataset)
                        #print(property_dataset) # Debugging
                    print(f"Page {page} processed successfully.")    
                else:
                    print(f"Error with status code {response.status_code} on page {page}.")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request error on page {page}: {e}")    
        
        df = pd.DataFrame(self.properties)
        df.to_csv('immoweb_data.csv', index=False, sep=';')
                        
        #print(property_urls, len(property_urls)) # Dubugging
        #window_classified = soup.find("script",type="text/javascript").text
        
        #clean_window_classified = self.extract_json_from_function(window_classified)
        #print(clean_window_classified) # Debugging
        #window_classified_dict = json.loads(clean_window_classified)
        #print("window_classified_dict WITH COMFORTABLE VIEW : \n", json.dumps(window_classified_dict, indent=4)) # Debugging
        #property_dataset = self.get_property_data(window_classified_dict)
        #print(property_dataset)
        
        """
        base_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&priceType=SALE_PRICE&page=1&orderBy=relevance{}'
        
        for page in range(1, self.pages + 1):
            page_url = base_url.format(page)
            try:
                response = self.session.get(page_url)
                if response.status_code == 200:
                    self.get_data_from_page(page_url)
                    print(f"successsful and {response.status_code}: {page}")
                else:
                    print(f"error and status code {response.status_code}: {page}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
        
        df = pd.DataFrame(self.dataset)
        df.to_csv('data_from_file.csv', index=False, sep=';')
        """
        
        
# Ides for get_links
"""
import requests 
from bs4 import BeautifulSoup

url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=1&orderBy=relevance"
headers = {
    'User-Agent': 'myuser',
    'Authorization': 'myusers'
}



content = requests.get(url).text
soup = BeautifulSoup(content, 'html.parser')
propertyurls = []

divs = soup.find_all("div", class="card--result__body")
for div in divs:
    a_tag = div.find("a", href=True)
    if a_tag:
        print(a_tag)
        property_url = 'https://www.immoweb.be/' + a_tag['href']
        print(property_url)
        property_urls.append(property_url)

print(property_urls)
"""