from typing import Dict, List
import requests;
import json;
import sqlite3 as sql;
from datetime import datetime;
from urllib.parse import quote
from classes import Manga
from database_querying import get_followed_ids, insert_manga
from tqdm.auto import tqdm
import langid

# Refactor
# - I need to devise a way to ommit manga that have already been suggested from the search
# - Need to test the is_complete check
# - Need more robust handling for a rating no response than skipping it
# - Rework the get all to go by date added so it can easily fetch new ones using offset 0 + stopping at some already found id 
# - Set the update on a timer instead of automatically

# Todo
# - Delete the current neutral manga
# - When fetching neutral manga search for a rating and sort them into disliked accordingly


# API tokens
secrets = json.load(open("tokens.json"))
res = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", secrets["access"])
res_content = json.loads(res.content)

(access, refresh) = (res_content["access_token"],res_content["refresh_token"])

last_refresh = datetime.now()

def refresh_token():
  payload = secrets["refresh"]
  payload["refresh_token"] = refresh
  res = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", payload)
  res_content = json.loads(res.content)
  
  # Access and update the globals
  global access
  global last_refresh
  access  = res_content["access_token"]
  last_refresh = datetime.now()

# API call header with bearer token
def get_auth() -> Dict:
  return {
    "Authorization": f"Bearer {access}",
    "accept":"application/json"
  }


# HELPER FUNCTIONS
def get_rating(id):
  """Try to get a `Manga`'s rating. Return 11 if no rating can be found."""
  for i in range(6):
    try:
      return json.loads(requests.get(f"https://api.mangadex.org/statistics/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["statistics"][id]["rating"]["bayesian"]
    except KeyError:
      if i == 5:
        print(f"{id} has no rating")
        return 11
      print(f"try {i}")
      continue

def user_follows(id:str) -> bool:
  """Returns `True` if the user is following the manga already."""
  return 200 == requests.get(f"https://api.mangadex.org/user/follows/manga/{id}",headers=get_auth()).status_code

def disliked(id:str):
  """Returns `True` if the user has given the manga a rating of <=5 the manga already."""
  res = json.loads(requests.get(f"https://api.mangadex.org/rating?manga[]={id}", headers=get_auth()).content.decode('utf8').replace("'", '"'))
  if len(res["ratings"]) > 0:
    return 5 >= int(res["ratings"][id]["rating"])
  else:
    return False

# API ACCESS
def followed_manga_get_and_store(): 
  # Get the ids of all followed manga
  ids = json.loads(requests.get("https://api.mangadex.org/manga/status?status=reading",  headers=get_auth()).content.decode('utf8').replace("'", '"'))["statuses"]
  
  # Connect to the db
  con = sql.connect("recommendations.db")
  cur = con.cursor()

  # Convert each item to a Manga and append it to the db
  tracker = 0 
  for id in ids:
    insert_manga("followed_manga", Manga(id), con, cur)
    tracker+=1
    print(f"{id}: {tracker} of {len(ids)} mangas processed.")
  
  con.close()

def get_recent_updates(last_update_time:str,) -> List[Manga]:
  """Checks for recently updated chapters. Finds their `Manga` and checks if it should be returned. 
  Returns a filtered list of `Manga` matching basic user preferences."""
  chapters_to_check = []
  offset = 0
  
  # Fetch all chapters since last update and add them to the list to check
  while True:
    # Get all recently updated manga since the last search 
    date = quote((last_update_time)) 
    chapters = json.loads(requests.get(f"https://api.mangadex.org/chapter?limit=99&offset={offset*99}&originalLanguage%5B%5D=ja&originalLanguage%5B%5D=kr&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&includeFutureUpdates=0&publishAtSince={date}&order%5BreadableAt%5D=desc").content.decode('utf8'))["data"]
    offset += 1

    # Return if nothing is found because it means we have found all manga since the last update
    if len(chapters) == 0:
      break
    
    if chapter["attributes"]["translatedLanguage"] == "en":
      chapters_to_check.extend(chapters)
    
  # Filter the mangas
  mangas = []
  tracker = 0
  for chapter in chapters_to_check: 
    # IDs
    manga_id = ""
    chapter_id = chapter["id"]
    for relationship in chapter["relationships"]:
      if relationship["type"] == "manga":
        manga_id = relationship["id"]
    
    manga = Manga(manga_id)
    # Filter 
    # - Manga whose last update was not in english
    # - Newest chapter cannot equal last chapter unless it is a oneshot
    # - Not already following
    if chapter["attributes"]["translatedLanguage"] != "en" or manga.is_complete(chapter["id"]) or user_follows(manga_id):
      tracker += 1  
      print(f"{chapter_id}: {tracker} of {len(chapters_to_check)} mangas processed.")
      continue
    else:
      mangas.append(manga)
      tracker += 1
      print(f"{chapter_id}: {tracker} of {len(chapters_to_check)} mangas processed.")
  
  print(f"mangas found: {len(mangas)}")
  
  # Update the time of the last update
  print(datetime.now().replace(microsecond=0).isoformat())
  
  return mangas

def get_and_store_all_manga(offset=0):
  """Fetches ~10,000 Manga. Sorts them into the neutral and disliked databases."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()

  # Query until all manga have been found
  while True:
    # Refresh the token
    refresh_token()
    
    # Get all recently updated manga since the last search 
    mangas = json.loads(requests.get(f"https://api.mangadex.org/manga?limit=99&offset={offset*99}&includedTagsMode=AND&excludedTagsMode=OR&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5BlatestUploadedChapter%5D=desc").content.decode('utf8'))["data"]
    offset += 1

    # Return if nothing is found because it means we have found all manga since the last update
    if len(mangas) == 0:
      break

    with tqdm(mangas, desc=f"Query Number: {offset-1}", colour="yellow", position=0, leave=True) as iterator:
      for manga in iterator:     
        id = manga["id"]
        manga = manga["attributes"]
        title = ""
        tags = []
        desc = ""
        url = f"https://mangadex.org/title/{id}"
        rating = get_rating(id) 
        year = manga["year"]

        # Get the titles
        # Check if "en" title exists
        title = manga["title"].get("en") or list(manga["title"].values())[0]
        lang_check = langid.classify(title)

        # If lang_check is not English or confidence is low, check alternative titles
        if lang_check[0] != "en" or lang_check[1] > -80.0:
          for alt_title in manga["altTitles"]:
            if "en" in alt_title:
              title = alt_title["en"]
              break

        # Get the tags
        for tag in manga["tags"]:
          tags.append(tag["attributes"]["name"]["en"])

        # Get the description
        if "en" in manga["description"]:
          desc = manga["description"]["en"]

        # Add the new manga to the db
        if disliked(id):
          insert_manga("unfollowed_manga", Manga.from_data(id, title, tags, desc, url, rating, year), con, cur)    
        else:
          insert_manga("neutral_manga", Manga.from_data(id, title, tags, desc, url, rating, year), con, cur)    
    
    print(f"Query {offset-1} completed")
  con.close()      

get_and_store_all_manga(70)