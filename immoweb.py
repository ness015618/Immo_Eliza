import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Function to extract JSON data from the provided string
def extract_json_from_function(data):
    # Find and extract JSON data within the function call
    start_index = data.find('{')
    end_index = data.rfind('}') + 1
    json_data = data[start_index:end_index]

    # Remove backslashes from the extracted JSON data
    clean_json_data = json_data.replace('\\/', '/')
    clean_json_data = clean_json_data.replace('"true"', 'true')


    return clean_json_data

def get_data_region(session,url,dataset_from_site):

    content = session.get(url).text  
# Parsing the HTML 
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all("div",class_="card--result__body")
    
    for div in divs:
        a_tag = div.find("a")
 
        click = a_tag.get('@click')
        #print("CLIK --->", click)  # Debugging: Print the href attribute
        #print("A attribute:", a_tag)  # Debugging: Print the href attribute
        #print(a_tag)
        #break
        
        if click.strip():
            try:
                # print("i======",i)
                extracted_json = extract_json_from_function(click)
            # Parse the extracted JSON data
                click_json = json.loads(extracted_json)
                
                # print("---------DATA-------")
                
                #print(click_json)
                # print("id",click_json.get('id'))
                
                pr = click_json.get('property')
                type = pr['type']
                # print("property type -----",type)
                
                bedroomCount = pr['bedroomCount']
                # print("property bedroomCount -----",bedroomCount)
                
                
                district = pr['location']['district']
                # print ("Location ---", district)
               
                sqm = pr['netHabitableSurface']
                # print("sqm -----",sqm)
                
                price = click_json.get('price')
                if type != "APARTMENT_GROUP":
                    price = price['mainValue']
                else:
                    pr1 = price['minRangeValue']
                    pr2 = price['maxRangeValue']
                    price = (pr1+pr2)/2
                # print(type.find("GROUP"), type)
                if type.find("GROUP") == -1:
                    dataset_from_site["sqmeter2"].append(sqm)
                    dataset_from_site["type"].append(type)
                    dataset_from_site["price"].append(price)
                    dataset_from_site["district"].append(district)
                    dataset_from_site["bedroomCount"].append(bedroomCount)
                
                # print("price -----",price)
                
                # if type == "APARTMENT_GROUP":
                    # print(json.dumps(click_json, indent=4))
                
                # print("=========DATA=======")
            
            except json.JSONDecodeError as e:
                print("Error: JSON parsing failed -", e)
        else:
            print("Error: Extracted attribute value is empty or contains only whitespace.")

        
    # print("LEN", len(divs))
    return dataset_from_site

def get_data_all():
    
    headers = {
        'User-Agent': 'My Agent',
        'Authorization': 'MyToken'
    }

    dataset_from_site =	{
        "type": [],
        "price": [],
        "bedroomCount":[],
        "sqmeter2": [],
        "district": [],
                        }
    
    citys = ['brussels','antwerp','gent','charleroi','liege','brugge','namur','leuven','mons','mechelen','aalst','hasselt']

    
    session = requests.Session()
    session.headers.update(headers)

    for city in citys:
#loop for getting dataset from one city
        page = 1
        while True:

            main_url="https://www.immoweb.be/en/search/house-and-apartment/for-sale/"+city+"/district?countries=BE&page="+str(page)+"&orderBy=relevance"

            try:
                response = session.get(main_url, verify=True)
                if response.status_code == 200:
                    print("Success: Response code is 200 (OK)")
                    dataset_from_site = get_data_region(session,main_url,dataset_from_site)
                    #print(dataset_from_site)
                    dfs = pd.DataFrame(dataset_from_site)
        # Write the DataFrame to a CSV file
                    dfs.to_csv('data_from_file.csv', index=False, sep=';')
                    # print('read')

                    # Read a CSV file
                    # dfs = pd.read_csv('data_from_file', sep=';')
                    # print(dfs)

                else:
                    print(f"Error: Received response with status code {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
            print (f"City {city}; pages {page}")
            page +=1
            
            # if page >= 3: break
        if city == 'gent': break    
    return

def save(leaders):
    with open("leaders.json", "w") as f:
        json.dump(leaders, f, indent=4)  # Use indent for better readability
    return

def read(leaders):
    try:
        with open("leaders.json", "r") as f:
            leaders = json.load(f)
    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    return leaders




