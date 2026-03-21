# Multi-API News Application (Web & iOS)
![3C4E4793-8B76-44FE-863F-7A2CD265FC12_1_105_c](https://github.com/user-attachments/assets/05000198-978a-4ef7-a798-daeb0222122a)

A cross-platform news aggregation and social platform that pulls articles from multiple global sources (NewsAPI, GNews, NewsData.io), translates them seamlessly using DeepL, and lets users share and discuss content.

The **Web version (Flask)** and **iOS version (SwiftUI)** run in parallel, sharing data in real time via Firebase as a unified backend.

The UI adopts a Liquid Glass design inspired by publicly available implementations, with a performance-optimized lightweight mode also included. Most of the coding was directed through AI agents.

---

## Features

### Smart News Aggregation
- **Multi-source:** Fetches articles from **NewsAPI**, **GNews**, and **NewsData.io** for broad coverage.
- **Parallel fetching:** Uses `ThreadPoolExecutor` to query multiple APIs concurrently, reducing response time.
- **Intelligent deduplication:** Automatically removes duplicate articles across different sources.

### Seamless Translation
- **DeepL integration:** High-quality translation between English and Japanese.
- **Bidirectional:** Supports both EN→JA and JA→EN for titles and descriptions.
- **Fallback mechanism:** If DeepL is unavailable, only articles in the target language are served (no broken translations).

### Cross-Platform User System
- **Firebase integration:** Secure login via **Firebase Authentication** and real-time data sync via **Firestore**.
- **Shared data:** Posts created on Web are visible on iOS and vice versa. Accounts are unified across platforms.
- **User posts:** Users can create posts with a title, description, and image.
- **Likes & Comments:** Like and comment on both news articles and user posts, with optimistic UI updates.

### Web UI/UX
- **Liquid Glass design:** Distinctive glassmorphism with transparency and blur effects.
- **Lightweight mode (Clean Glass):** Animation-free, performance-first design mode to prevent slowdowns in Chrome and similar browsers. Switchable from settings.
- **Responsive:** Card-based layout that adapts to various screen sizes.

### iOS (Native)
- **Native Liquid Glass:** Glassmorphism using iOS standard `UltraThinMaterial` for a fully native feel.
- **Unified feed:** News articles and user posts displayed seamlessly in a single timeline.
- **Image optimization:** Automatic resize and aspect-ratio-preserving display for post images.
- **Auth security flows:** Email verification, password reset, re-authentication, account deletion, and email address change.
- **Theme & language switching:** Light / Dark / System theme and JA / EN language toggle.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask, Firebase Admin SDK |
| Database | Google Cloud Firestore (NoSQL) |
| Authentication | Firebase Authentication (Email/Password) |
| HTTP | `requests`, `httpx` |
| Web Frontend | HTML5, CSS3, Vanilla JS, Firebase JS SDK |
| iOS | SwiftUI, Firebase iOS SDK |
| News APIs | NewsAPI, GNews, NewsData.io |
| Translation | DeepL API |
| Deploy | `gunicorn` |

---

## Setup & Installation (Web)

### 1. Prerequisites
- Python 3.11+
- API keys for NewsAPI, GNews, NewsData.io, and DeepL
- A Firebase project with Authentication (Email/Password) and Firestore enabled
- Firebase Admin SDK credentials JSON file

### 2. Install dependencies

```bash
git clone <repository-url>
cd flaskdev
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# Flask
SECRET_KEY=your_secret_key_here

# News APIs
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_api_key_here
NEWSDATA_IO_API_KEY=your_newsdata_io_api_key_here

# Translation
DEEPL_AUTH_KEY=your_deepl_auth_key_here

# Firebase (Admin SDK)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-adminsdk.json
```

### 4. Run the application

```bash
python run.py
# or
flask run --host=0.0.0.0 --port=8000
```

Open `http://localhost:8000` in your browser.

---

## Project Structure

```
flaskdev/
├── app/
│   ├── __init__.py        # App factory & Firebase Admin SDK init
│   ├── routes/
│   │   ├── main.py        # News fetch & search endpoints
│   │   ├── auth.py        # Authentication (session management)
│   │   └── posts.py       # Posts API (Firestore CRUD, likes, comments)
│   ├── services/
│   │   ├── aggregator.py  # Parallel news fetching & deduplication
│   │   ├── deepl.py       # DeepL translation wrapper
│   │   ├── gnews.py       # GNews API wrapper
│   │   ├── newsapi.py     # NewsAPI wrapper
│   │   └── newsdata.py    # NewsData.io wrapper
│   ├── static/            # CSS (glassUI.css, lightweightUI.css), images
│   └── templates/         # Jinja2 HTML (includes Firebase JS SDK init)
├── News-Mobile/           # iOS SwiftUI project (Firebase-integrated)
│   └── News-Mobile/
│       ├── ContentView.swift     # Main view (unified feed)
│       ├── PostViewModel.swift   # Firestore logic
│       ├── NewsService.swift     # Flask API client
│       └── CommentView.swift     # Comment sheet
├── docs/                  # Project documentation & implementation plans
├── requirements.txt
└── run.py                 # Entry point
```

---

## Architecture Overview

### News Flow (Server-Side)
```
Client (Web/iOS)
  → GET /api/update
  → Flask aggregator.py (parallel fetch from NewsAPI, GNews, NewsData.io)
  → DeepL translation
  → JSON response (not stored in DB — fetched on demand)
```

### User Data Flow (Firestore)
```
Web  ←→ Firebase JS SDK  ←→ Firestore `posts` collection
iOS  ←→ Firebase iOS SDK ←→ Firestore `posts` collection
         (real-time sync across platforms)
```

### Authentication
```
Client → Firebase Auth (Client SDK) → ID Token
Token  → Flask Backend (Admin SDK verification) → Session established
```

---

## Design Highlights

- **Dual Web themes:** Heavy "Liquid Glass" and lightweight "Clean Glass" — users choose based on their hardware.
- **iOS native feel:** `UltraThinMaterial` throughout, matching Apple's design language.
- **On-demand news fetching:** No scheduled jobs needed; news is fetched when the user requests it, saving API quota.
- **Base64 image storage:** Since Firebase Storage (Blaze plan) is not used, iOS post images are resized to ≤800px, JPEG-compressed, and stored as Base64 strings directly in Firestore.

---

## Roadmap

- [x] Multi-source news aggregation with parallel fetch
- [x] DeepL translation with fallback
- [x] Firebase Auth + Firestore cross-platform sync
- [x] iOS Native Liquid Glass UI
- [x] Likes & comments (Web)
- [ ] Likes & comments (iOS)
- [ ] User profile pages (display name, avatar)
- [ ] Push notifications via FCM
- [ ] Full-text search (Algolia or similar)
- [ ] Firestore pagination
- [ ] iOS home screen widget
