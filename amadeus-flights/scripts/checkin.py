#!/usr/bin/env python3
"""
Flight Check-in Links - Get direct check-in URLs for airlines.

Uses Amadeus Flight Check-in Links API to simplify the check-in process
by providing direct links to airline check-in pages.

Usage:
    python3 checkin.py --airline BA
    python3 checkin.py --airline IB --language es
"""

import argparse
import json
import os
import sys

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def get_checkin_links(airline_code: str, language: str = "en") -> dict:
    """
    Get check-in links for an airline.
    
    Args:
        airline_code: IATA airline code (e.g., "BA")
        language: Language code for the check-in page (default: "en")
    
    Returns:
        API response with check-in URLs
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    params = {
        "airlineCode": airline_code.upper(),
        "language": language
    }
    
    response = requests.get(
        f"{base_url}/v2/reference-data/urls/checkin-links",
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
    
    links = data.get("data", [])
    if not links:
        return "No check-in links found for that airline."
    
    lines = []
    for link in links:
        airline = link.get("id", "").split("-")[0]
        channel = link.get("channel", "")
        href = link.get("href", "")
        
        channel_emoji = "🖥️" if channel == "Web" else "📱" if channel == "Mobile" else "🔗"
        lines.append(f"{channel_emoji} [{airline}] {channel}: {href}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get airline check-in links")
    parser.add_argument("--airline", "-a", required=True, help="Airline IATA code")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    result = get_checkin_links(args.airline, args.language)
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
