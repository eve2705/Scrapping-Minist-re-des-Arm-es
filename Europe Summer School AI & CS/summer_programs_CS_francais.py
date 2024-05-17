import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from timeit import default_timer as timer
from multiprocessing import Pool
from transformers import MarianMTModel, MarianTokenizer

# From Hugging Face --> MarianMT model and tokenizer for English to French translation
model_name = 'Helsinki-NLP/opus-mt-en-fr'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Function to translate text from English to French (or french to french!)
def translate_to_french(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest")
    translated = model.generate(**inputs)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

url = 'https://www.summerschoolsineurope.eu/search/discipline;ComSc'

# Retrieve soup of url
def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    return BeautifulSoup(response.content, 'html.parser')

soup = get_soup(url)

#Get all URLS of the website for the 2024 courses (49 courses in total)
def get_urls(soup):
    base_url = 'https://www.summerschoolsineurope.eu'
    title_elements = soup.find_all('h3')

    urls = []
    url_limit = 61 #number of programs in 2024!

    for title_element in title_elements:
        next_sibling = title_element.find_next()
        if next_sibling and next_sibling.name == 'a':
            full_url = base_url + next_sibling['href']
            urls.append(full_url)
        
        if len(urls) >= url_limit:
            break
        
    return urls

urls = get_urls(soup)

# Clean text to avoid extra spaces + doubles
def clean_text(text):
    # Replace multiple spaces or newlines with a single space
    return re.sub(r'\s+', ' ', text).strip()

# Function to get all info from the page
def get_allInfo(soup):
    # Initialize the dictionary to store the information
    info = {
        'Name of Program': '',
        'Place': [],
        'University': [],
        'When': '',
        'Language': '',
        'Duration': '',
        'Credits': '',
        'Fee': '',
        'Registration deadline': '',
        'Course leader': '',
        'Target group': '',
        'Course aim': '',
        'Fee info': '',
        'Scholarships': '',
        'Credits info': ''
    }

    # NAME
    name_elements = soup.find_all('h1')
    if len(name_elements) > 1:
        info['Name of Program'] = translate_to_french(clean_text(name_elements[1].get_text()))

    # COUNTRY+CITY
    place_elements = soup.find_all('span', class_='location-label')
    info['Place'] = [translate_to_french(p.get_text(strip=True)) for p in place_elements]

    # UNIVERSITY
    university_elements = soup.find_all('h2')
    info['University'] = [translate_to_french(u.get_text(strip=True)) for u in university_elements]

    # General labels processing
    elements = soup.find_all('span', class_='label')
    for element in elements:
        text = element.get_text(strip=True).lower()

        # WHEN
        if 'when' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['When'] = translate_to_french(clean_text(next_element.get_text()))

        # LANGUAGE       
        elif 'language' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['Language'] = translate_to_french(clean_text(next_element.get_text()))

        # DURATION
        elif 'duration' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['Duration'] = translate_to_french(clean_text(next_element.get_text()))

        # CREDITS
        elif 'credits' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['Credits'] = translate_to_french(clean_text(next_element.get_text()))

        # FEE
        elif 'fee' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['Fee'] = translate_to_french(clean_text(next_element.get_text()))

        # REGISTRATION DEADLINE
        elif 'registration deadline' in text:
            next_element = element.find_next_sibling()
            if next_element:
                info['Registration deadline'] = translate_to_french(clean_text(next_element.get_text()))

    # Specific section processing
    sections = soup.find_all('h3')
    for section in sections:
        section_text = section.get_text(strip=True).lower()

        # COURSE LEADER
        if 'course leader' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Course leader'] = translate_to_french(clean_text(next_element.get_text()))

        # TARGET GROUP
        elif 'target group' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Target group'] = translate_to_french(clean_text(next_element.get_text()))

        # COURSE AIM
        elif 'course aim' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Course aim'] = translate_to_french(clean_text(next_element.get_text()))

        # FEE INFO
        elif 'fee info' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Fee info'] = translate_to_french(clean_text(next_element.get_text()))

        # SCHOLARSHIPS
        elif 'scholarships' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Scholarships'] = translate_to_french(clean_text(next_element.get_text()))

        # CREDIT INFO
        elif 'credits info' in section_text:
            next_element = section.find_next_sibling('p')
            if next_element:
                info['Credits info'] = translate_to_french(clean_text(next_element.get_text()))

    # Convert lists to strings for DataFrame
    for key in ['Place', 'University']:
        info[key] = ', '.join(info[key])

    return info

# Initialize a list to hold all the information
all_info = []

# Iterate over the first 49 URLs and extract information
for url in urls:
    page_soup = get_soup(url)
    info = get_allInfo(page_soup)
    all_info.append(info)

# Create a DataFrame from the collected information
df = pd.DataFrame(all_info)
print(df)

# Save the DataFrame to a CSV file
df.to_csv('course_info_CS_francais.csv', index=False)

