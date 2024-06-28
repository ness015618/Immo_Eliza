import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

class ImmowebScraper:
    def __init__(self, headers, pages):
        self.headers = headers
        self.pages = pages
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.dataset = {
            "type": [],
            "price": [],
            "bedroomCount": [],
            "sqmeter2": [],
            "district": [],
        }



    def extract_json_from_function(self, data):
        """
        Put data into usable json
        """
        start_index = data.find('{')
        end_index = data.rfind('}') + 1
        json_data = data[start_index:end_index]
        clean_json_data = json_data.replace('\\/', '/').replace('"true"', 'true')
        return clean_json_data



    def parse_property(self, property_json):
        """
        Get the actual data from the house
        """
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



    def scrape(self):
        """ 
        We start with this
        call get_data_from_page
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
        
        
# Ides for get_links
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