#!/usr/bin/env python3
"""
Airport Routes - Find all destinations served by an airport.

Uses Amadeus Airport Routes API to discover where you can fly from
a given airport.

Usage:
    python3 routes.py --airport LHR
    python3 routes.py --airport LHR --max 50
"""

import argparse
import json
import os
import sys

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def get_airport_routes(airport_code: str, max_results: int = 100) -> dict:
    """
    Get all destinations served by an airport.
    
    Args:
        airport_code: IATA airport code (e.g., "LHR")
        max_results: Maximum number of destinations to return
    
    Returns:
        API response with destination airports
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    params = {"max": max_results}
    
    response = requests.get(
        f"{base_url}/v1/airport/direct-destinations",
        headers={"Authorization": f"Bearer {token}"},
        params={"departureAirportCode": airport_code.upper(), **params}
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def format_human(data: dict) -> str:
    """Format results in human-readable form."""
    if "error" in data:
        return f"❌ Error: {json.dumps(data['error'], indent=2)}"
    
    destinations = data.get("data", [])
    if not destinations:
        return "No routes found from that airport."
    
    lines = [f"🌍 {len(destinations)} direct destinations:\n"]
    
    for dest in destinations:
        iata = dest.get("iataCode", "???")
        name = dest.get("name", "")
        dest_type = dest.get("type", "")
        
        if name:
            lines.append(f"✈️  {iata} - {name}")
        else:
            lines.append(f"✈️  {iata}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find destinations from an airport")
    parser.add_argument("--airport", "-a", required=True, help="Airport IATA code")
    parser.add_argument("--max", type=int, default=100, help="Maximum results (default: 100)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    result = get_airport_routes(args.airport, args.max)
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
