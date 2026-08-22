import csv 
import json
import xml.etree.ElementTree as ET
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

logging.info('Starting logging')

def read_and_filter_csv(path: str) -> list[dict[str, str]]:
    people = []
    with open(path, 'r') as file:
        delimeter = csv.DictReader(file, delimiter=';')
        with open('clean_usernames.csv', 'w', newline='') as newfile:
            fieldnames = ['username', 'first_name']
            writer = csv.DictWriter(newfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in delimeter:
                if not (row['Username']):
                    logging.warning(f"Skipping row, missing Username: {row}")
                    continue
                if not (row['First name']):
                    continue
                writer.writerow({'username': row['Username'], 'first_name': row['First name']})
                people.append({'username': row['Username'], 'first_name': row['First name']})
    return people

people = read_and_filter_csv('username.csv')


with open('usernames.json','w') as jsonfile:
    json.dump(people, jsonfile, indent=2)
with open('usernames.json','r') as jsonfile:
    people = json.load(jsonfile)
with open('xml_exam.xml','r') as xmlfile:
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for element in root:
        logging.info(f"Attributes: {element.attrib['id']}")
        logging.info(f"Title: {element.find('title').text}")
        logging.info(f"Price: {element.find('price').text}")
          # for child in element:
            #     if child.tag == 'title':
            #         print(f"Title: {child.text}")
            #     if child.tag == 'price': 
            #         print(f"Price: {child.text}")  

# File Error Handling
try:
    with open('errorhandling.csv','r') as efile:
        reader = csv.reader(efile)
        for row in reader:
            print(row)
except FileNotFoundError as e:
    logging.error(f"Something went wrong: {e}")
except csv.Error:
    logging.error("Error: Failed to parse the CSV data.")
finally:
    logging.info("This will be always execute")