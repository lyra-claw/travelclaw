#!/usr/bin/env python3
"""
Flight Cheapest Date Search - Find cheapest dates to fly a specific route.

Uses Amadeus Flight Cheapest Date Search API to find the best dates
for a given origin-destination pair, ordered by price.

Usage:
    python3 cheapest_dates.py --origin LHR --destination BCN
    python3 cheapest_dates.py --origin LHR --destination BCN --date 2026-03-01,2026-03-31
    python3 cheapest_dates.py --origin LHR --destination BCN --nonstop --max-price 100
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def search_cheapest_dates(
    origin: str,
    destination: str,
    departure_date: str = None,
    one_way: bool = None,
    duration: int = None,
    non_stop: bool = False,
    max_price: float = None,
    view_by: str = None,
    currency: str = "GBP"
) -> dict:
    """
    Search for cheapest dates to fly a specific route.
    
    Args:
        origin: IATA airport code for origin
        destination: IATA airport code for destination
        departure_date: Date or date range (YYYY-MM-DD or YYYY-MM-DD,YYYY-MM-DD)
        one_way: True for one-way only, False for round-trip only, None for both
        duration: Trip duration in days (for filtering)
        non_stop: Only direct flights
        max_price: Maximum ticket price
        view_by: Group results by DATE, DESTINATION, DURATION, WEEK
        currency: Currency code for prices (default: GBP)
    
    Returns:
        API response with date options and prices
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    params = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "currency": currency
    }
    
    if departure_date:
        params["departureDate"] = departure_date
    if one_way is not None:
        params["oneWay"] = str(one_way).lower()
    if duration:
        params["duration"] = duration
    if non_stop:
        params["nonStop"] = "true"
    if max_price:
        params["maxPrice"] = max_price
    if view_by:
        params["viewBy"] = view_by.upper()
    
    response = requests.get(
        f"{base_url}/v1/shopping/flight-dates",
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
    
    dates = data.get("data", [])
    if not dates:
        return "No flight dates found. Try adjusting your search criteria."
    
    # Get origin/destination from first result
    first = dates[0] if dates else {}
    origin = first.get("origin", "???")
    destination = first.get("destination", "???")
    
    lines = [f"📅 Cheapest dates for {origin} → {destination}:\n"]
    
    for flight in dates:
        price = flight.get("price", {}).get("total", "N/A")
        dep_date = flight.get("departureDate", "")
        ret_date = flight.get("returnDate", "")
        
        # Format dates nicely
        try:
            dep = datetime.strptime(dep_date, "%Y-%m-%d")
            date_str = dep.strftime("%a %b %d")
            if ret_date:
                ret = datetime.strptime(ret_date, "%Y-%m-%d")
                days = (ret - dep).days
                date_str += f" → {ret.strftime('%a %b %d')} ({days}d)"
        except:
            date_str = f"{dep_date}"
            if ret_date:
                date_str += f" → {ret_date}"
        
        lines.append(f"💰 £{price:<8} {date_str}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find cheapest dates to fly a route")
    parser.add_argument("--origin", "-o", required=True, help="Origin airport IATA code")
    parser.add_argument("--destination", "-d", required=True, help="Destination airport IATA code")
    parser.add_argument("--date", help="Departure date/range (YYYY-MM-DD or YYYY-MM-DD,YYYY-MM-DD)")
    parser.add_argument("--one-way", action="store_true", help="One-way flights only")
    parser.add_argument("--round-trip", action="store_true", help="Round-trip flights only")
    parser.add_argument("--duration", type=int, help="Trip duration in days")
    parser.add_argument("--nonstop", action="store_true", help="Direct flights only")
    parser.add_argument("--max-price", type=float, help="Maximum ticket price")
    parser.add_argument("--view-by", choices=["date", "duration", "week"],
                        help="Group results by category")
    parser.add_argument("--currency", default="GBP", help="Currency code (default: GBP)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Determine one_way setting
    one_way = None
    if args.one_way:
        one_way = True
    elif args.round_trip:
        one_way = False
    
    result = search_cheapest_dates(
        origin=args.origin,
        destination=args.destination,
        departure_date=args.date,
        one_way=one_way,
        duration=args.duration,
        non_stop=args.nonstop,
        max_price=args.max_price,
        view_by=args.view_by,
        currency=args.currency
    )
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
