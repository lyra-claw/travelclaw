#!/usr/bin/env python3
"""
Tours & Activities Search - Find things to do at a destination.

Uses Amadeus Tours and Activities API to find experiences,
tours, attractions, and activities by location.

Usage:
    # By coordinates (most reliable)
    python3 activities.py --lat 48.8566 --lng 2.3522 --radius 5
    
    # By city name (uses geocoding)
    python3 activities.py --city "Barcelona"
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token, get_base_url


def search_activities(
    latitude: float,
    longitude: float,
    radius: int = 5
) -> dict:
    """
    Search for tours and activities near a location.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate  
        radius: Search radius in km (default: 5)
    
    Returns:
        API response with activities
    """
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius
    }
    
    response = requests.get(
        f"{base_url}/v1/shopping/activities",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def search_activities_by_square(
    north: float,
    south: float,
    east: float,
    west: float
) -> dict:
    """
    Search for activities within a geographic square.
    
    Args:
        north: Northern latitude boundary
        south: Southern latitude boundary
        east: Eastern longitude boundary
        west: Western longitude boundary
    
    Returns:
        API response with activities
    """
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    params = {
        "north": north,
        "south": south,
        "east": east,
        "west": west
    }
    
    response = requests.get(
        f"{base_url}/v1/shopping/activities/by-square",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def get_activity_details(activity_id: str) -> dict:
    """Get details for a specific activity."""
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    response = requests.get(
        f"{base_url}/v1/shopping/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


# Common city coordinates for convenience
CITY_COORDS = {
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "barcelona": (41.3851, 2.1734),
    "rome": (41.9028, 12.4964),
    "amsterdam": (52.3676, 4.9041),
    "berlin": (52.5200, 13.4050),
    "madrid": (40.4168, -3.7038),
    "lisbon": (38.7223, -9.1393),
    "prague": (50.0755, 14.4378),
    "vienna": (48.2082, 16.3738),
    "new york": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
}


def format_human(data: dict) -> str:
    """Format results in human-readable form."""
    if "error" in data:
        return f"❌ Error: {json.dumps(data['error'], indent=2)}"
    
    activities = data.get("data", [])
    if not activities:
        return "No activities found in this area."
    
    lines = [f"🎯 Found {len(activities)} activities:\n"]
    
    for act in activities[:20]:  # Limit output
        name = act.get("name", "Unknown")
        act_id = act.get("id", "")[:10]
        
        # Price
        price = act.get("price", {})
        amount = price.get("amount", "N/A")
        currency = price.get("currencyCode", "")
        
        # Rating
        rating = act.get("rating", "")
        
        # Description (truncated)
        desc = act.get("shortDescription", "")[:100]
        if len(act.get("shortDescription", "")) > 100:
            desc += "..."
        
        # Pictures
        pictures = act.get("pictures", [])
        has_pics = "📷" if pictures else ""
        
        # Booking link
        booking = act.get("bookingLink", "")
        
        lines.append(f"🎫 {name} {has_pics}")
        if amount != "N/A":
            lines.append(f"   💰 From {currency} {amount}")
        if rating:
            lines.append(f"   ⭐ {rating}")
        if desc:
            lines.append(f"   📝 {desc}")
        lines.append(f"   ID: {act_id}")
        lines.append("")
    
    if len(activities) > 20:
        lines.append(f"... and {len(activities) - 20} more activities")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search for tours and activities")
    
    # Location options
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lng", type=float, help="Longitude")
    parser.add_argument("--city", help="City name (uses built-in coordinates)")
    parser.add_argument("--radius", type=int, default=5, help="Search radius in km")
    
    # Square search
    parser.add_argument("--north", type=float, help="North boundary (for square search)")
    parser.add_argument("--south", type=float, help="South boundary")
    parser.add_argument("--east", type=float, help="East boundary")
    parser.add_argument("--west", type=float, help="West boundary")
    
    # Get specific activity
    parser.add_argument("--id", help="Get details for specific activity ID")
    
    parser.add_argument("--format", choices=["json", "human"], default="json")
    
    args = parser.parse_args()
    
    # Get specific activity
    if args.id:
        result = get_activity_details(args.id)
    # Square search
    elif args.north and args.south and args.east and args.west:
        result = search_activities_by_square(args.north, args.south, args.east, args.west)
    # Coordinate search
    elif args.lat and args.lng:
        result = search_activities(args.lat, args.lng, args.radius)
    # City search
    elif args.city:
        city_lower = args.city.lower()
        if city_lower in CITY_COORDS:
            lat, lng = CITY_COORDS[city_lower]
            result = search_activities(lat, lng, args.radius)
        else:
            print(f"Unknown city: {args.city}")
            print(f"Known cities: {', '.join(CITY_COORDS.keys())}")
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
