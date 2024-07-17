from typing import List
import pandas as pd;
from sklearn.preprocessing import MultiLabelBinarizer 
from sklearn.feature_extraction.text import TfidfVectorizer
from classes import Manga
from database_querying import get_mangas;

# lets start with sorting by tags then add in the descriptions

# Refactor:
# - Still have to clean the description data when I store it

def pre_process_tags(mangas:List[Manga]):
  mlb = MultiLabelBinarizer()
  tags = []
  for manga in mangas:
    tags.append(manga.tags)
  return mlb.fit_transform(tags)

def preprocess_description():
  tfidf = TfidfVectorizer(stop_words='english')

mangas = get_mangas()



print(pre_process_tags(mangas))
