import sqlite3
import json
from services.matching_service import get_embedding

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("SELECT id, title, description FROM items")
items = c.fetchall()

for item in items:
    item_id, title, description = item

    emb = get_embedding(title + " " + description)
    emb_json = json.dumps(emb)

    c.execute("UPDATE items SET embedding=? WHERE id=?", (emb_json, item_id))

conn.commit()
conn.close()

print("✅ All embeddings updated")
