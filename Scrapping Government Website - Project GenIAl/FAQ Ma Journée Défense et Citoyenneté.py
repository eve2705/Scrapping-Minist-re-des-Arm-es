from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

url = 'https://presaje.sga.defense.gouv.fr/faq'

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
    driver.quit()
    return soup

soup = get_soup(url)

#Get title
def get_title(soup):
    title_elements = soup.find_all('div', class_='fr-col-12 fr-col-lg-12 fr-p-1w fr-col-md-4')
    title = [t.get_text(strip=True) for t in title_elements]
    return title

title = get_title(soup)

#Retrieve questions
def get_question(soup):
    question_elements = soup.find_all('div')
    questions = [q.get_text(strip=True) for q in question_elements if q.get_text(strip=True).endswith('?')]#remove unwanted tags - only question
    return questions

questions = get_question(soup)

def get_answers(soup):
    question_elements = soup.find_all('div')  # Finds all <div> elements, assuming questions are in <div>
    answers = []  # List to hold all found answers
    
    for question_element in question_elements:
        if question_element.get_text(strip=True).endswith('?'):
            # Find the next sibling element that is expected to contain the answer
            answer_element = question_element.find_next('div')  # Assuming the answer is in the next <p> tag
            if answer_element:
                # Add the text of the answer to the list
                answers.append(answer_element.get_text(strip=True))
    
    return answers

answers = get_answers(soup)

#Printing in database
dataframes = []

# Create DataFrame only if the number of questions and answers match
if len(questions) == len(answers):
    for question, answer in zip(questions, answers):
        df = pd.DataFrame({'URL': [url], 'Title': [title], 'Question': [question], 'Réponse': [answer]})
        dataframes.append(df)
    else:
        print(f"Mismatch in number of questions and answers for URL: {url}")

# Concatenate all the dataframes
df = pd.concat(dataframes, ignore_index=True)
print(df)

#Export to csv file 
csv_file_path = 'e.csv'
df.to_csv(csv_file_path, index=False)  

print(f"Data exported successfully to {csv_file_path}")











