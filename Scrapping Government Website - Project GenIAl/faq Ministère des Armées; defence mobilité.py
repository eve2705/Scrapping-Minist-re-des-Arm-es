from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


url = 'https://www.defense.gouv.fr/defense-mobilite/besoin-daide/faq'

#Open web browser + deny cookies
def get_soup(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    cookie_button = driver.find_element(By.XPATH, '//*[@id="tarteaucitronAllDenied2"]') #deny all cookies
    cookie_button.click()
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

soup = get_soup(url)

#Retrieve questions
def get_question(soup):
    soup = get_soup(url)
    question_elements = soup.find_all('button', class_ = 'fr-accordion__btn')
    questions = [q.get_text(strip=True) for q in question_elements] #remove unwanted tags - only question
    return questions

questions = get_question(soup)

# # Print each question 
# for question in questions:
#     print(question)

#Retrieve answers 
def get_answers(soup):
    soup = get_soup(url)
    answers_elements = soup.find_all('div', class_ = 'fr-richtext fr-container')
    answers = [a.get_text(strip=True) for a in answers_elements] #remove unwanted tags - only answers
    return answers

answers = get_answers(soup)

# # Print each answer 
# for answer in answers:
#     print(answer)

#Printing in database
dataframes = []


# Create DataFrame only if the number of questions and answers match
if len(questions) == len(answers):
    for question, answer in zip(questions, answers):
        df = pd.DataFrame({'Question': [question], 'Réponse': [answer]})
        dataframes.append(df)
    else:
        print(f"Mismatch in number of questions and answers for URL: {url}")

# Concatenate all the dataframes
df = pd.concat(dataframes, ignore_index=True)

#Export to csv file 
csv_file_path = 'faq_scrap.csv'
df.to_csv(csv_file_path, index=False)  

print(f"Data exported successfully to {csv_file_path}")
print("Rabeau, G., Raliterason, R. and Rein, C. (2024) Hackathon_2024/SCRAPING_QUORA.ipynb at main ·\n Waxguillermo/hackathon_2024, GitHub. Available at:\n https://github.com/Waxguillermo/HACKATHON_2024/blob/main/scraping_quora.ipynb (Accessed: 07 May 2024). ")