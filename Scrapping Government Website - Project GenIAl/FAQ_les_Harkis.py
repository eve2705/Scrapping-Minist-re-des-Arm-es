import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://harkis.gouv.fr/foire-aux-questions'

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

soup = get_soup(url)

def get_title(soup):
    title_elements = soup.find_all('p', class_='fr-header__service-title')
    title = [t.get_text(strip=True) for t in title_elements]
    return title

title = get_title(soup)

def get_questions(soup):
    question_elements = soup.find_all('button', class_='fr-accordion__btn')
    questions = [q.get_text(strip=True) for q in question_elements]
    # print(questions)
    return questions

questions = get_questions(soup)

def get_answers(soup):
    answers_elements = soup.find_all('div', class_='fr-prose')
    answers = [a.get_text(strip=True) for a in answers_elements]
    # print(answers)
    return answers[1:]

answers = get_answers(soup)

dataframes = []

if len(questions) == len(answers):
    for question, answer in zip(questions, answers):
        df = pd.DataFrame({'URL': [url],'Title': [title], 'Question': [question], 'Réponse': [answer]})
        dataframes.append(df)
else:
    print(f"Mismatch in number of questions ({len(questions)}) and answers ({len(answers)}) for URL: {url}")

if dataframes:
    df = pd.concat(dataframes, ignore_index=True)
    print(df)
    # csv_file_path = 'FAQ_Les_Harkis.csv'
   

