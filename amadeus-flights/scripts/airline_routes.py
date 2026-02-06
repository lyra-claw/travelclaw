#!/usr/bin/env python3
"""
Airline Routes - Find all destinations served by an airline.

Uses Amadeus Airline Routes API to discover where a specific
airline flies.

Usage:
    python3 airline_routes.py --airline BA
    python3 airline_routes.py --airline VY --max 50
"""

import argparse
import json
import os
import sys

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def get_airline_routes(airline_code: str, max_results: int = 100) -> dict:
    """
    Get all destinations served by an airline.
    
    Args:
        airline_code: IATA airline code (e.g., "BA")
        max_results: Maximum number of destinations to return
    
    Returns:
        API response with destination airports
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    response = requests.get(
        f"{base_url}/v1/airline/destinations",
        headers={"Authorization": f"Bearer {token}"},
        params={"airlineCode": airline_code.upper(), "max": max_results}
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def format_human(data: dict, airline: str) -> str:
    """Format results in human-readable form."""
    if "error" in data:
        return f"❌ Error: {json.dumps(data['error'], indent=2)}"
    
    destinations = data.get("data", [])
    if not destinations:
        return f"No routes found for airline {airline}."
    
    lines = [f"✈️  {airline} flies to {len(destinations)} destinations:\n"]
    
    for dest in destinations:
        iata = dest.get("iataCode", "???")
        name = dest.get("name", "")
        
        if name:
            lines.append(f"   {iata} - {name}")
        else:
            lines.append(f"   {iata}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find destinations for an airline")
    parser.add_argument("--airline", "-a", required=True, help="Airline IATA code")
    parser.add_argument("--max", type=int, default=100, help="Maximum results (default: 100)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    result = get_airline_routes(args.airline, args.max)
    
    if args.format == "human":
        print(format_human(result, args.airline.upper()))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
