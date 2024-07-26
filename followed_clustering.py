from typing import List
import pandas as pd;
from sklearn import linear_model 
from sklearn.metrics import accuracy_score
from classes import Manga
from database_querying import get_mangas;
import numpy as np

# lets start with sorting by tags then add in the ratings then year then descriptions

# Refactor:
# - Still have to clean the description data when I store it

# Get the different Manga lists
followed_mangas = get_mangas("followed_manga", 2)
unfollowed_mangas = get_mangas("unfollowed_manga", 2)
neutral_mangas = get_mangas("neutral_manga", 2)

# Model's predictor variable
tags = []
# Model's outcome variable -1 means unliked, 0 means neutral, 1 means followed
liked = []

# Add the unfollowed mangas
for manga in unfollowed_mangas:
  tags.append(manga.binarize_tags())
  liked.append(-1)

# Add the neutral mangas
for manga in neutral_mangas:
  tags.append(manga.binarize_tags())
  liked.append(0)

# Add the followed mangas
for manga in followed_mangas:
  tags.append(manga.binarize_tags())
  liked.append(1)

print(tags)

# X = np.array(tags)
# y = np.array(liked)

# classifier = linear_model.LogisticRegression(C=10, solver="saga", multi_class="multinomial", max_iter=10000)
# classifier.fit(X,y)

# y_pred = classifier.predict(X)
# accuracy = accuracy_score(y, y_pred)
# print("Accuracy (train) for %s: %0.1f%% " % ("classifier", accuracy * 100))