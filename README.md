# Jloset — AI-Powered Smart Wardrobe Styler

> Upload any garment from your wardrobe and get instant curated outfit ideas with pairings, colour palettes, and accessory suggestions.

---

## Features

- **Garment upload** — drag-and-drop or browse; supports PNG, JPG, WEBP
- **Auto-categorisation** — detects clothing type (top, bottom, dress, jacket, shoes, bag) from the filename
- **9+ outfit suggestions per upload** — each with a title, style vibe, occasion, season, pair-with item, accessories, and a colour palette
- **Style filtering** — filter results by vibe: Casual, Formal, Trendy, Boho, Minimal, Edgy
- **Save board** — heart any look to save it; revisit your saved outfits anytime
- **Detail modal** — click any card to see the full look breakdown
- **Single-file app** — the entire frontend is embedded in `app.py`; no template folder needed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite (`jloset.db`) |
| Frontend | Vanilla HTML/CSS/JS (embedded in `app.py`) |
| Fonts | Cormorant Garamond, Jost (Google Fonts) |

---

## Project Structure

```
jloset/
├── app.py            # Flask app + embedded frontend + style engine
├── requirements.txt  # Python dependencies
└── jloset.db         # SQLite database (auto-created on first run)
```

---

## Setup & Run

**1. Clone or download the project**

```bash
git clone <your-repo-url>
cd jloset
```

**2. Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
python app.py
```

**5. Open in browser**

```
http://127.0.0.1:5000
```

The SQLite database (`jloset.db`) is created automatically on first run — no setup needed.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a garment image; returns outfit suggestions |
| `POST` | `/api/save` | Toggle save/unsave an outfit |
| `GET` | `/api/saved` | Get all saved outfits |
| `GET` | `/api/saved_ids` | Get IDs of all saved outfits |
| `GET` | `/` | Serve the frontend |

---

## Database Schema

**`garments`** — stores uploaded clothing images (as base64)  
**`outfits`** — stores generated outfit suggestions linked to a garment  
**`saves`** — tracks which outfits the user has saved  

---

## How the Style Engine Works

1. The uploaded image filename is parsed to detect the garment category.
2. A random selection of 9 outfit templates is chosen from a built-in library of 12 curated looks (Golden Hour, Quiet Luxury, Pinterest Mood, etc.).
3. Each look comes with a style vibe, occasion, season, pairing suggestion, accessories list, and a warm-toned colour palette.
4. Outfits are stored in the database and returned to the frontend for display.

---

## Requirements

```
flask>=2.3.0
```

Python 3.8+ recommended.

---

## Author

**Javeria Fatima Asif**  
B.E. Software Engineering — MUET, Pakistan  
[GitHub: javeriafatimaasif](https://github.com/javeriafatimaasif)
