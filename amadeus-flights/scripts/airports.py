#!/usr/bin/env python3
"""
Search for airports and cities via Amadeus API.
Useful for finding IATA codes.
"""

import argparse
import json
import sys
import time

import requests

from auth import get_auth_header, get_base_url


def make_request(url: str, params: dict, retries: int = 3) -> dict:
    """Make API request with retry logic."""
    headers = get_auth_header()
    
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        
        if response.status_code == 401:
            raise EnvironmentError("Authentication failed.")
        
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded")


def search_airports(query: str, subtype: str = "AIRPORT,CITY") -> list:
    """Search for airports/cities by keyword."""
    base_url = get_base_url()
    
    params = {
        "keyword": query,
        "subType": subtype,
    }
    
    data = make_request(
        f"{base_url}/v1/reference-data/locations",
        params,
    )
    
    return data.get("data", [])


def format_human(locations: list) -> str:
    """Format locations for human reading."""
    if not locations:
        return "No airports/cities found."
    
    lines = []
    
    for loc in locations[:15]:
        code = loc.get("iataCode", "")
        name = loc.get("name", "").title()
        subtype = loc.get("subType", "")
        city = loc.get("address", {}).get("cityName", "")
        country = loc.get("address", {}).get("countryName", "")
        
        icon = "🏙️" if subtype == "CITY" else "✈️"
        location_str = ", ".join(filter(None, [city, country]))
        
        lines.append(f"{icon}  {code} — {name}")
        if location_str and location_str.lower() != name.lower():
            lines.append(f"    📍 {location_str}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search airports/cities")
    parser.add_argument("--query", "-q", required=True,
                        help="Search query (city name, airport name, etc.)")
    parser.add_argument("--type", choices=["airport", "city", "both"], default="both",
                        help="Location type filter")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format")
    
    args = parser.parse_args()
    
    subtype_map = {
        "airport": "AIRPORT",
        "city": "CITY",
        "both": "AIRPORT,CITY",
    }
    
    try:
        locations = search_airports(args.query, subtype_map[args.type])
        
        if args.format == "human":
            print(format_human(locations))
        else:
            print(json.dumps(locations, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
