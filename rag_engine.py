"""
rag_engine.py
Retrieval-Augmented Generation pipeline for GoRiyadh.

Steps:
  1. Build index   – embed all documents with all-MiniLM-L6-v2, store in FAISS
  2. Retrieve      – embed user query, find nearest documents
  3. Generate      – pass retrieved context + question to google/flan-t5-base
"""

import os
import re
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── Constants ───────────────────────────────────────────────────────────────

EMBED_MODEL = "all-MiniLM-L6-v2"
INDEX_DIR   = "rag_index"

PRICE_BUDGET_MAP = {
    # restaurant price strings → rough SAR-per-person ceiling
    "Cheap":         50,
    "Moderate":      100,
    "Expensive":     200,
    "Very Expensive": 9999,
}

# ── Query expansion map ───────────────────────────────────────────────────────
# Appends extra semantic terms to the query before embedding so FAISS finds
# more relevant candidates for common travel intents.
QUERY_EXPANSIONS = {
    "romantic":   "romantic fine dining upscale elegant candlelit dinner date night atmosphere",
    "romance":    "romantic fine dining upscale elegant date night atmosphere",
    "date":       "romantic upscale restaurant elegant quiet intimate",
    "studying":   "quiet calm cafe study work laptop wifi peaceful cozy",
    "study":      "quiet calm cafe study work laptop wifi peaceful cozy",
    "work":       "cafe work laptop wifi quiet productive",
    "family":     "family friendly restaurant kids children spacious welcoming",
    "kids":       "family friendly restaurant children play area",
    "budget":     "cheap affordable budget-friendly low cost value meal",
    "cheap":      "cheap affordable budget low price value",
    "luxury":     "luxury premium upscale high-end fine dining five star hotel resort",
    "luxurious":  "luxury premium upscale high-end elegant five star",
    "hotel":      "hotel accommodation stay room night Riyadh",
    "breakfast":  "cafe breakfast morning brunch early",
    "brunch":     "cafe brunch breakfast morning",
    "lunch":      "restaurant lunch midday meal",
    "dinner":     "restaurant dinner evening meal",
    "late":       "cafe open late night 24 hours",
    "coffee":     "specialty coffee third wave espresso barista cafe",
    "saudi":      "traditional saudi arabian local cuisine",
    "arabic":     "arabic traditional local cuisine food",
    "italian":    "italian pizza pasta cuisine restaurant",
    "japanese":   "japanese sushi ramen cuisine restaurant",
    "رومانسي":    "رومانسي عشاء فاخر أجواء هادئة راقي romantic fine dining",
    "رومانسية":   "مطعم رومانسي راقي أجواء هادئة عشاء romantic restaurant",
    "دراسة":      "مقهى هادئ للدراسة واي فاي quiet cafe study wifi",
    "عائلي":      "مطعم عائلي مناسب للأطفال family restaurant kids",
    "فطور":       "مقهى فطور صباحي cafe breakfast morning",
    "غداء":       "مطعم غداء وجبة restaurant lunch meal",
    "عشاء":       "مطعم عشاء مساء restaurant dinner evening",
    "فاخر":       "فاخر راقي مطعم فندق luxury upscale hotel restaurant",
    "رخيص":       "رخيص اقتصادي قليل التكلفة cheap budget affordable",
    # Arabic type keywords → English so FAISS matches English-language documents
    "فندق":       "hotel accommodation stay room Riyadh",
    "فنادق":      "hotels accommodation stay room Riyadh",
    "مطعم":       "restaurant food dining eat Riyadh",
    "مطاعم":      "restaurants food dining eat Riyadh",
    "مقهى":       "cafe coffee shop study Riyadh",
    "مقاهي":      "cafes coffee shops Riyadh",
    "قهوة":       "coffee cafe specialty espresso Riyadh",
    "إقامة":      "hotel accommodation stay room Riyadh",
    "أكل":        "restaurant food eat dining Riyadh",
    "وجبة":       "restaurant meal food dining",
    "تقييم":      "rating highly rated best top Riyadh",
    "ميزانية":    "budget affordable cheap price Riyadh",
    "شمال":       "north Riyadh Al Nakheel Al Yasmin",
    "جنوب":       "south Riyadh",
    "وسط":        "central Riyadh Al Olaya",
}


# ─── RAGEngine class ─────────────────────────────────────────────────────────

class RAGEngine:
    """
    Encapsulates:
      - Sentence-transformer embedder (all-MiniLM-L6-v2)
      - FAISS flat L2 index
      - Flan-T5 language model for answer generation
    """

    def __init__(self):
        self.embedder = None
        self.index    = None
        self.metadata = []   # list of dicts (one per document)

    # ── Model loading ────────────────────────────────────────────────────────

    def load_embedder(self):
        if self.embedder is None:
            print(f"Loading embedding model ({EMBED_MODEL}) …")
            self.embedder = SentenceTransformer(EMBED_MODEL)

    # ── Index building & persistence ─────────────────────────────────────────

    def build_index(self, documents, batch_size=64):
        """
        documents : list of dicts, each must have a 'text' key.
        Embeds all texts and stores them in a FAISS IndexFlatL2.
        """
        self.load_embedder()
        self.metadata = documents
        texts = [d["text"] for d in documents]

        print(f"Encoding {len(texts)} documents …")
        embeddings = self.embedder.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
        ).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        print(f"FAISS index built  ({self.index.ntotal} vectors, dim={dim})")

    def save_index(self, path=INDEX_DIR):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"Index saved to '{path}/'")

    def load_index(self, path=INDEX_DIR):
        idx_path  = os.path.join(path, "index.faiss")
        meta_path = os.path.join(path, "metadata.pkl")
        if not os.path.exists(idx_path):
            raise FileNotFoundError(f"No saved index found at '{path}/'")
        self.index = faiss.read_index(idx_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"Index loaded from '{path}/'  ({self.index.ntotal} vectors)")

    def index_ready(self):
        return self.index is not None and len(self.metadata) > 0

    # ── Retrieval ─────────────────────────────────────────────────────────────

    @staticmethod
    def _expand_query(query: str) -> str:
        """Append domain-specific expansion terms based on keywords in the query."""
        q_lower = query.lower()
        extras = []
        for keyword, expansion in QUERY_EXPANSIONS.items():
            if keyword in q_lower and expansion not in extras:
                extras.append(expansion)
        if extras:
            return query + " " + " ".join(extras)
        return query

    def retrieve(
        self,
        query,
        top_k=5,
        filter_type=None,
        max_budget=None,
        price_tiers=None,
        district_hint=None,
        _k_override=None,
    ):
        """
        Semantic search over the FAISS index with:
          - Query expansion for better intent matching
          - Large candidate pool (top_k * 20) before filtering
          - Rating-boosted re-ranking (60% semantic + 40% rating)
          - Optional district_hint to boost nearby results

        Parameters
        ----------
        query        : user question string
        top_k        : number of results to return after filtering
        filter_type  : 'hotel' | 'restaurant' | 'cafe' | None
        max_budget   : numeric SAR ceiling
        price_tiers  : list of allowed price strings e.g. ['Expensive','Very Expensive']
        district_hint: district name string — boosts results from that district
        """
        self.load_embedder()

        # 1. Expand query with semantic intent terms
        expanded = self._expand_query(query)
        query_emb = self.embedder.encode(
            [expanded], convert_to_numpy=True
        ).astype("float32")

        # 2. Large candidate pool — bigger when price tier filtering is active
        # (price tiers are rare, so we need to cast a wider net)
        if _k_override:
            k_search = min(self.index.ntotal, _k_override)
        elif price_tiers:
            k_search = min(self.index.ntotal, max(top_k * 40, 250))
        else:
            k_search = min(self.index.ntotal, max(top_k * 15, 80))
        distances, indices = self.index.search(query_emb, k_search)

        # Build candidates — guard against FAISS -1 padding indices
        raw_indices  = indices[0].tolist()
        raw_dists    = distances[0].tolist()
        max_dist     = max(raw_dists) if raw_dists else 1.0
        if max_dist == 0:
            max_dist = 1.0

        candidates = []
        for idx, dist in zip(raw_indices, raw_dists):
            if idx < 0 or idx >= len(self.metadata):   # skip invalid
                continue
            sem_score = 1.0 - (dist / max_dist)
            candidates.append((self.metadata[idx], sem_score))

        # 3. Apply filters
        # ── Type filter ──────────────────────────────────────────────────────
        if filter_type:
            candidates = [(r, s) for r, s in candidates if r.get("type") == filter_type]

        # ── Budget filter ────────────────────────────────────────────────────
        if max_budget is not None:
            filtered = []
            for r, s in candidates:
                rtype = r.get("type")
                price = r.get("price")
                if rtype == "hotel":
                    if isinstance(price, (int, float)) and price <= max_budget:
                        filtered.append((r, s))
                elif rtype == "restaurant":
                    ceiling = PRICE_BUDGET_MAP.get(str(price), 100)
                    if ceiling <= max_budget:
                        filtered.append((r, s))
                else:
                    filtered.append((r, s))
            candidates = filtered

        # ── Price tier filter (restaurants only — hotels use numeric prices) ──
        if price_tiers:
            tiered = [(r, s) for r, s in candidates
                      if r.get("type") == "hotel"
                      or str(r.get("price", "")) in price_tiers]
            candidates = tiered if tiered else candidates  # fallback if no match

        # 4. Rating-boosted re-ranking + optional district boost (pure Python)
        ratings = []
        for r, _ in candidates:
            try:
                ratings.append(float(r.get("rating") or 0))
            except (ValueError, TypeError):
                ratings.append(0.0)

        max_rating   = max(ratings) if ratings else 1.0
        min_rating   = min(ratings) if ratings else 0.0
        rating_range = (max_rating - min_rating) or 1.0

        scored = []
        for (r, sem_score), raw_rating in zip(candidates, ratings):
            norm_rating = (raw_rating - min_rating) / rating_range
            combined    = 0.60 * sem_score + 0.40 * norm_rating
            # Boost docs in the hinted district (e.g. follow-up "near it" context)
            if district_hint:
                doc_district = str(r.get("district", "")).lower()
                if district_hint.lower() in doc_district:
                    combined += 0.20
            scored.append((r, combined))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored[:top_k]]

    # ── Generation ────────────────────────────────────────────────────────────

    def translate_to_arabic(self, text: str) -> str:
        """Translate an English string to Arabic using Groq."""
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key or not text.strip():
            return text
        try:
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Translate the following text to Arabic. Return only the translated text, nothing else."},
                    {"role": "user", "content": text},
                ],
                max_tokens=400,
                temperature=0.1,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return text

    @staticmethod
    def _dedup_paragraphs(text: str) -> str:
        """Remove duplicate sentences/paragraphs from LLM output."""
        seen = set()
        out  = []
        for para in text.split("\n"):
            key = para.strip().lower()
            if not key:
                out.append(para)
                continue
            if key not in seen:
                seen.add(key)
                out.append(para)
        return "\n".join(out).strip()

    def generate(self, query, docs, max_new_tokens=150, arabic_mode=False, history=None):
        """
        Generate a response using Groq (Llama 3.3 70B) with retrieved docs as context.
        Falls back to template if Groq is unavailable.
        """
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return self._arabic_template(query, docs) if arabic_mode else self._english_template(query, docs)

        # Build context from retrieved docs
        context_lines = []
        for d in docs[:6]:
            name     = d.get("name", "")
            ptype    = d.get("type", "")
            district = d.get("district", "")
            rating   = d.get("rating", "")
            price    = d.get("price", "")
            desc     = d.get("text", "")[:200]
            extras   = []
            if d.get("category"):
                extras.append(f"cuisine: {d['category']}")
            if d.get("is_24h"):
                extras.append("open 24 hours")
            if d.get("price_category"):
                extras.append(f"tier: {d['price_category']}")
            extra_str = (", " + ", ".join(extras)) if extras else ""
            context_lines.append(
                f"- {name} ({ptype}, {district}, rating: {rating}, price: {price}{extra_str}): {desc}"
            )
        context = "\n".join(context_lines)

        lang_instruction = (
            "Respond in Arabic." if arabic_mode
            else "Respond in English."
        )

        system_prompt = (
            "You are GoRiyadh, a friendly and knowledgeable AI travel assistant for Riyadh, Saudi Arabia. "
            "You help visitors discover the best cafes, restaurants, and hotels in the city. "
            "Use the provided context as your primary source — only recommend places listed there. "
            "You may use your general knowledge to add helpful details about atmosphere, cuisine style, "
            "or practical tips not in the data (e.g. dress code, best time to visit, ambiance). "
            "\n\nFormatting rules — always follow these:\n"
            "- Start with a short warm intro sentence (1 line).\n"
            "- List each recommended place as a bullet point using '- '.\n"
            "- For each place use: **Place Name** 📍 District ⭐ Rating 💰 Price — then one short sentence about it.\n"
            "- After the list, add a brief closing tip or question (1 line).\n"
            "- Use **bold** only for place names.\n"
            "- Keep the total response under 200 words.\n"
            f"{lang_instruction}"
        )

        user_prompt = (
            f"Context — retrieved places from our database:\n{context}\n\n"
            f"Visitor question: {query}\n\n"
            "Answer naturally based on the context above."
        )

        try:
            client = Groq(api_key=api_key)

            # Build message list: system + prior turns (last 6) + current user turn
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for turn in history[-6:]:
                    role = turn.get("role", "user")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": turn.get("content", "")})
            messages.append({"role": "user", "content": user_prompt})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=400,
                temperature=0.55,
                frequency_penalty=0.5,   # prevents repeated sentences
                presence_penalty=0.3,    # encourages covering different places
            )
            raw = response.choices[0].message.content.strip()
            return self._dedup_paragraphs(raw)
        except Exception as e:
            print(f"[Groq error] {e}")
            return self._arabic_template(query, docs) if arabic_mode else self._english_template(query, docs)

    def _english_template(self, query, docs):
        """Build a clear, readable English recommendation answer from retrieved docs."""
        if not docs:
            return "I couldn't find any places matching your request. Try a different search."

        type_labels = {"hotel": "Hotel", "restaurant": "Restaurant", "cafe": "Café"}
        price_labels = {
            "Cheap": "Budget-friendly",
            "Moderate": "Moderate pricing",
            "Expensive": "Upscale",
            "Very Expensive": "Luxury",
        }

        # Build intro based on detected type
        types = list({d.get("type", "") for d in docs if d.get("type")})
        if len(types) == 1:
            label = {"hotel": "hotels", "restaurant": "restaurants", "cafe": "cafés"}.get(types[0], "places")
            intro = f"Here are some great {label} in Riyadh for you:\n\n"
        else:
            intro = "Here are some top recommendations in Riyadh:\n\n"

        lines = []
        for doc in docs[:5]:
            name     = doc.get("name", "Unknown")
            district = doc.get("district", "Riyadh")
            rating   = doc.get("rating")
            ptype    = doc.get("type", "")
            price    = doc.get("price")

            parts = [f"{name}"]
            if district:
                parts.append(f"📍 {district}")
            if rating:
                try:
                    parts.append(f"⭐ {float(rating):.1f}")
                except (ValueError, TypeError):
                    pass
            if ptype == "hotel" and isinstance(price, (int, float)) and price > 0:
                parts.append(f"~{price:.0f} SAR/night")
            elif isinstance(price, str) and price in price_labels:
                parts.append(price_labels[price])

            lines.append("• " + "  ·  ".join(parts))

        return intro + "\n".join(lines)

    def _arabic_template(self, query, docs):
        """Build a structured Arabic recommendation answer from retrieved docs."""
        type_ar = {"hotel": "فندق", "restaurant": "مطعم", "cafe": "مقهى"}
        lines = []
        for doc in docs[:5]:
            name     = doc.get("name", "")
            district = doc.get("district", "الرياض")
            rating   = doc.get("rating")
            ptype    = doc.get("type", "")
            price    = doc.get("price")

            label = type_ar.get(ptype, "مكان")
            r_str = f"، التقييم: {rating}" if rating else ""
            p_str = ""
            if ptype == "hotel" and isinstance(price, (int, float)):
                p_str = f"، السعر: {price:.0f} ريال/ليلة"
            elif ptype == "restaurant" and isinstance(price, str) and price:
                price_map_ar = {"Cheap": "رخيص", "Moderate": "متوسط",
                                "Expensive": "غالي", "Very Expensive": "فاخر"}
                p_str = f"، السعر: {price_map_ar.get(price, price)}"

            lines.append(f"• {label}: {name} — {district}{r_str}{p_str}")

        result = "إليك أفضل الأماكن المقترحة في الرياض:\n\n" + "\n".join(lines)
        return result

    # ── Main query method ─────────────────────────────────────────────────────

    def query(
        self,
        question,
        top_k=5,
        filter_type=None,
        max_budget=None,
        arabic_mode=False,
        price_tiers=None,
        history=None,
        district_hint=None,
    ):
        """
        Full RAG pipeline: retrieve + generate.

        Returns
        -------
        answer : str  – generated natural-language response
        docs   : list – retrieved document metadata dicts
        """
        docs = self.retrieve(
            question,
            top_k=top_k,
            filter_type=filter_type,
            max_budget=max_budget,
            price_tiers=price_tiers,
            district_hint=district_hint,
        )
        # Fallback 1: too few results → drop price/budget constraints, keep type
        if len(docs) < max(2, top_k // 2) and (max_budget or price_tiers):
            docs = self.retrieve(question, top_k=top_k, filter_type=filter_type,
                                 district_hint=district_hint)
        # Fallback 2: still too few → widen candidate pool, keep type filter
        if len(docs) < 2 and filter_type:
            docs = self.retrieve(question, top_k=top_k, filter_type=filter_type,
                                 district_hint=district_hint, _k_override=400)
        # Fallback 3: last resort → drop all filters
        if len(docs) < 2 and filter_type:
            docs = self.retrieve(question, top_k=top_k, district_hint=district_hint)
        if not docs:
            msg = (
                "عذراً، لم أجد أماكن تطابق معاييرك. حاول تعديل الفلاتر."
                if arabic_mode else
                "Sorry, I couldn't find any places matching your criteria. "
                "Try adjusting your budget or removing filters."
            )
            return msg, []
        answer = self.generate(question, docs, arabic_mode=arabic_mode, history=history)
        return answer, docs

    # ── Itinerary ─────────────────────────────────────────────────────────────

    # Five themed plan templates — each has distinct morning/afternoon/evening queries
    _PLAN_THEMES = [
        {
            "theme": "Relaxed Day",
            "morning_q":   "cozy quiet cafe for morning coffee or breakfast",
            "afternoon_q": "traditional Arabic cuisine family restaurant lunch",
            "evening_q":   "relaxing lounge cafe evening shisha or tea",
        },
        {
            "theme": "Trendy Explorer",
            "morning_q":   "specialty coffee third wave roastery modern cafe",
            "afternoon_q": "international fusion restaurant trendy upscale",
            "evening_q":   "night cafe popular young crowd vibrant atmosphere",
        },
        {
            "theme": "Family Outing",
            "morning_q":   "family-friendly breakfast cafe kids welcome",
            "afternoon_q": "large family restaurant Saudi food buffet",
            "evening_q":   "dessert cafe ice cream sweets family evening",
        },
        {
            "theme": "Budget Smart",
            "morning_q":   "affordable cheap cafe quick coffee breakfast",
            "afternoon_q": "budget cheap restaurant good value meal",
            "evening_q":   "inexpensive cafe snacks light evening drinks",
        },
        {
            "theme": "Premium Experience",
            "morning_q":   "premium luxury specialty coffee artisan roastery",
            "afternoon_q": "fine dining upscale restaurant gourmet experience",
            "evening_q":   "hotel lounge bar premium cocktails evening",
        },
    ]

    # Estimated cost per slot type when no price data available (SAR)
    _SLOT_EST = {"cafe": 35, "restaurant": 80}

    def generate_multiple_itineraries(self, budget=None, n=5):
        """
        Generate n distinct day plans, each budget-aware.

        budget : total daily SAR (split ~20% morning cafe, 45% restaurant,
                 20% evening cafe, 15% misc)

        Returns list of dicts:
          { theme, slots:[{period,type,doc}], estimated_cost }
        """
        rest_budget = int(budget * 0.45) if budget else None

        plans = []
        for i, tmpl in enumerate(self._PLAN_THEMES[:n]):
            # Fetch a small pool per slot, pick different index per plan
            morning_pool = self.retrieve(
                tmpl["morning_q"], top_k=8, filter_type="cafe"
            )
            afternoon_pool = self.retrieve(
                tmpl["afternoon_q"], top_k=8,
                filter_type="restaurant", max_budget=rest_budget
            )
            evening_pool = self.retrieve(
                tmpl["evening_q"], top_k=8, filter_type="cafe"
            )

            def pick(pool, idx):
                if not pool:
                    return None
                return pool[idx % len(pool)]

            morning   = pick(morning_pool,   i)
            afternoon = pick(afternoon_pool, i)
            evening   = pick(evening_pool,   (i + 2) % max(len(evening_pool), 1))

            slots = []
            if morning:
                slots.append({"period": "Morning",   "type": "cafe",       "doc": morning})
            if afternoon:
                slots.append({"period": "Afternoon", "type": "restaurant", "doc": afternoon})
            if evening:
                slots.append({"period": "Evening",   "type": "cafe",       "doc": evening})

            # Estimate total cost
            cost = 0
            for s in slots:
                doc   = s["doc"]
                ptype = doc.get("type", "cafe")
                price = doc.get("price")
                if ptype == "restaurant":
                    cost += PRICE_BUDGET_MAP.get(str(price), self._SLOT_EST["restaurant"])
                else:
                    cost += self._SLOT_EST["cafe"]

            plans.append({
                "theme":          tmpl["theme"],
                "slots":          slots,
                "estimated_cost": cost,
            })

        return plans

    # Keep old method as alias (used nowhere externally, but safe to keep)
    def generate_itinerary(self, budget=None):
        plans = self.generate_multiple_itineraries(budget=budget, n=1)
        if not plans:
            return []
        return [(s["period"], s["type"].capitalize(), s["doc"])
                for s in plans[0]["slots"]]

    # ── Budget extraction helper ──────────────────────────────────────────────

    @staticmethod
    def extract_budget(text):
        """
        Tries to extract a numeric SAR budget from a free-text question.
        Returns float or None.
        """
        patterns = [
            r"(\d[\d,]*)\s*sar",
            r"budget\s+(?:of\s+)?(\d[\d,]*)",
            r"(\d[\d,]*)\s*riyal",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return float(m.group(1).replace(",", ""))
        return None

    @staticmethod
    def detect_ambiance(text):
        """
        Detects upscale/romantic intent and returns required price tiers.
        Returns a list of allowed price strings, or None if no constraint.
        """
        t = text.lower()
        upscale_keywords = [
            "romantic", "romance", "date night", "anniversary", "fine dining",
            "upscale", "luxury restaurant", "special occasion", "elegant",
            "رومانسي", "رومانسية", "فاخر", "فاخرة", "راقي", "راقية",
            "عشاء رومانسي", "مناسبة خاصة",
        ]
        if any(k in t for k in upscale_keywords):
            return ["Expensive", "Very Expensive"]
        return None

    @staticmethod
    def detect_type(text):
        """
        Infers requested place type from question keywords.
        Returns 'hotel' | 'restaurant' | 'cafe' | None.
        """
        t = text.lower()
        if any(k in t for k in ["hotel", "stay", "accommodation", "room", "فندق", "إقامة"]):
            return "hotel"
        if any(k in t for k in ["restaurant", "food", "eat", "lunch", "dinner", "meal", "cuisine", "مطعم", "أكل"]):
            return "restaurant"
        if any(k in t for k in ["cafe", "coffee", "study", "work", "breakfast", "tea", "latte", "espresso", "مقهى", "قهوة"]):
            return "cafe"
        return None


# ─── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from data_loader import load_all

    engine = RAGEngine()

    # Build or load index
    if os.path.exists(os.path.join(INDEX_DIR, "index.faiss")):
        engine.load_index()
    else:
        docs = load_all(".")
        engine.build_index(docs)
        engine.save_index()

    # Test queries
    questions = [
        "Recommend a quiet cafe for studying in Riyadh",
        "Suggest a family restaurant in North Riyadh",
        "Find a hotel with a budget of 800 SAR",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        budget     = engine.extract_budget(q)
        place_type = engine.detect_type(q)
        answer, docs = engine.query(q, top_k=3, filter_type=place_type, max_budget=budget)
        print(f"A: {answer}")
        print("Retrieved:")
        for d in docs:
            print(f"  [{d['type']}] {d['name']} – {d.get('district','')}")