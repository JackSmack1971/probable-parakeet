import requests
from bs4 import BeautifulSoup
import nltk
from textblob import TextBlob
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import os

# At the beginning of your main function, add:
print("Current Working Directory:", os.getcwd())


# Ensure you have downloaded the necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('brown')  # Make sure to download the 'brown' corpus for TextBlob

def fetch_page_content(url):
    response = requests.get(url)
    return response.text

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    return filtered_words

def extract_entities(text):
    blob = TextBlob(text)
    return blob.noun_phrases

def build_lsi_model(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=10)
    return lsi, dictionary

def main(url):
    html_content = fetch_page_content(url)
    text = extract_text(html_content)
    preprocessed_text = preprocess_text(text)
    entities = extract_entities(text)
    
    lsi_model, dictionary = build_lsi_model([preprocessed_text])
    
    # Initialize a dictionary to hold entities and LSI keywords
    data = {"Entities": [], "LSI Keywords": []}
    
    # Append entities to the DataFrame
    for entity in entities:
        data["Entities"].append(entity)
    
    # Extract keywords from LSI topics and append to the DataFrame
    topics = lsi_model.show_topics(num_topics=10, formatted=False)
    for topic in topics:
        for word, _ in topic[1]:  # topic[1] contains the list of (word, weight) tuples
            data["LSI Keywords"].append(word)
    
    # Ensure both columns have the same length for the DataFrame
    max_len = max(len(data["Entities"]), len(data["LSI Keywords"]))
    data["Entities"] += [""] * (max_len - len(data["Entities"]))
    data["LSI Keywords"] += [""] * (max_len - len(data["LSI Keywords"]))
    
    # Create DataFrame and export to Excel
    df = pd.DataFrame(data)
    df.to_excel("lsi_keywords_and_entities.xlsx", index=False)

if __name__ == "__main__":
    url = "https://artofficialintelligence.academy"  # Change this to the URL you wish to scrape
    main(url)
