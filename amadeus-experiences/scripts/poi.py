#!/usr/bin/env python3
"""
Points of Interest - Find attractions and landmarks.

Uses Amadeus Points of Interest API to discover tourist
attractions, landmarks, and notable places.

Usage:
    python3 poi.py --lat 48.8566 --lng 2.3522
    python3 poi.py --city "Barcelona" --category SIGHTS
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token, get_base_url

# POI Categories
CATEGORIES = [
    "SIGHTS",        # Tourist attractions
    "NIGHTLIFE",     # Bars, clubs
    "RESTAURANT",    # Places to eat
    "SHOPPING",      # Shopping areas
]

# Common city coordinates
CITY_COORDS = {
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "barcelona": (41.3851, 2.1734),
    "rome": (41.9028, 12.4964),
    "amsterdam": (52.3676, 4.9041),
    "berlin": (52.5200, 13.4050),
    "madrid": (40.4168, -3.7038),
    "lisbon": (38.7223, -9.1393),
    "new york": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503),
    "dubai": (25.2048, 55.2708),
}


def search_poi(
    latitude: float,
    longitude: float,
    radius: int = 2,
    categories: list = None
) -> dict:
    """
    Search for points of interest near a location.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius: Search radius in km (default: 2, max: 20)
        categories: List of categories to filter by
    
    Returns:
        API response with POIs
    """
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius
    }
    
    if categories:
        params["categories"] = ",".join(categories)
    
    response = requests.get(
        f"{base_url}/v1/reference-data/locations/pois",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def search_poi_by_square(
    north: float,
    south: float,
    east: float,
    west: float,
    categories: list = None
) -> dict:
    """Search for POIs within a geographic square."""
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    params = {
        "north": north,
        "south": south,
        "east": east,
        "west": west
    }
    
    if categories:
        params["categories"] = ",".join(categories)
    
    response = requests.get(
        f"{base_url}/v1/reference-data/locations/pois/by-square",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def format_human(data: dict) -> str:
    """Format results in human-readable form."""
    if "error" in data:
        return f"❌ Error: {json.dumps(data['error'], indent=2)}"
    
    pois = data.get("data", [])
    if not pois:
        return "No points of interest found."
    
    lines = [f"📍 Found {len(pois)} points of interest:\n"]
    
    category_emoji = {
        "SIGHTS": "🏛️",
        "NIGHTLIFE": "🌙",
        "RESTAURANT": "🍽️",
        "SHOPPING": "🛍️",
    }
    
    for poi in pois[:25]:
        name = poi.get("name", "Unknown")
        category = poi.get("category", "")
        rank = poi.get("rank", "")
        
        # Tags
        tags = poi.get("tags", [])
        tags_str = ", ".join(tags[:3]) if tags else ""
        
        emoji = category_emoji.get(category, "📍")
        
        lines.append(f"{emoji} {name}")
        if tags_str:
            lines.append(f"   🏷️ {tags_str}")
        if rank:
            lines.append(f"   📊 Rank: {rank}")
        lines.append("")
    
    if len(pois) > 25:
        lines.append(f"... and {len(pois) - 25} more places")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search for points of interest")
    
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lng", type=float, help="Longitude")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--radius", type=int, default=2, help="Search radius in km (max 20)")
    parser.add_argument("--category", choices=CATEGORIES, action="append",
                        help="Filter by category (can repeat)")
    
    # Square search
    parser.add_argument("--north", type=float)
    parser.add_argument("--south", type=float)
    parser.add_argument("--east", type=float)
    parser.add_argument("--west", type=float)
    
    parser.add_argument("--format", choices=["json", "human"], default="json")
    
    args = parser.parse_args()
    
    categories = args.category if args.category else None
    
    # Square search
    if args.north and args.south and args.east and args.west:
        result = search_poi_by_square(args.north, args.south, args.east, args.west, categories)
    # Coordinate search
    elif args.lat and args.lng:
        result = search_poi(args.lat, args.lng, args.radius, categories)
    # City search
    elif args.city:
        city_lower = args.city.lower()
        if city_lower in CITY_COORDS:
            lat, lng = CITY_COORDS[city_lower]
            result = search_poi(lat, lng, args.radius, categories)
        else:
            print(f"Unknown city. Known: {', '.join(CITY_COORDS.keys())}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
