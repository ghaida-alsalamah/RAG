"""
fetch_images.py  -  GoRiyadh
Fetches a real photo URL for every hotel/restaurant/cafe using
DuckDuckGo Images (no API key needed).

Output: frontend/place_images.json   { "Place Name": "https://..." }

Run: python fetch_images.py
Time: ~8-12 min for 215 places
"""

import json, pickle, re, time, sys, pathlib, random
from ddgs import DDGS
from ddgs.exceptions import RatelimitException

# ── Config ────────────────────────────────────────────────────────────────────
LIMITS     = {"hotel": 0, "restaurant": 100, "cafe": 100}
BASE_DELAY = 3.5        # seconds between calls
JITTER     = 1.0        # ± random seconds added to delay
RETRIES    = 3          # attempts before giving up on a place
OUT_FILE   = pathlib.Path(__file__).parent / "frontend" / "place_images.json"
META_FILE  = pathlib.Path(__file__).parent / "rag_index"  / "metadata.pkl"

# force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Helpers ───────────────────────────────────────────────────────────────────

ARABIC_RE = re.compile(r'[\u0600-\u06FF]')

def clean(name: str) -> str:
    """Strip parenthetical suffixes (Arabic or English)."""
    s = re.sub(r"\([^)]*\)", "", name).strip()
    return re.sub(r"\s+", " ", s) or name

def is_arabic_only(name: str) -> bool:
    """True if the name contains no Latin letters (pure Arabic)."""
    latin = re.search(r'[A-Za-z]', name)
    return latin is None and bool(ARABIC_RE.search(name))

def queries_for(name: str, ptype: str) -> list[str]:
    """
    Return a list of search queries to try in order.
    - If name has English: try specific name first, then generic fallback.
    - If name is Arabic-only: skip name search, go straight to generic.
    """
    tword = {"hotel": "hotel", "restaurant": "restaurant", "cafe": "cafe interior"}[ptype]
    location = "Riyadh Saudi Arabia"
    generic = f"{tword} {location}"

    cleaned = clean(name)
    if is_arabic_only(cleaned):
        # Arabic-only name — no point searching it, use generic queries
        return [
            generic,
            f"modern {tword} {location}",
        ]
    else:
        return [
            f"{cleaned} {tword} {location}",  # specific
            generic,                            # generic fallback
        ]

def fetch_one(query: str) -> str | None:
    """Try a single query, return image URL or None."""
    for attempt in range(RETRIES):
        try:
            with DDGS() as d:
                hits = list(d.images(query, max_results=4, safesearch="off"))
            for h in hits:
                u = h.get("image", "")
                if u and any(e in u.lower() for e in (".jpg", ".jpeg", ".webp", ".png")):
                    return u
            return hits[0]["image"] if hits else None
        except RatelimitException:
            wait = (attempt + 1) * 8
            print(f"    [rate-limit] waiting {wait}s …")
            time.sleep(wait)
        except Exception as e:
            wait = (attempt + 1) * 4
            print(f"    [error] {e!s:.60} — retrying in {wait}s")
            time.sleep(wait)
    return None

def fetch(name: str, ptype: str) -> str | None:
    """Try each query in order, return first successful URL."""
    for q in queries_for(name, ptype):
        url = fetch_one(q)
        if url:
            return url
        time.sleep(2)  # small pause between fallback attempts
    return None


def sleep_between():
    time.sleep(BASE_DELAY + random.uniform(-JITTER, JITTER))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("GoRiyadh - Image Fetcher")
    print("=" * 58)

    with open(META_FILE, "rb") as f:
        meta = pickle.load(f)
    print(f"Metadata: {len(meta):,} places loaded")

    # Load existing cache so interrupted runs can resume
    cache: dict = {}
    if OUT_FILE.exists():
        cache = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        print(f"Resuming: {len(cache)} images already cached")

    # Sort by rating for restaurants/cafes
    by_type = {
        "hotel":      [d for d in meta if d["type"] == "hotel"],
        "restaurant": sorted([d for d in meta if d["type"] == "restaurant"],
                             key=lambda x: -(x.get("rating") or 0)),
        "cafe":       sorted([d for d in meta if d["type"] == "cafe"],
                             key=lambda x: -(x.get("rating") or 0)),
    }

    queue = []
    for ptype, limit in LIMITS.items():
        queue += [(ptype, d) for d in by_type[ptype][:limit]]

    todo = [(t, d) for t, d in queue if d["name"] not in cache]
    print(f"To fetch: {len(todo)}  |  Already cached: {len(queue)-len(todo)}")
    print("=" * 58)

    ok = fail = 0
    for i, (ptype, doc) in enumerate(todo, 1):
        name  = doc["name"]

        # Truncate for display
        display_name = name[:52] + "…" if len(name) > 52 else name
        print(f"[{i:>3}/{len(todo)}] {ptype:10s}  {display_name}")

        url = fetch(name, ptype)
        if url:
            cache[name] = url
            print(f"          OK  {url[:80]}")
            ok += 1
        else:
            print(f"          FAIL")
            fail += 1

        # Incremental save every 10
        if i % 10 == 0:
            OUT_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            pct = round(i / len(todo) * 100)
            print(f"\n  [saved {len(cache)} entries | {pct}% done]\n")

        sleep_between()

    # Final save
    OUT_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 58)
    print(f"Done!  OK={ok}  FAIL={fail}  TOTAL={len(cache)}")
    print(f"Saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
