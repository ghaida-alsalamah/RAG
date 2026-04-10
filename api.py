"""
api.py – GoRiyadh FastAPI backend
Wraps the RAG engine and serves the premium frontend.

Run with:
    uvicorn api:app --reload --port 8000
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── Make sure local modules are importable ────────────────────────────────────
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from data_loader import load_all
from rag_engine import RAGEngine, INDEX_DIR

# ── Global engine instance ────────────────────────────────────────────────────
engine: RAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    print("─" * 60)
    print("  GoRiyadh API — initialising RAG engine …")
    print("─" * 60)
    engine = RAGEngine()
    idx_path = str(BASE_DIR / INDEX_DIR)
    if os.path.exists(os.path.join(idx_path, "index.faiss")):
        engine.load_index(idx_path)
    else:
        docs = load_all(str(BASE_DIR))
        engine.build_index(docs)
        engine.save_index(idx_path)
    if hasattr(engine, "load_llm"):
        engine.load_llm()
    if hasattr(engine, "load_translator"):
        engine.load_translator()
    n = len(engine.metadata)
    print(f"  ✅ Ready — {n:,} places indexed")
    print("─" * 60)
    yield


app = FastAPI(title="GoRiyadh API", version="2.0", lifespan=lifespan)


# ── Pydantic models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    filter_type: str | None = None
    max_budget: float | None = None
    arabic_mode: bool | None = None   # None = auto-detect


class ItineraryRequest(BaseModel):
    budget: float | None = None


class ChatMessage(BaseModel):
    role: str    # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages:    list[ChatMessage]
    top_k:       int         = 5
    arabic_mode: bool | None = None   # None = auto-detect


# ── Helper ────────────────────────────────────────────────────────────────────

def _require_engine():
    if not engine or not engine.index_ready():
        raise HTTPException(status_code=503, detail="Engine is still loading — try again in a moment.")


def _serialise(doc: dict) -> dict:
    """Make sure all values are JSON-serialisable."""
    out = {}
    for k, v in doc.items():
        if isinstance(v, float) and (v != v):   # NaN
            out[k] = None
        elif hasattr(v, "item"):                 # numpy scalar
            out[k] = v.item()
        else:
            out[k] = v
    return out


def _serialise_arabic(doc: dict) -> dict:
    """Serialise doc and translate the 'text' field to Arabic."""
    out = _serialise(doc)
    if out.get("text") and hasattr(engine, "translate_to_arabic"):
        try:
            out["text"] = engine.translate_to_arabic(out["text"])
        except Exception:
            pass  # fall back to English if translation fails
    return out


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    _require_engine()
    meta = engine.metadata
    return {
        "total":       len(meta),
        "hotels":      sum(1 for d in meta if d["type"] == "hotel"),
        "restaurants": sum(1 for d in meta if d["type"] == "restaurant"),
        "cafes":       sum(1 for d in meta if d["type"] == "cafe"),
    }


@app.post("/api/query")
def query(req: QueryRequest):
    _require_engine()
    question = req.question.strip()
    if not question:
        raise HTTPException(400, "question must not be empty")

    # Auto-detect Arabic if caller didn't specify
    is_arabic = req.arabic_mode
    if is_arabic is None:
        is_arabic = any("\u0600" <= c <= "\u06ff" for c in question)

    budget      = req.max_budget or engine.extract_budget(question)
    ftype       = req.filter_type or engine.detect_type(question)
    price_tiers = engine.detect_ambiance(question)

    answer, docs = engine.query(
        question,
        top_k=req.top_k,
        filter_type=ftype,
        max_budget=budget,
        arabic_mode=bool(is_arabic),
        price_tiers=price_tiers,
    )

    serialise = _serialise_arabic if is_arabic else _serialise
    return {
        "answer":      answer,
        "docs":        [serialise(d) for d in docs],
        "arabic_mode": bool(is_arabic),
        "filter_type": ftype,
        "budget":      budget,
    }


@app.get("/api/explore/{place_type}")
def explore(place_type: str, top_k: int = 24):
    _require_engine()
    if place_type not in ("hotel", "restaurant", "cafe"):
        raise HTTPException(400, "place_type must be hotel | restaurant | cafe")

    queries = {
        "hotel":      "best highly rated luxury hotel Riyadh",
        "restaurant": "top rated restaurant Riyadh family food",
        "cafe":       "popular specialty coffee cafe Riyadh",
    }
    docs = engine.retrieve(queries[place_type], top_k=top_k, filter_type=place_type)
    return {"docs": [_serialise(d) for d in docs]}


@app.post("/api/itinerary")
def itinerary(req: ItineraryRequest):
    _require_engine()
    plans = engine.generate_multiple_itineraries(budget=req.budget, n=5)
    serialised = []
    for p in plans:
        serialised.append({
            "theme":          p["theme"],
            "estimated_cost": p["estimated_cost"],
            "slots": [
                {"period": s["period"], "type": s["type"], "doc": _serialise(s["doc"])}
                for s in p["slots"]
            ],
        })
    return {"plans": serialised}


@app.post("/api/chat")
def chat(req: ChatRequest):
    _require_engine()
    if not req.messages:
        raise HTTPException(400, "messages must not be empty")

    # Latest user message
    user_msgs = [m for m in req.messages if m.role == "user"]
    if not user_msgs:
        raise HTTPException(400, "No user message found")
    question = user_msgs[-1].content.strip()

    # Auto-detect Arabic
    is_arabic = req.arabic_mode
    if is_arabic is None:
        is_arabic = any("\u0600" <= c <= "\u06ff" for c in question)

    # Build context from conversation history for filter inheritance
    full_text   = " ".join(m.content for m in req.messages)
    budget      = engine.extract_budget(full_text)
    ftype       = engine.detect_type(question) or engine.detect_type(full_text)
    price_tiers = engine.detect_ambiance(question) or engine.detect_ambiance(full_text)

    history = [{"role": m.role, "content": m.content} for m in req.messages[:-1]]

    answer, docs = engine.query(
        question,
        top_k=req.top_k,
        filter_type=ftype,
        max_budget=budget,
        arabic_mode=bool(is_arabic),
        price_tiers=price_tiers,
        history=history,
    )

    serialise = _serialise_arabic if is_arabic else _serialise
    return {
        "answer":      answer,
        "docs":        [serialise(d) for d in docs],
        "arabic_mode": bool(is_arabic),
        "filter_type": ftype,
        "budget":      budget,
    }


@app.get("/api/map")
def map_data(place_type: str | None = None, limit: int = 400):
    _require_engine()
    meta = engine.metadata
    if place_type and place_type in ("hotel", "restaurant", "cafe"):
        meta = [d for d in meta if d["type"] == place_type]
    # Return first `limit` entries — frontend adds district-based coordinates
    return {"docs": [_serialise(d) for d in meta[:limit]]}


# ── Serve the React-free premium frontend ─────────────────────────────────────

FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Serve index.html for all non-API routes (SPA-style)
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        raise HTTPException(404, "Frontend not built yet")
    return FileResponse(str(index))