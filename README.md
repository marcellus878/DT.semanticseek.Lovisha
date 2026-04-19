# 🔍 SemanticSeek — AI Powered Lost & Found System

## 🧠 Project Overview

SemanticSeek is a smart Lost & Found web application built for campus environments.
It uses **AI-based semantic matching + image similarity** to automatically connect lost and found items.

### 🎯 Goal

To replace manual lost-and-found systems with an **intelligent, automated, and interactive platform**.

---

## 🚀 Features Implemented

### 🔐 Authentication

* User registration & login
* Session-based authentication

### 📦 Item Management

* Post lost/found items
* Upload images
* Edit items (title, description, image, category, status)
* Delete items
* Status tracking (Lost, Found, Claimed, Returned)

### 🧠 AI Matching System

* Semantic similarity using Sentence Transformers
* Cosine similarity scoring
* Keyword overlap boosting
* Category-based matching boost/penalty
* Image similarity (embedding-based)
* Combined scoring system

### 🔔 Smart Alerts

* Automatic match detection
* Top matches shown in dashboard
* Match scoring with explanation

### 💬 Chat System

* Real-time-style messaging (Flask-based)
* Chat tied to specific items
* Inbox system
* Message notifications badge

### 🗂️ Category System

* Items categorized (Electronics, Wallet, Clothing, etc.)
* Improves matching accuracy

### 📍 Location Support

* Map-based location selection (Leaflet.js)

### 🎨 UI (Glassmorphism Theme)

* Dark themed UI
* Responsive dashboard
* Navbar with profile dropdown
* Clean item cards
* Chat UI similar to WhatsApp

---

## ⚙️ Tech Stack

### Backend

* Python (Flask)
* SQLite

### AI / ML

* Sentence Transformers (`all-mpnet-base-v2`)
* NumPy

### Frontend

* HTML (Jinja templates)
* CSS (custom + glassmorphism)
* JavaScript
* Leaflet.js (maps)

---

## 🏃 How to Run the Project

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd lost-found-app
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Application

```bash
python app.py
```

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 🗄️ Database Setup

Database is auto-created on first run.

If issues occur:

* Delete `database.db`
* Restart app

---

## 📁 Project Structure

```
lost-found-app/
│
├── app.py
├── database.db
│
├── services/
│   ├── matching_service.py
│   ├── image_matching.py
│
├── templates/
│   ├── base.html
│   ├── auth/
│   ├── items/
│   ├── chat/
│
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │
│   ├── uploads/
│   ├── js/
│
└── .env
```

---

## ⚠️ Important Notes for Developers

### 🔥 CSS System

* `main.css` → global design (DO NOT override)
* `components.css` → feature-specific styles ONLY

### 🔥 AI Model

* Uses `all-mpnet-base-v2`
* Ensure embeddings are consistent (same model always)

### 🔥 Performance

* Embeddings are generated only during post/edit
* Matching is optimized (no repeated encoding)

---

## 🚧 Features Pending / Future Work

### 🔥 HIGH PRIORITY

* Email notifications (match alerts)
* SMS notifications (optional)
* Image-based matching improvements (CLIP / better embeddings)
* Better ranking algorithm tuning

### 🔥 MEDIUM PRIORITY

* Admin dashboard
* Report / spam system
* Item verification system
* Search & filters (category, date, status)

### 🔥 UI Improvements

* Animations & micro-interactions
* Mobile responsiveness improvements
* Loading skeletons

### 🔥 Advanced AI

* Fine-tuned model for item matching
* Duplicate detection
* Auto-tagging categories

---

## 📌 Known Issues

* Matching accuracy depends on input quality
* Image similarity is basic (can be improved)
* No real-time WebSocket chat (currently refresh-based)

---

## 🔮 Future Vision

SemanticSeek can evolve into:

* Campus-wide system
* Multi-campus platform
* Mobile app (Flutter / React Native)
* AI-powered recovery assistant

---

## 👥 Contributors

* Original Developer: *[Your Name]*
* Future Contributors: Open for extension

---

## 📜 License

This project is open for academic and educational use.

---

## 💡 Final Note

This project is built with scalability in mind.
Core systems (AI matching, chat, items) are modular and can be extended easily.

---
