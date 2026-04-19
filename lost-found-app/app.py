from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import json
from dotenv import load_dotenv
from services.image_matching import get_image_embedding

load_dotenv()

# 🔥 IMPORT AI FUNCTIONS
from services.matching_service import find_matches_ai, get_embedding

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🔹 USERS TABLE
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
    """
    )

    # 🔹 ITEMS TABLE (UPDATED 🔥)
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        title TEXT,
        description TEXT,
        status TEXT,
        timestamp TEXT,
        image TEXT,
        embedding TEXT,
        category TEXT,
        image_embedding TEXT
    )
    """
    )

    # 🔹 MESSAGES TABLE
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        item_id INTEGER,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()


# 🔥 RUN DB INIT
init_db()


# ---------- HOME ----------
@app.route("/")
def home():
    if "username" in session:
        return redirect("/explore")
    return redirect("/login")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
            "SELECT id, name, username, email, password FROM users WHERE email=?",
            (email,),
        )
        user = c.fetchone()
        conn.close()

        if user and user[4] == password:
            session["name"] = user[1]
            session["username"] = user[2]
            return redirect("/explore")
        else:
            error = "Invalid email or password"

    return render_template("auth/login.html", error=error)


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # CHECK USERNAME
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            error = "Username already taken"
        else:
            c.execute(
                "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
                (name, username, email, password),
            )
            conn.commit()
            conn.close()
            return redirect("/login")

        conn.close()

    return render_template("auth/register.html", error=error)


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    user_name = session["name"]

    c.execute("SELECT * FROM items WHERE user=?", (user_name,))
    user_items = c.fetchall()

    c.execute("SELECT * FROM items")
    all_items = c.fetchall()

    conn.close()

    alerts = []

    for item in user_items:
        matches = find_matches_ai(item, all_items)
        for match in matches:
            alerts.append((item, match))

    return render_template("dashboard/dashboard.html", items=user_items, alerts=alerts)


# ---------- EXPLORE ----------
@app.route("/explore")
def explore():
    if "username" not in session:
        return redirect("/login")

    query = request.args.get("q")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if query:
        c.execute(
            "SELECT * FROM items WHERE title LIKE ? OR description LIKE ? ORDER BY id DESC",
            ("%" + query + "%", "%" + query + "%"),
        )
    else:
        c.execute("SELECT * FROM items ORDER BY id DESC")

    items = c.fetchall()
    conn.close()

    return render_template("explore.html", items=items, query=query)


# ---------- POST ITEM ----------
@app.route("/post", methods=["GET", "POST"])
def post_item():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        category = request.form["category"]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 🔥 TEXT EMBEDDING
        embedding = get_embedding(title + " " + description)
        embedding_json = json.dumps(embedding) if embedding else None

        # 🔥 IMAGE HANDLING + EMBEDDING
        file = request.files.get("image")
        filename = ""
        image_embedding_json = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # 🔥 GENERATE IMAGE EMBEDDING (ONLY ONCE)
            try:
                from services.image_matching import get_image_embedding

                emb = get_image_embedding(filepath)

                if emb is not None:
                    image_embedding_json = json.dumps(emb.cpu().numpy().tolist())
            except Exception as e:
                print("Image embedding error:", e)

        # 🔥 INSERT INTO DB (UPDATED)
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO items 
            (user, title, description, status, timestamp, image, embedding, category, image_embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["name"],
                title,
                description,
                status,
                timestamp,
                filename,
                embedding_json,
                category,
                image_embedding_json,  # 🔥 NEW
            ),
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("items/post_item.html")


# ---------- SMART SEARCH ----------
@app.route("/smart_search/<int:item_id>")
def smart_search(item_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    current_item = c.fetchone()

    if not current_item:
        conn.close()
        return redirect("/dashboard")

    if current_item[4] == "Lost":
        c.execute("SELECT * FROM items WHERE status='Found'")
    else:
        c.execute("SELECT * FROM items WHERE status='Lost'")

    all_items = c.fetchall()

    # MAP name → username
    c.execute("SELECT name, username FROM users")
    mapping = dict(c.fetchall())

    conn.close()

    matches = find_matches_ai(current_item, all_items)

    updated_matches = []
    for item, score, explanation in matches:
        username = mapping.get(item[1], item[1])
        updated_matches.append((item, score, explanation, username))

    return render_template("smart_results.html", matches=updated_matches)


# ---------- CHAT ----------
@app.route("/chat/<receiver_username>/<int:item_id>", methods=["GET", "POST"])
def chat(receiver_username, item_id):
    if "username" not in session:
        return redirect("/login")

    sender = session["username"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        message = request.form.get("message")
        if message:
            c.execute(
                "INSERT INTO messages (sender, receiver, item_id, message) VALUES (?, ?, ?, ?)",
                (sender, receiver_username, item_id, message),
            )
            conn.commit()

    c.execute(
        """
    SELECT sender, receiver, message, timestamp
    FROM messages
    WHERE (sender=? AND receiver=? AND item_id=?)
       OR (sender=? AND receiver=? AND item_id=?)
    ORDER BY timestamp ASC
    """,
        (sender, receiver_username, item_id, receiver_username, sender, item_id),
    )

    messages = c.fetchall()

    c.execute("SELECT name FROM users WHERE username=?", (receiver_username,))
    user = c.fetchone()
    receiver_name = user[0] if user else receiver_username

    conn.close()

    return render_template("chat.html", messages=messages, other_user=receiver_name)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/delete_item/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🔐 Ensure user owns item
    c.execute("SELECT user FROM items WHERE id=?", (item_id,))
    item = c.fetchone()

    if item and item[0] == session["name"]:
        c.execute("DELETE FROM items WHERE id=?", (item_id,))
        conn.commit()

    conn.close()
    return redirect("/dashboard")


@app.route("/inbox")
def inbox():
    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🔥 Get latest message per conversation
    c.execute(
        """
    SELECT m1.*
    FROM messages m1
    JOIN (
        SELECT 
            CASE 
                WHEN sender = ? THEN receiver 
                ELSE sender 
            END as other_user,
            item_id,
            MAX(timestamp) as max_time
        FROM messages
        WHERE sender = ? OR receiver = ?
        GROUP BY other_user, item_id
    ) m2
    ON m1.item_id = m2.item_id 
       AND m1.timestamp = m2.max_time
    WHERE m1.sender = ? OR m1.receiver = ?
    ORDER BY m1.timestamp DESC
    """,
        (current_user, current_user, current_user, current_user, current_user),
    )

    chats = c.fetchall()

    # 🔹 Get username → name mapping
    c.execute("SELECT username, name FROM users")
    user_map = dict(c.fetchall())

    conn.close()

    return render_template("inbox.html", chats=chats, user_map=user_map)


@app.context_processor
def inject_notifications():
    if "username" not in session:
        return {}

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    current_user = session["username"]

    # 🔥 Count messages received
    c.execute(
        """
        SELECT COUNT(*) FROM messages
        WHERE receiver = ?
    """,
        (current_user,),
    )
    msg_count = c.fetchone()[0]

    conn.close()

    return dict(msg_count=msg_count)


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🔹 FETCH ITEM FIRST (for both GET + ownership check)
    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = c.fetchone()

    if not item:
        conn.close()
        return redirect("/dashboard")

    # 🔐 OWNER CHECK (IMPORTANT)
    if item[1] != session["name"]:
        conn.close()
        return redirect("/dashboard")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        category = request.form["category"]

        # 🔥 REGENERATE EMBEDDING
        embedding = get_embedding(title + " " + description)
        embedding_json = json.dumps(embedding)

        # 🔥 HANDLE IMAGE UPDATE
        file = request.files.get("image")
        filename = item[6]  # keep old image by default

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        # 🔥 SINGLE CLEAN UPDATE QUERY
        c.execute(
            """
            UPDATE items
            SET title=?, description=?, status=?, embedding=?, image=?, category=?
            WHERE id=?
            """,
            (
                title,
                description,
                status,
                embedding_json,
                filename,
                category,
                item_id,
            ),
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()
    return render_template("items/edit_item.html", item=item)


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=False)
