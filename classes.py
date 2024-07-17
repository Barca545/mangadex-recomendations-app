import json
import requests;
from datetime import datetime;
import langid
from typing import List, Self

class Manga:
  def __init__(self,id:str, title:str, tags:List[str], desc:str, url:str, updated:str, rating:float, year:int, oneshot:int):
    manga_res = json.loads(requests.get(f"https://api.mangadex.org/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["data"]["attributes"]
    manga_stats = json.loads(requests.get(f"https://api.mangadex.org/statistics/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["statistics"][id]

    self.id = id
    self.title = ""
    self.tags = []
    self.desc = ""
    self.url = f"https://mangadex.org/title/{id}"
    self.updated = datetime.fromisoformat("2023-11-11T01:43:07+00:00").strftime("%m/%d/%Y")
    self.rating = manga_stats["rating"]["bayesian"]
    self.year = manga_res["year"]
    self.oneshot = False

    # Get the description and clean it
    if "en" in manga_res["description"]:
      self.desc = manga_res["description"]["en"]

    # Get the titles
    if "en" in manga_res["title"]:
      self.title = manga_res["title"]["en"]
      lang_check = langid.classify(self.title)
      if lang_check != None and lang_check[0] != "en" or lang_check[1] > -80.0:
        for title in manga_res["altTitles"]:
          if "en" in title:
            self.title = title["en"]
            break
    
    # Get the tags
    for tag in manga_res["tags"]:
      if tag["attributes"]["name"]["en"] == "Oneshot":
        self.oneshot = True
      else:
        self.tags.append(tag["attributes"]["name"]["en"])

  @classmethod
  def from_data(cls, id:str, title:str, tags:List[str], desc:str, url:str, updated:str, rating:float, year:int, oneshot:int) -> Self:
    cls.oneshot = bool(oneshot)
    return cls(id = id, title = title, tags = tags, desc = desc, url = url, updated = updated, rating = rating, year = year, oneshot = bool(oneshot))

  def is_complete(self, chapter_id:str) -> bool:
    """Checks whether a given manga (json object) is complete."""
    manga = json.loads(requests.get(f"https://api.mangadex.org/manga/{self.id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["data"]["attributes"]
    chapter = json.loads(requests.get(f"https://api.mangadex.org/chapter/{chapter_id}").content)["data"]["attributes"]
    if manga["status"] == "completed" and manga["lastChapter"] != "":
      return manga["lastChapter"] == chapter["chapter"]
    else:
      False

  def __str__(self) -> str:
    str_rep = {
      "id":self.id,
      "title":self.title,
      "tags":self.tags,
      "desc":self.desc,
      "url":self.url,
      "updated":self.updated,
      "rating":self.rating,
      "year":self.year,
      "oneshot":self.oneshot,
    }
    return f'{str_rep}'
  
  def __repr__(self):
    return self.__str__()
  

  
