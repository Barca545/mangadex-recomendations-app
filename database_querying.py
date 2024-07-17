import pprint
from typing import List
from classes import Manga;
import sqlite3 as sql;

def insert_followed_manga(manga:Manga, cur:sql.Cursor, con:sql.Connection):
    """Insert a `Manga` into the `recommendations.db`."""
    # Updating after each addition is less efficent but prevents data loss in the case of an interuption
    cur.execute("INSERT OR IGNORE INTO manga VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (manga.id, manga.title, manga.desc,  manga.url, manga.updated, manga.rating, manga.year, int(manga.oneshot)))  

    for tag in manga.tags:
      cur.execute("INSERT INTO manga_tags VALUES(?, ?)", (manga.id, tag))
      
    con.commit()

def create_db():
  """Create a `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS manga(id TEXT PRIMARY KEY, title TEXT, desc TEXT, url TEXT, updated TEXT, rating REAL, year INTEGER, oneshot INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS manga_tags(id TEXT, tag TEXT)")
  con.close()

def get_mangas() -> List[Manga]:
  """Retrieves the user's followed `Manga` from `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  
  cur.execute("SELECT * from manga")
  mangas = cur.fetchmany(2)
  # mangas = cur.fetchall()

  for i in range(len(mangas)):
    manga = mangas[i]
    # Get the manga's tags
    cur.execute("SELECT tag from manga_tags WHERE id=?", (manga[0],))
    tags = cur.fetchall()
    for j in range(len(tags)):
      tags[j] = tags[j][0]
    mangas[i] = Manga.from_data(id=manga[0], title=manga[1], tags=tags, desc=manga[2], url=manga[3], updated=manga[4], rating=manga[5], year=manga[6], oneshot=manga[7])
  con.close()
  return mangas