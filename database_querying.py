from enum import Enum
import pprint
from typing import List
from classes import Manga;
import sqlite3 as sql;

# Refactor
# - I don't think I need to care about when a manga was updated
# - Is there a less hacky way to prevent duplicate tags than creating a dead column for the id + num

def create_db():
  """Create a `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS neutral_manga(id TEXT PRIMARY KEY, title TEXT, desc TEXT, url TEXT, rating REAL, year INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS neutral_manga_tags(id TEXT, tag_num TEXT PRIMARY KEY, tag TEXT)")
  cur.execute("CREATE TABLE IF NOT EXISTS followed_manga(id TEXT PRIMARY KEY, title TEXT, desc TEXT, url TEXT, rating REAL, year INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS followed_manga_tags(id TEXT, tag_num TEXT PRIMARY KEY, tag TEXT)")
  cur.execute("CREATE TABLE IF NOT EXISTS unfollowed_manga(id TEXT PRIMARY KEY, title TEXT, desc TEXT, url TEXT, rating REAL, year INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS unfollowed_manga_tags(id TEXT, tag_num TEXT PRIMARY KEY, tag TEXT)")
  con.close()

def insert_manga(table:str, manga:Manga, con:sql.Connection, cur:sql.Cursor):
  """Insert a `Manga` into the unfollowed section of `recommendations.db`."""
  # Updating after each addition is less efficent but prevents data loss in the case of an interuption
  cur.execute(f"INSERT OR IGNORE INTO {table} VALUES(?, ?, ?, ?, ?, ?)", (manga.id, manga.title, manga.desc,  manga.url, manga.rating, manga.year))  

  for (index,tag) in enumerate(manga.tags):
    cur.execute(f"INSERT OR IGNORE INTO {table}_tags VALUES(?, ?, ?)", (manga.id, f"{manga.id}{index}", tag))

  con.commit()

def get_mangas(table:str, fetch: int | None) -> List[Manga]:
  """Retrieves all `Manga` from the table in `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  
  cur.execute(f"SELECT * from {table}")
  
  mangas = []
  if fetch == None:
    mangas = cur.fetchall()
  else:
    mangas = cur.fetchmany(fetch)

  for i in range(len(mangas)):
    manga = mangas[i]
    # Get the manga's tags
    cur.execute(f"SELECT tag from {table}_tags WHERE id=?", (manga[0],))
    tags = cur.fetchall()
    for j in range(len(tags)):
      tags[j] = tags[j][0]
    mangas[i] = Manga.from_data(id=manga[0], title=manga[1], tags=tags, desc=manga[2], url=manga[3], rating=manga[4], year=manga[5])
  con.close()
  return mangas


def get_followed_ids(fetch: int | None) -> List[str]:
  """Retrieves ids of all manga the user follows from `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()

  cur.execute("SELECT id from followed_manga")

  ids = []
  if fetch == None:
    ids = cur.fetchall()
  else:
    ids = cur.fetchmany(fetch)
  
  con.close()
  return ids

# create_db()