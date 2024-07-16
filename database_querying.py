from classes import Manga;
import sqlite3 as sql;

def insert_followed_manga(manga:Manga, cur:sql.Cursor, con:sql.Connection):
    """Insert a `Manga` into the db."""
    # Updating after each addition is less efficent but prevents data loss in the case of an interuption
    cur.execute("INSERT OR IGNORE INTO manga VALUES(?, ?, ?, ?, ?, ?, ?)", (manga.id, manga.desc,  manga.url, manga.updated, manga.rating, manga.year, int(manga.oneshot)))  
    
    for title in manga.titles:
      cur.execute("INSERT INTO manga_titles VALUES(?, ?)", (manga.id, title))

    for tag in manga.tags:
      cur.execute("INSERT INTO manga_tags VALUES(?, ?)", (manga.id, tag))
      
    con.commit()

def create_db():
  """Create a `recommendations.db`."""
  con = sql.connect("recommendations.db")
  cur = con.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS manga(id TEXT, desc TEXT, url TEXT, updated TEXT, rating REAL, year INTEGER, oneshot INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS manga_tags(id TEXT, title TEXT)")
  cur.execute("CREATE TABLE IF NOT EXISTS manga_titles(id TEXT, tag TEXT)")
  con.close()