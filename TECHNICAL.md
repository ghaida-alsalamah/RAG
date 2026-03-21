# GoRiyadh — Technical Documentation


## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Browser (SPA)                     │
│  HTML + CSS + Vanilla JS  ·  RTL/LTR bilingual      │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼───────────────────────────────┐
│              FastAPI  (api.py)                      │
│  /api/query  /api/explore  /api/itinerary           │
│  /api/stats  /api/map  /api/districts  /api/chat    │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼───────────────────┐
│   RAG Engine        │  │   Groq Cloud API           │
│   rag_engine.py     │  │   llama-3.3-70b-versatile  │
│                     │  └───────────────────────────┘
│  1. Embed query     │
│     (MiniLM-L6-v2)  │
│  2. FAISS search    │
│  3. Re-rank + boost │
│  4. Build prompt    │
│  5. Stream answer   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   FAISS Index       │
│   rag_index/        │
│   4,439 docs        │
│   384-dim vectors   │
└─────────────────────┘
```

---

## Data

| Source | Format | Raw Records | Indexed | Filter Applied |
|--------|--------|-------------|---------|----------------|
| Riyadh Cafes | CSV | 2,609 | **2,384** | min 3 reviews |
| Riyadh Restaurants | CSV | 19,361 | **2,000** | top-rated first, café categories excluded, capped at 2,000 |
| Riyadh Hotels | XLSX | 1,089 | **55** | deduplicated by name, keeps highest-rated entry per hotel |
| **Total** | | **23,059** | **4,439** | |

Data is preprocessed by `data_loader.py` into a unified schema with fields: `name`, `type`, `rating`, `price`, `district`, `description`, `lat`, `lng`.

---

## RAG Pipeline

### 1. Embedding (`rag_engine.py`)
- Model: **`all-MiniLM-L6-v2`** (SentenceTransformers)
- Vector size: **384 dimensions**
- Each document is embedded as: `"{name} {type} {district} {description} {price}"`
- Index stored on disk in `rag_index/` (FAISS + pickle)

### 2. Retrieval
- Index type: **FAISS IndexFlatL2** (exact nearest-neighbour search)
- Default top-k: **60 candidates** retrieved per query
- **Query expansion**: common intent keywords (e.g. "romantic", "studying", "budget") are expanded with semantic synonyms before embedding

### 3. Re-ranking
- Pure Python post-processing on the 60 candidates:
  - **Type filter**: keeps only cafe / restaurant / hotel if specified
  - **Budget filter**: drops places exceeding `max_budget`
  - **Price-tier filter**: matches ambiance level (budget / moderate / upscale)
  - **District boost**: +0.15 score bonus for places in the hinted district
  - **Rating boost**: score weighted by `rating / 5.0`
- Final result trimmed to top-k (default 8 for chat, 24 for explore)

### 4. Generation
- Provider: **Groq Cloud**
- Model: **`llama-3.3-70b-versatile`**
- Language: auto-detected from query (Arabic Unicode range `\u0600–\u06ff`)
- Bilingual prompts: separate system prompts for Arabic and English responses
- Context window: top retrieved docs formatted as bullet list injected into prompt

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/stats` | Total counts of cafes, restaurants, hotels |
| `POST` | `/api/query` | RAG search — returns answer + docs |
| `POST` | `/api/chat` | Conversational AI with session history |
| `GET` | `/api/explore/{type}` | Browse places by type with filters |
| `GET` | `/api/districts` | List distinct districts by place type |
| `POST` | `/api/itinerary` | Generate 5 full-day plans for a budget |
| `GET` | `/api/map` | All places with coordinates for map view |

---

## Frontend

- **Type**: Single-page application (SPA) — no framework, vanilla JS
- **Router**: custom `navigate(page)` function with `history.pushState`
- **Styling**: pure CSS with CSS custom properties for theming
- **Pages**: Home, GoGuide AI (chat), Explore, Map, Plan My Day
- **Bilingual**: English / Arabic with full RTL layout switching (`dir="rtl"` on `<html>`)
- **Theme**: Light / Dark mode via `data-theme="dark"` on `<html>`

### Key Frontend Features
| Feature | Implementation |
|---------|---------------|
| Stat counters | `IntersectionObserver` + `requestAnimationFrame` count-up |
| Scroll reveal | `IntersectionObserver` + CSS `.reveal-up` class |
| Card 3D tilt | `mousemove` → `perspective` + `rotateX/Y` transform |
| Confetti | Dynamically created DOM elements + `@keyframes confettiFall` |
| Progress bar | Fixed `#progressBar` element, width animated via JS |
| Place images | Unsplash pool fallback + real photos from `place_images.json` |
| Compare | Multi-select up to 3 places, side-by-side modal |
| Share | `navigator.share` API with clipboard fallback |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI 0.111+ |
| ASGI server | Uvicorn |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector search | FAISS (CPU) |
| LLM | Groq — Llama 3.3 70B Versatile |
| ML runtime | PyTorch (CPU-only) |
| Data processing | Pandas, OpenPyXL |
| Frontend | HTML5, CSS3, Vanilla JS (ES2020) |
| Deployment | Render.com (Python web service) |

---

## Project Structure

```
GoRiyadh/
├── api.py                  # FastAPI app — all REST endpoints
├── rag_engine.py           # RAG pipeline (embed, retrieve, generate)
├── data_loader.py          # Data ingestion and preprocessing
├── fetch_images.py         # Scrapes real hotel/place images
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
├── rag_index/              # Persisted FAISS index + metadata
├── riyadh_cafes.csv        # 2,609 cafe records
├── riyadh_resturants_clean.csv  # 19,361 restaurant records
├── Riyadh_Hotels.xlsx      # 1,089 hotel records
└── frontend/
    ├── index.html          # Single HTML shell
    ├── app.js              # All JS: router, pages, API calls (~1,550 lines)
    ├── style.css           # All styles: light/dark/RTL (~925 lines)
    ├── hero.jpg            # Hero background (Riyadh night skyline)
    └── place_images.json   # Real place photo URLs cache
```

---

## Deployment

Hosted on **Render.com** as a Python web service.

```yaml
buildCommand: pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt
startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
```

Environment variable required:
- `GROQ_API_KEY` — set manually in Render dashboard

The FAISS index is built once on first startup and cached to disk. Subsequent restarts load from `rag_index/` directly.

---

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variable
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Start the server
uvicorn api:app --reload --port 8000

# 4. Open browser
# http://localhost:8000
```
