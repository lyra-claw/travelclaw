#!/usr/bin/env python3
"""
Search flights via Amadeus Flight Offers Search API.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Optional

import requests

from auth import get_auth_header, get_base_url


def make_request(url: str, params: dict = None, json_body: dict = None, method: str = "GET", retries: int = 3) -> dict:
    """Make API request with retry logic for rate limits."""
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"
    
    for attempt in range(retries):
        if method == "POST":
            response = requests.post(url, headers=headers, json=json_body, timeout=60)
        else:
            response = requests.get(url, headers=headers, params=params, timeout=60)
        
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        
        if response.status_code == 401:
            raise EnvironmentError(
                "Authentication failed. Check AMADEUS_API_KEY and AMADEUS_API_SECRET."
            )
        
        if response.status_code == 400:
            error = response.json().get("errors", [{}])[0]
            raise ValueError(f"Bad request: {error.get('detail', response.text)}")
        
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded due to rate limiting")


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    travel_class: Optional[str] = None,
    nonstop: bool = False,
    max_results: int = 20,
    max_price: Optional[int] = None,
    currency: str = "GBP",
) -> dict:
    """Search for flight offers."""
    base_url = get_base_url()
    
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "adults": adults,
        "currencyCode": currency,
        "max": min(max_results, 250),
    }
    
    if return_date:
        params["returnDate"] = return_date
    
    if children > 0:
        params["children"] = children
    
    if infants > 0:
        params["infants"] = infants
    
    if travel_class:
        params["travelClass"] = travel_class.upper()
    
    if nonstop:
        params["nonStop"] = "true"
    
    if max_price:
        params["maxPrice"] = max_price
    
    data = make_request(
        f"{base_url}/v2/shopping/flight-offers",
        params=params,
    )
    
    return data


def format_duration(iso_duration: str) -> str:
    """Convert ISO 8601 duration to readable format."""
    # PT2H30M -> 2h 30m
    duration = iso_duration.replace("PT", "")
    result = ""
    
    if "H" in duration:
        hours, duration = duration.split("H")
        result += f"{hours}h "
    
    if "M" in duration:
        minutes = duration.replace("M", "")
        result += f"{minutes}m"
    
    return result.strip()


def format_time(iso_time: str) -> str:
    """Extract time from ISO datetime."""
    # 2026-03-15T08:30:00 -> 08:30
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return iso_time


def format_human(data: dict) -> str:
    """Format flight offers for human reading."""
    offers = data.get("data", [])
    dictionaries = data.get("dictionaries", {})
    carriers = dictionaries.get("carriers", {})
    
    if not offers:
        return "No flights found."
    
    lines = []
    
    for i, offer in enumerate(offers[:15], 1):
        price = offer.get("price", {})
        total = price.get("grandTotal", price.get("total", "?"))
        currency = price.get("currency", "GBP")
        
        # Currency symbols
        symbols = {"GBP": "£", "EUR": "€", "USD": "$"}
        symbol = symbols.get(currency, currency + " ")
        
        itineraries = offer.get("itineraries", [])
        
        for j, itinerary in enumerate(itineraries):
            direction = "→" if j == 0 else "←"
            segments = itinerary.get("segments", [])
            
            if not segments:
                continue
            
            first_seg = segments[0]
            last_seg = segments[-1]
            
            # Carrier
            carrier_code = first_seg.get("carrierCode", "")
            carrier_name = carriers.get(carrier_code, carrier_code)
            flight_number = first_seg.get("number", "")
            
            # Times
            dep_time = format_time(first_seg.get("departure", {}).get("at", ""))
            arr_time = format_time(last_seg.get("arrival", {}).get("at", ""))
            
            # Airports
            dep_airport = first_seg.get("departure", {}).get("iataCode", "")
            arr_airport = last_seg.get("arrival", {}).get("iataCode", "")
            
            # Duration
            duration = format_duration(itinerary.get("duration", ""))
            
            # Stops
            stops = len(segments) - 1
            stop_str = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
            
            # Cabin class
            cabin = ""
            traveler_pricings = offer.get("travelerPricings", [])
            if traveler_pricings:
                fare_details = traveler_pricings[0].get("fareDetailsBySegment", [])
                if fare_details:
                    cabin = fare_details[0].get("cabin", "").title()
            
            if j == 0:
                lines.append(f"✈️  {carrier_name} {carrier_code}{flight_number}")
                lines.append(f"    {dep_airport} {dep_time} {direction} {arr_airport} {arr_time} ({duration}) · {stop_str}")
                lines.append(f"    💰 {symbol}{total}" + (f" · {cabin}" if cabin else ""))
            else:
                lines.append(f"    Return: {dep_airport} {dep_time} {direction} {arr_airport} {arr_time} ({duration}) · {stop_str}")
        
        lines.append("")
    
    if len(offers) > 15:
        lines.append(f"... and {len(offers) - 15} more options")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search flights via Amadeus API")
    
    # Required
    parser.add_argument("--from", dest="origin", required=True, 
                        help="Origin airport code (e.g., LHR)")
    parser.add_argument("--to", dest="destination", required=True,
                        help="Destination airport code (e.g., BCN)")
    parser.add_argument("--date", required=True,
                        help="Departure date (YYYY-MM-DD)")
    
    # Optional
    parser.add_argument("--return", dest="return_date",
                        help="Return date for round trip (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=1,
                        help="Number of adults (default: 1)")
    parser.add_argument("--children", type=int, default=0,
                        help="Number of children (2-11)")
    parser.add_argument("--infants", type=int, default=0,
                        help="Number of infants (<2)")
    parser.add_argument("--class", dest="travel_class",
                        choices=["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
                        help="Travel class")
    parser.add_argument("--nonstop", action="store_true",
                        help="Direct flights only")
    parser.add_argument("--max", type=int, default=20,
                        help="Max results (default: 20)")
    parser.add_argument("--max-price", type=int,
                        help="Maximum price")
    parser.add_argument("--currency", default="GBP",
                        help="Currency code (default: GBP)")
    
    # Output
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    try:
        data = search_flights(
            origin=args.origin,
            destination=args.destination,
            departure_date=args.date,
            return_date=args.return_date,
            adults=args.adults,
            children=args.children,
            infants=args.infants,
            travel_class=args.travel_class,
            nonstop=args.nonstop,
            max_results=args.max,
            max_price=args.max_price,
            currency=args.currency,
        )
        
        if args.format == "human":
            print(format_human(data))
        else:
            print(json.dumps(data, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
