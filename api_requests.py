import requests;
import json;
import sqlite3 as sql;
from datetime import datetime;
from urllib.parse import quote
from classes import Manga
from database_querying import insert_followed_manga

# Refactor
# - I need to devise a way to ommit manga that have already been suggested from the search
# - Need to test the is_complete check

secrets = json.load(open("tokens.json"))
res = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", secrets)
res_content = json.loads(res.content)

# API tokens
(access, refresh) = (res_content["access_token"],res_content["refresh_token"])

# API call header with bearer token
api_call_headers = {
  "Authorization": f"Bearer {access}",
  "accept":"application/json"
  }

def get_user_follows_list(): 
  # Get the ids of all followed manga
  ids = json.loads(requests.get("https://api.mangadex.org/manga/status?status=reading",  headers=api_call_headers).content.decode('utf8').replace("'", '"'))["statuses"]
  
  # Connect to the db
  con = sql.connect("recommendations.db")
  cur = con.cursor()

  # Convert each item to a Manga and append it to the db
  tracker = 0 
  for id in ids:
    insert_followed_manga(Manga(id), cur, con)
    tracker+=1
    print(f"{id}: {tracker} of {len(ids)} mangas processed.")
  
  con.close()

def user_follows(id:str) -> bool:
  """Returns `True` if the user is following the manga already."""
  return 200 == requests.get(f"https://api.mangadex.org/user/follows/manga/{id}",headers=api_call_headers).status_code

def get_recent_updates(last_update_time:str,):
  """Checks for recently updated chapters. Finds their `Manga` and checks if it should be returned. 
  Returns a filtered list of `Manga` matching basic user preferences."""
  chapters_to_check = []
  offset = 0
  
  # Fetch all chapters since last update and add them to the list to check
  while True:
    # Get all recently updated manga since the last search 
    date = quote((last_update_time)) 
    chapters = json.loads(requests.get(f"https://api.mangadex.org/chapter?limit=99&offset={offset*99}&originalLanguage%5B%5D=ja&originalLanguage%5B%5D=kr&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&includeFutureUpdates=0&publishAtSince={date}&order%5BreadableAt%5D=desc").content.decode('utf8'))["data"]
    offset+=1

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


    
get_recent_updates("2024-07-16T02:21:56")  


# con = sql.connect("recommendations.db")
# cur = con.cursor()
# res = cur.execute("SELECT * FROM manga WHERE id= ?", ("9bb7e77b-c34b-4b96-b1cd-38c1aaddc06f",))
# print(res.fetchone())
