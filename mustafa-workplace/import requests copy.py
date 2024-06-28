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
                property_url = 'https://www.immoweb.be' + link['href']
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