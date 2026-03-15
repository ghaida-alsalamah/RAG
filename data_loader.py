"""
data_loader.py
Loads and preprocesses the three Riyadh datasets (hotels, restaurants, cafes)
and converts each row into a human-readable text document for the RAG pipeline.
"""

import pandas as pd
import numpy as np
import os


# ─── District Estimation from Coordinates ────────────────────────────────────

def get_district(lat, lon):
    """Approximate Riyadh neighbourhood from lat/lon coordinates."""
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return "Riyadh"

    if pd.isna(lat) or pd.isna(lon):
        return "Riyadh"

    if lat > 24.79:
        if lon < 46.65:
            return "Al Nakheel, North Riyadh"
        elif lon < 46.72:
            return "Al Woroud, North Riyadh"
        else:
            return "Al Hamra, North Riyadh"
    elif lat > 24.74:
        if lon < 46.64:
            return "Al Sulimaniyah, Riyadh"
        elif lon < 46.70:
            return "Al Olaya, Riyadh"
        elif lon < 46.74:
            return "Al Rawdah, Riyadh"
        else:
            return "Al Malaz, Riyadh"
    elif lat > 24.68:
        if lon < 46.64:
            return "Al Hamra, Central Riyadh"
        elif lon < 46.70:
            return "Al Muruj, Central Riyadh"
        elif lon < 46.74:
            return "Al Malaz, Central Riyadh"
        else:
            return "Al Naseem, East Riyadh"
    elif lat > 24.63:
        if lon < 46.68:
            return "Al Murabba, Central Riyadh"
        elif lon < 46.72:
            return "Al Batha, Central Riyadh"
        else:
            return "Al Naseem, East Riyadh"
    else:
        return "South Riyadh"


def price_category_hotel(price_sar):
    """Convert numeric price (SAR/night) to a human-readable label."""
    price_sar = float(price_sar)
    if price_sar < 400:
        return "budget-friendly"
    elif price_sar < 700:
        return "affordable"
    elif price_sar < 1200:
        return "mid-range"
    elif price_sar < 2000:
        return "upscale"
    else:
        return "luxury"


# ─── Hotels ──────────────────────────────────────────────────────────────────

def load_hotels(filepath):
    """
    Reads Riyadh_Hotels.xlsx.
    Deduplicates by hotel_name (keeps best-rated entry).
    Converts each row to a descriptive text document.
    """
    df = pd.read_excel(filepath)

    # Keep only rows with a name and a price
    df = df.dropna(subset=["hotel_name", "price"])

    # Deduplicate – keep the highest-rated entry per hotel
    df = (
        df.sort_values("rating", ascending=False)
          .drop_duplicates(subset=["hotel_name"])
          .reset_index(drop=True)
    )

    docs = []
    for _, row in df.iterrows():
        name    = str(row["hotel_name"]).strip()
        price   = float(row["price"])
        rating  = float(row["rating"]) if pd.notna(row["rating"]) else None
        lat     = row.get("latitude")
        lon     = row.get("longitude")
        info    = str(row.get("Info", "")) if pd.notna(row.get("Info")) else ""

        district  = get_district(lat, lon)
        price_cat = price_category_hotel(price)
        rating_str = f"{rating}/5" if rating is not None else "not yet rated"

        text = (
            f"{name} is a {price_cat} hotel located in {district}. "
            f"It has an average price of {price:.0f} SAR per night and a guest rating of {rating_str}."
        )
        if info and info.lower() not in ("nan", "none", ""):
            text += f" Amenities include: {info}."

        docs.append({
            "text":           text,
            "type":           "hotel",
            "name":           name,
            "price":          price,
            "price_category": price_cat,
            "rating":         rating,
            "district":       district,
        })

    return docs


# ─── Restaurants ─────────────────────────────────────────────────────────────

# Categories that belong to the café dataset – exclude to avoid duplication
CAFE_CATEGORIES = {
    "Coffee Shop", "Café", "Cafe", "Caf\xe9",
    "Tea Room", "Juice Bar",
}

PRICE_LABELS = {
    "Cheap":         "budget-friendly (under 50 SAR per person)",
    "Moderate":      "moderately priced (50–100 SAR per person)",
    "Expensive":     "upscale (100–200 SAR per person)",
    "Very Expensive": "luxury (200+ SAR per person)",
}


def load_restaurants(filepath, max_docs=2000):
    """
    Reads riyadh_resturants_clean.csv (cp1256 encoding).
    Filters out café-category entries.
    Returns up to max_docs descriptive text documents.
    """
    df = pd.read_csv(filepath, encoding="utf-8")
    df = df.dropna(subset=["name", "categories"])

    # Remove café-type categories (covered separately)
    df = df[~df["categories"].isin(CAFE_CATEGORIES)]

    # Prefer rows that have a rating; sort by rating desc
    rated   = df[df["rating"].notna()].sort_values("rating", ascending=False)
    unrated = df[df["rating"].isna()]

    # Take up to max_docs rows (rated first)
    n_rated   = min(len(rated), max_docs)
    n_unrated = min(len(unrated), max_docs - n_rated)
    df = pd.concat([rated.head(n_rated), unrated.head(n_unrated)], ignore_index=True)

    docs = []
    for _, row in df.iterrows():
        name     = str(row["name"]).strip()
        category = str(row["categories"]).strip()
        price    = str(row.get("price", "")).strip()
        rating   = float(row["rating"]) if pd.notna(row.get("rating")) else None
        lat      = row.get("lat")
        lng      = row.get("lng")

        district   = get_district(lat, lng)
        price_label = PRICE_LABELS.get(price, "moderately priced")
        rating_str  = f"{rating:.1f}/10" if rating is not None else "not yet rated"

        text = (
            f"{name} is a {category} located in {district}. "
            f"It is {price_label} with a customer rating of {rating_str}."
        )

        docs.append({
            "text":     text,
            "type":     "restaurant",
            "name":     name,
            "category": category,
            "price":    price,
            "rating":   rating,
            "district": district,
        })

    return docs


# ─── Cafes ───────────────────────────────────────────────────────────────────

def load_cafes(filepath, min_reviews=3):
    """
    Reads riyadh_cafes.csv (cp1256 encoding).
    Filters out cafes with very few reviews.
    Converts each row to a descriptive text document.

    Note: the dataset uses 'lan' for latitude and 'lon' for longitude.
    """
    df = pd.read_csv(filepath, encoding="utf-8")
    df = df.dropna(subset=["coffeeName"])
    df = df[df["rating_count"] >= min_reviews].reset_index(drop=True)

    docs = []
    for _, row in df.iterrows():
        name   = str(row["coffeeName"]).strip()
        rating = float(row["rating"])          if pd.notna(row.get("rating"))       else None
        count  = int(row["rating_count"])      if pd.notna(row.get("rating_count")) else 0
        is24h  = bool(row.get("24_hours", False))
        lat    = row.get("lan")   # note swapped col names in source file
        lon    = row.get("lon")

        district   = get_district(lat, lon)
        rating_str = f"{rating}/5" if rating is not None else "not yet rated"
        hours_str  = "open 24 hours a day" if is24h else "standard operating hours"

        location = district if "Riyadh" in district else f"{district}, Riyadh"
        text = (
            f"{name} is a cafe in {location}. "
            f"It has a rating of {rating_str} based on {count} reviews "
            f"and operates {hours_str}."
        )

        docs.append({
            "text":     text,
            "type":     "cafe",
            "name":     name,
            "rating":   rating,
            "count":    count,
            "is_24h":   is24h,
            "district": district,
        })

    return docs


# ─── Combined Loader ─────────────────────────────────────────────────────────

def load_all(data_dir=".", max_restaurants=2000):
    """
    Loads all three datasets and returns a single list of document dicts.
    Each dict has at minimum: {text, type, name, rating, district}
    """
    hotels_path      = os.path.join(data_dir, "Riyadh_Hotels.xlsx")
    restaurants_path = os.path.join(data_dir, "riyadh_resturants_clean.csv")
    cafes_path       = os.path.join(data_dir, "riyadh_cafes.csv")

    print("Loading hotels …")
    hotels = load_hotels(hotels_path)
    print(f"  {len(hotels)} hotel documents")

    print("Loading restaurants …")
    restaurants = load_restaurants(restaurants_path, max_docs=max_restaurants)
    print(f"  {len(restaurants)} restaurant documents")

    print("Loading cafes …")
    cafes = load_cafes(cafes_path)
    print(f"  {len(cafes)} cafe documents")

    all_docs = hotels + restaurants + cafes
    print(f"\nTotal RAG documents: {len(all_docs)}")
    return all_docs


# ─── Quick test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    docs = load_all(".")
    print("\nSample documents:")
    for d in docs[:3]:
        print(" •", d["text"])
    print()
    for d in docs[55:58]:
        print(" •", d["text"])
    print()
    for d in docs[-3:]:
        print(" •", d["text"])
