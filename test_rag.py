"""
test_rag.py — Interactive RAG terminal tester
Run: python test_rag.py
"""

import os, sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from rag_engine import RAGEngine, INDEX_DIR

print("=" * 60)
print("  GoRiyadh RAG — Interactive Tester")
print("=" * 60)

engine = RAGEngine()
idx_path = str(Path(__file__).parent / INDEX_DIR)

if os.path.exists(os.path.join(idx_path, "index.faiss")):
    engine.load_index(idx_path)
else:
    from data_loader import load_all
    print("Building index from data...")
    docs = load_all(str(Path(__file__).parent))
    engine.build_index(docs)
    engine.save_index(idx_path)

print(f"\n  {len(engine.metadata):,} places indexed. Type your question below.")
print("  Commands: 'quit' to exit | 'debug on/off' | 'reset' to clear history")
print("-" * 60)

debug    = False
history  = []      # conversation turns  [{"role":"user","content":"..."}, ...]
last_docs = []     # docs returned in the last turn

# Keywords that suggest the user is asking about a place mentioned earlier
CONTEXT_WORDS = ["near", "nearby", "close to", "around it", "around there",
                 "next to", "by it", "in the same area", "same district",
                 "قريب", "بالقرب", "نفس المنطقة"]

def extract_district_hint(question: str, prev_docs: list) -> str | None:
    """If question references a previous location, return its district."""
    q = question.lower()
    if not prev_docs:
        return None
    if any(w in q for w in CONTEXT_WORDS):
        # Pick the most common district from previous results
        districts = [d.get("district", "") for d in prev_docs if d.get("district")]
        if districts:
            return Counter(districts).most_common(1)[0][0]
    return None

while True:
    try:
        q = input("\nYou: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        break

    if not q:
        continue
    if q.lower() in ("quit", "exit", "q"):
        print("Bye!")
        break
    if q.lower() == "debug on":
        debug = True
        print("  [debug mode ON]")
        continue
    if q.lower() == "debug off":
        debug = False
        print("  [debug mode OFF]")
        continue
    if q.lower() == "reset":
        history, last_docs = [], []
        print("  [conversation history cleared]")
        continue

    # Detect params
    is_arabic    = any("\u0600" <= c <= "\u06ff" for c in q)
    budget       = engine.extract_budget(q)
    ftype        = engine.detect_type(q)
    price_tiers  = engine.detect_ambiance(q)
    district_hint = extract_district_hint(q, last_docs)

    # For follow-up "near" questions: inherit type from previous if not set
    if district_hint and not ftype and last_docs:
        # If user didn't specify a type, keep it open so both cafes/restaurants show
        pass

    if debug:
        print(f"  [type={ftype}  budget={budget}  tiers={price_tiers}  "
              f"district={district_hint}  arabic={is_arabic}]")

    answer, docs = engine.query(
        q,
        top_k=5,
        filter_type=ftype,
        max_budget=budget,
        arabic_mode=is_arabic,
        price_tiers=price_tiers,
        history=history,
        district_hint=district_hint,
    )

    print(f"\nGoRiyadh: {answer}")

    if debug and docs:
        print("\n  Retrieved docs:")
        for i, d in enumerate(docs, 1):
            print(f"    {i}. [{d['type']}] {d['name']} — {d.get('district','')}  "
                  f"⭐{d.get('rating','')}  💰{d.get('price','')}")

    # Update conversation history (keep last 10 turns to avoid token overflow)
    history.append({"role": "user",      "content": q})
    history.append({"role": "assistant", "content": answer})
    if len(history) > 20:
        history = history[-20:]

    last_docs = docs
