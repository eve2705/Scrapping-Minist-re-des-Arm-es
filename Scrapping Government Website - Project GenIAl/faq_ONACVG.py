from bs4 import BeautifulSoup
# import requests as req
# import re   
# import os
# import selenium
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
# import sys
import pandas as pd


dict_of_urls = {'https://maison-des-blesses.defense.gouv.fr/faq/militaire/armee-terre': 0, 'https://maison-des-blesses.defense.gouv.fr/faq/militaire/marine-nationale': 0, 'https://maison-des-blesses.defense.gouv.fr/faq/militaire/armee-lair-lespace': 0, 'https://maison-des-blesses.defense.gouv.fr/faq/militaire/gendarmerie-nationale': 0, 'https://maison-des-blesses.defense.gouv.fr/faq/militaire/service-sante-armees': 0, 'https://maison-des-blesses.defense.gouv.fr/faq/militaire/organismes-interarmees-autres': 0}

#Open web browser + deny cookies
def get_soup(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    # cookie_button = driver.find_element(By.XPATH, '//*[@id="tarteaucitronAllDenied2"]') #deny all cookies
    # cookie_button.click()
    # time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# soup = get_soup(url)

#Retrieve questions
def get_question(soup):
    # soup = get_soup(url)
    question_elements = soup.find_all('button', class_ = 'fr-accordion__btn')
    questions = [q.get_text(strip=True) for q in question_elements if q.get_text(strip=True).endswith('?')] #remove unwanted tags - only question
    return questions

# questions = get_question(soup)

# # Print each question 
# for question in questions:
#     print(question)

#Retrieve answers 
def get_answers(soup):
    # soup = get_soup(url)
    answers_elements = soup.find_all('div', class_ = 'fr-richtext')
    answers = [a.get_text(strip=True) for a in answers_elements] #remove unwanted tags - only answers
    return answers

# answers = get_answers(soup)

# # Print each answer 
# for answer in answers:
#     print(answer)


dataframes = []


for url, nb in dict_of_urls.items():
    soup = get_soup(url)
    questions = get_question(soup)
    answers = get_answers(soup)

    if len(questions) == len(answers):
        for question, answer in zip(questions, answers):        
            df = pd.DataFrame({'Question': [question], 'Réponse': [answer], 'URL': [url]})                
            dataframes.append(df)

    else:
        print(f"Mismatch in number of questions ({len(questions)}) and answers ({len(answers)}) for URL: {url}")

# Concatenate all the dataframes
if dataframes:
    df = pd.concat(dataframes, ignore_index=True)
    df
else:
    print("No dataframes to concatenate.")

# #Printing in database
# dataframes = []

# # Create DataFrame only if the number of questions and answers match
# if len(questions) == len(answers):
#     for question, answer in zip(questions, answers):
#         df = pd.DataFrame({'Question': [question], 'Réponse': [answer]})
#         dataframes.append(df)
#     else:
#         print(f"Mismatch in number of questions and answers for URL: {url}")

# # Concatenate all the dataframes
# df = pd.concat(dataframes, ignore_index=True)

#Export to csv file 
csv_file_path = 'faq_ONACVG_type2.csv'
df.to_csv(csv_file_path, index=False)  

print(f"Data exported successfully to {csv_file_path}")















