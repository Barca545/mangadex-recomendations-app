import json
import requests;
import langid
from typing import List, Self

class Manga:
  def __init__(self,id:str, title:str, tags:List[str], desc:str, url:str, rating:float, year:int):
    manga_res = json.loads(requests.get(f"https://api.mangadex.org/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["data"]["attributes"]
    manga_stats = json.loads(requests.get(f"https://api.mangadex.org/statistics/manga/{id}",{"accept":"application/json"}).content.decode('utf8').replace("'", '"'))["statistics"][id]

    self.id = id
    self.title = manga_res["title"].get("en") or list(manga_res["title"].values())[0]
    self.tags = []
    self.desc = ""
    self.url = f"https://mangadex.org/title/{id}"
    self.rating = manga_stats["rating"]["bayesian"]
    self.year = manga_res["year"]
    self.oneshot = False

    # Get the description 
    if "en" in manga_res["description"]:
      self.desc = manga_res["description"]["en"]

    # Get the titles
    # Get the titles
    # Check if "en" title exists
   
    lang_check = langid.classify(self.title)
    # If lang_check is not English or confidence is low, check alternative titles
    if lang_check[0] != "en" or lang_check[1] > -80.0:
      for alt_title in manga_res["altTitles"]:
        if "en" in alt_title:
          self.title = alt_title["en"]
          break
    
    # Get the tags
    for tag in manga_res["tags"]:
      if tag["attributes"]["name"]["en"] == "Oneshot":
        self.oneshot = True
      else:
        self.tags.append(tag["attributes"]["name"]["en"])

  def binarize_tags(self):
    """Return the binary representation of a `Manga`'s tags."""
    tags = 0
    for tag in self.tags:
      tags += 1 << tag_defs.index(tag)
    return bin(tags)

  @classmethod
  def from_data(cls, id:str, title:str, tags:List[str], desc:str, url:str, rating:float, year:int) -> Self:
    return cls(id = id, title = title, tags = tags, desc = desc, url = url, rating = rating, year = year)

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
  

tag_defs = [
            "4-Koma",
            "Adaptation",
            "Anthology",
            "Award Winning",
            "Doujinshi",
            "Fan Colored",
            "Full Color",
            "Long Strip",
            "Official Colored",
            "Self-Published",
            "Web Comic",
            "Action",
            "Adventure",
            "Boys' Love",
            "Comedy",
            "Crime",
            "Drama",
            "Fantasy",
            "Girls' Love",
            "Historical",
            "Horror",
            "Isekai",
            "Magical Girls",
            "Mecha",
            "Medical",
            "Mystery",
            "Philosophical",
            "Psychological",
            "Romance",
            "Sci-Fi",
            "Slice of Life",
            "Sports",
            "Superhero",
            "Thriller",
            "Tragedy",
            "Wuxia",
            "Aliens",
            "Animals",
            "Cooking",
            "Crossdressing"
            "Delinquents",
            "Demons",
            "Genderswap",
            "Ghosts",
            "Gyaru",
            "Harem",
            "Incest",
            "Loli",
            "Mafia",
            "Magic",
            "Martial Arts",
            "Military",
            "Monster Girls",
            "Monsters",
            "Music",
            "Ninja",
            "Office Workers",
            "Police",
            "Post-Apocalyptic",
            "Reincarnation",
            "Reverse Harem",
            "Samurai",
            "School Life",
            "Shota",
            "Supernatural",
            "Survival",
            "Time Travel",
            "Traditional Games",
            "Vampires",
            "Video Games",
            "Villainess",
            "Virtual Reality",
            "Zombies",
            "Gore",
            "Sexual Violence",
            ]
