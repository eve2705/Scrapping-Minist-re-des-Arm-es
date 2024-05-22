#ce code est prévu pour scrapper les pages ayant un url qui commence par "https://www.service-public.fr/particuliers/vosdroits/F", il en existe plusiseurs centaines suivant ce modèle et étant complétées par un nombre directement après le F
import pandas as pd
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
from timeit import default_timer as timer
import os
import time
import random  

# on a remarqué la présence récurente d'espaces insécables \xa0 que l'on choisit de remplacer par des espaces normaux
def xaout(questions_texte):
    for i in range(len(questions_texte)):
        questions_texte[i] = questions_texte[i].replace('\xa0', ' ')
    return questions_texte

# fonction pour créer un tableau organisé des valeurs que l'on récupère dans un tableau à double entrée de taile n*m codé en html, on aura à la fin une liste de listes avec en première liste les variables en colonnes, en deuxième liste les variables en ligne et ensuite n listes avec les m informations correspondant à la combinaison de deux colonnes
def crea_tab(tab_txt):
    tab = []
    soup = BeautifulSoup(tab_txt, 'html.parser')

    # on extrait les noms des colonnes
    thead = soup.find('thead')
    colonnes = thead.find_all('p')
    colonnes_textes = [colonne.text.strip() for colonne in colonnes[1:]]
    tab.append(colonnes_textes)
    tab.append([])

    # on extrait les lignes
    tbody = soup.find('tbody')
    lignes_brutes = tbody.find_all('tr')
    for ligne in lignes_brutes:
        elements = ligne.find_all('p')
          # on prend les informations de la ligne
        tab.append([element.text.strip() for element in elements[1:]])
          # on prend le nom de la ligne regardée
        tab[1].append(elements[0].text.strip())
    return tab

# fonction qui à partir d'un tableau généré avec la fonction précédente va écrire de manière formulée le titre du tableau, et ensuite ses informations en indiquant d'abord le premier critère puis le deuxième critère et ensuite l'information concernée, et cela pour chaque case du tableau
def generer_combinaisons(tableau):
    combinaisons = ""
    if tableau and len(tableau) >= 3 and all(len(row) >= 2 for row in tableau):
        min_length = min(len(tableau[0]), len(tableau[1]))
        for i in range(2, len(tableau)):
            for j in range(min_length):
                combinaisons += f"{tableau[0][j]} et {tableau[1][i-2]} : {tableau[i][j]}"
                if i != len(tableau) - 1 or j != min_length - 1:
                    combinaisons += ", "
                else:
                    combinaisons += "."
    return combinaisons

# fonction qui analyse chaque élément qu'on lui donne et va réagir en fonction du type de la balise pour prendre l'information ou non
def rec_extract_text(element):
    texte_filtre = ""
    
    if element.name == 'li' or element.name =='p':
        if not element.find('a', class_='fr-btn fr-mb-2w'):
            texte_filtre += " " + element.text.strip()

    elif element.name == 'table':
        caption = element.find('caption')
        texte_filtre+=caption.text.strip() + " : "
        tab = crea_tab(str(element))
        texte_filtre+=generer_combinaisons(tab)

    if hasattr(element, 'children') : #and element.name != 'table' , on peut pas le mettre à cause du manque de normalisation, avec cela on enlèverait des données qui se répètent mais on perdrait des données dans certains cas
        for child in element.children:
            texte_filtre += rec_extract_text(child)
    return texte_filtre

# fonction qui va exporter le dataframe crée pour l'ajouter à la fin d'un document csv donné, si ce document csv n'existe pas on le créera
def export(df, nom_doc):
    try:
        if os.path.isfile(nom_doc):
            df0 = pd.read_csv(nom_doc, on_bad_lines='skip') #skip rows with bad format
            df2 = pd.concat([df0, df], ignore_index=True)
            df2.to_csv(nom_doc, index=False)
        else:
            df.to_csv(nom_doc, index=False)
    except Exception as e:
        print(f"Erreur lors de l'exportation du DataFrame : {e}")

# fonction principale qui prend en argument une page web et un document csv auquel on veut ajouter les informations récupérées
def scrap(url, doc_nom):
        # on récupère les informations
    request = requests.get(url)
    html = request.text
    soup = BeautifulSoup(html,'html.parser')

            # QUESTIONS
        # on récupère les questions à partir des boutons (on a remarqué une standardisation sur les pages visées)
    questions = soup.findAll('span',{'class':'sp-chapter-btn-text'})
    questions_texte = [question.get_text() for question in questions] # liste avec l'ensemble des questions
    questions_texte = xaout(questions_texte)
    # liste avec l'ensemble des questions
    
            # REPONSES
    chemins = soup.findAll('ol','fr-breadcrumb__list')
    reponses_brutes = soup.findAll('div',{'class':'sp-chapter-content'}) # on récupère le contenu de chaque bloc en dessous d'un bouton qu'on a identifié comme bouton question

    image_transcription = soup.findAll('div',{'class':'fr-p-2w'})
    cat_select = soup.findAll('div',{'class' : 'choice-tree-item-content'})

    reponse_filtree = []
    titre = soup.find('h1',{'id':'titlePage'})
    titre = titre.get_text()
    chemin_texte=""
    
    for chemin in chemins:
        chemin_texte+=rec_extract_text(chemin)
    chemin_texte = chemin_texte.replace('\xa0', ' ')
    
    for reponse_brute in reponses_brutes:
        reponse_filtree.append(rec_extract_text(reponse_brute))
        reponse_filtree = xaout(reponse_filtree)
        
    if image_transcription != []:
        for image in image_transcription:
            # on choisit d'ajouter en question pour la description d'une image le titre de la page
            questions_texte.append(titre)
            questions_texte = xaout(questions_texte)

            reponse_filtree.append(rec_extract_text(image))
            reponse_filtree = xaout(reponse_filtree)
            
    if cat_select != []:
        for cat in cat_select:
            # on choisit d'ajouter en question le titre de la page pour le contenu d'une page avec une sélection de choix
            questions_texte.append(titre)
            questions_texte = xaout(questions_texte)

            reponse_filtree.append(rec_extract_text(cat))
            reponse_filtree = xaout(reponse_filtree)
            
    if "?" in titre:
        rep_titre = soup.find('div',{'id' : 'intro'})
        if rep_titre != None:
            questions_texte.append(titre)
            questions_texte = xaout(questions_texte)

            reponse_filtree.append(rec_extract_text(rep_titre))
            reponse_filtree = xaout(reponse_filtree)
            
        # DATAFRAME
    if questions_texte:
           df = pd.DataFrame({'Chemin' : chemin_texte, 'Question': questions_texte, 'Réponse': reponse_filtree, 'URL': url})
            print(df)
            export(df, doc_nom)
        else:
            print(f"Aucune question trouvée pour URL: {url}")
    except Exception as e:
        print(f"Erreur lors du scraping de l'URL {url} : {e}")

# on récupère l'adresse web de la page vosdroits de la première page voulue à la dernière demandée, si la page n'est pas une page 404 ou une redirection (identifiées comme étant des pages de menu, donc sans information à scraper car c'est seulement des redirections sur d'autres pages) on va scraper la page
def requete_web(number, session, doc_nom):
    url = f"https://www.service-public.fr/particuliers/vosdroits/F{number}"
    try:
        response = session.get(url, allow_redirects=False)
        if response.status_code == 200:
            response.raise_for_status()
            scrap(url, doc_nom)
            time.sleep(random.randint(0, 3))
            return number, f"La requête a réussi {response.status_code}"
        else:
            return number, f"La requête a échoué avec le code d'état: {response.status_code}"
    except Exception as e:
        return number, f"Erreur lors de la requête pour {url} : {e}"

# on demande le nom du document csv dans lequel on va enregistrer les informations que l'on aura scrapé
def get_name_csv():
    return str(input("Veuillez entrer le nom du document csv dans lequel vous voudrez récupérer les informations, sous la forme suivante 'nomdudocument.csv'. Vous pouvez choisir un document qui n'existe pas déjà dans vos dossiers, il sera alors créé. \n"))

# on demande la plage de recherche de cet url que l'utilisateur souhaite, et ensuite le nombre de precesseurs que l'on veut utiliser pour l'utilisation du multiprocessing
def get_user_input():
    while True:
        try:
            start = int(input("Enter the start of the range: / Saisissez le début de la plage: "))
            end = int(input("Enter the end of the range (inclusive): / Saisissez la fin de la plage: "))
            if start <= end:
                numbers = range(start, end + 1)
                break
            else:
                print("Start must be less than end. Please enter valid numbers. / Le début doit être inférieur à la fin. Veuillez saisir des chiffres valides.")
        except ValueError:
            print("Please enter valid natural numbers for the range. / Veuillez entrer des entiers valides pour la plage.")
    while True:
        try:
            num_processes = int(input("Enter the number of Pool: / Saisissez le nombre de Pool: "))
            if num_processes > 0:
                break
            else:
                print("Please enter a positive integer for the number of Pool. / Saisissez un nombre positif.")
        except ValueError:
            print("Please enter a valid integer for the number of Pool. / Veuillez entrer un entier valide pour le nombre de Pool.")
    return numbers, num_processes

# on vérifie qu'il n'y a pas des lignes doublons dans le fichier csv et on update le fichier donné sans les doublons
def verif_doublon(doc_nom):
    df = pd.read_excel(doc_nom)
    df.drop_duplicates(subset=df.columns[1], keep='first', inplace=True)
    df.to_csv(doc_nom, index=False)



# fonction principale qui va utiliser les précédentes
def main():
        # on peut directement indiquer les informations que l'on veut sans utiliser cette fonction en enlevant le # permettant la mise en argumetation de la ligne de code voulue
    numbers, num_processes = get_user_input()
    # numbers, num_processes = 
    
    doc_nom = get_name_csv()

    if os.path.exists(doc_nom):
        os.remove(doc_nom)

        # on choisit de timer le temps que prendra le scraping des pages
    start_time = timer()
    
    with requests.Session() as session:
        with Pool(num_processes) as pool:
            results = pool.starmap(requete_web, [(number, session, doc_nom) for number in numbers])
    end_time = timer()

    for result in results:
        print(result)

    print(f"Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main()
