#!/usr/bin/env python3
"""
Airline Code Lookup - Find airline names by IATA/ICAO codes.

Uses Amadeus Airline Code Lookup API to get airline information.

Usage:
    python3 airlines.py --code BA
    python3 airlines.py --code "BA,IB,VY"
"""

import argparse
import json
import os
import sys

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def lookup_airlines(codes: str) -> dict:
    """
    Look up airline information by IATA or ICAO codes.
    
    Args:
        codes: Comma-separated airline codes (e.g., "BA,IB,VY")
    
    Returns:
        API response with airline details
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    params = {"airlineCodes": codes.upper()}
    
    response = requests.get(
        f"{base_url}/v1/reference-data/airlines",
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
    
    airlines = data.get("data", [])
    if not airlines:
        return "No airlines found for those codes."
    
    lines = []
    for airline in airlines:
        iata = airline.get("iataCode", "")
        icao = airline.get("icaoCode", "")
        name = airline.get("businessName") or airline.get("commonName", "Unknown")
        
        codes_str = iata
        if icao:
            codes_str += f"/{icao}"
        
        lines.append(f"✈️  [{codes_str}] {name}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Look up airline information by code")
    parser.add_argument("--code", "-c", required=True, 
                        help="Airline code(s), comma-separated (e.g., 'BA,IB,VY')")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    result = lookup_airlines(args.code)
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
