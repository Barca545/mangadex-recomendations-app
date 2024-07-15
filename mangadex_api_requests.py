import requests;
import json;
import sqlite3 as sql;

secrets = json.load(open("tokens.json"))
res = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", secrets["mangadex"])
res_content = json.loads(res.content)

# Refactor:
# - Use executeall or whatever instead of doing it one at a time

# API tokens
(access, refresh) = (res_content["access_token"],res_content["refresh_token"])

class Manga:
  def __init__(self, id):
    manga_res = json.loads(requests.get(f"https://api.mangadex.org/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["data"]["attributes"]
    
    self.id = id
    self.titles = []
    self.tags = []
    self.desc = ""
    self.url = f"https://mangadex.org/title/{id}"
    self.updated = manga_res["updatedAt"]

    # Get the description
    if "en" in manga_res["description"]:
      self.desc = manga_res["description"]["en"]

    # Get the titles
    if "en" in manga_res["title"]:
      self.titles.append(manga_res["title"]["en"])
    for title in manga_res["altTitles"]:
      if "en" in title:
        self.titles.append(title["en"])
    
    # Get the tags
    for tag in manga_res["tags"]:
      self.tags.append(tag["attributes"]["name"]["en"])

  def __str__(self) -> str:
    str_rep = {
      "id":self.id,
      "name":self.titles,
      "tags":self.tags,
      "desc":self.desc,
      "url":self.url,
      "updated":self.updated
    }
    return f'\u007b{str_rep}\u007d,'

def get_user_follows(): 
  api_call_headers = {
    "Authorization": f"Bearer {access}",
    "accept":"application/json"
    }
  # Get the ids of all followed manga
  ids = json.loads(requests.get("https://api.mangadex.org/manga/status?status=reading",  headers=api_call_headers).content.decode('utf8').replace("'", '"'))["statuses"]
  
  # Connect to the DB
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS manga(id TEXT PRIMARY KEY, names TEXT, tags TEXT, desc TEXT, url TEXT, updated TEXT)")
  
  # Convert each item to a Manga and append it to the db
  tracker = 0 
  for id in ids:
    manga = Manga(id)
    data = (manga.id, manga.titles.__str__(), manga.tags.__str__(), manga.desc, manga.url, manga.updated)
    # Updating after each addition is less efficent but prevents data loss in the case of an interuption
    cur.execute("INSERT OR IGNORE INTO manga VALUES(?, ?, ?, ?, ?, ?)", data)  
    con.commit()
    tracker+=1
    print(f"{id}: {tracker} of {len(ids)} mangas processed.")
  
# get_user_follows()

con = sql.connect("recommendations.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM manga WHERE id= ?", ("9bb7e77b-c34b-4b96-b1cd-38c1aaddc06f",))
print(res.fetchone())


# Looks like I have the data now so I think I can begin processing

# Hard boundries on new matches:
# - SFW
# - English
# - Ongoing or Completed
# - Newest chapter cannot equal last chapter unless it is a oneshot
