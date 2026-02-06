#!/usr/bin/env python3
"""
Transfer Search - Find airport transfers, taxis, and private cars.

Uses Amadeus Transfer Search API to find transportation options
from airports to destinations.

Usage:
    # Airport to address
    python3 search.py --from-airport CDG --to-address "Avenue Anatole France, 5" --to-city Paris --date 2026-03-15 --time 10:30 --passengers 2

    # Airport to airport
    python3 search.py --from-airport LHR --to-airport LGW --date 2026-03-15 --time 14:00 --passengers 1

    # With transfer type
    python3 search.py --from-airport BCN --to-address "La Rambla, 100" --to-city Barcelona --date 2026-03-15 --time 09:00 --type PRIVATE
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token, get_base_url

TRANSFER_TYPES = [
    "PRIVATE",      # Private transfer point to point
    "SHARED",       # Shared transfer point to point
    "TAXI",         # Taxi reservation (price estimated)
    "HOURLY",       # Chauffeured driven per hour
    "AIRPORT_EXPRESS",  # Express train from/to airport
    "AIRPORT_BUS",  # Express bus from/to airport
]


def search_transfers(
    start_location_code: str = None,
    start_address: str = None,
    start_city: str = None,
    start_country: str = None,
    start_geo: str = None,
    end_location_code: str = None,
    end_address: str = None,
    end_city: str = None,
    end_country: str = None,
    end_geo: str = None,
    transfer_type: str = None,
    start_datetime: str = None,
    passengers: int = 1,
    currency: str = "GBP"
) -> dict:
    """
    Search for transfer offers.
    
    Args:
        start_location_code: IATA airport code for pickup
        start_address: Street address for pickup
        start_city: City name for pickup
        start_country: Country code for pickup (e.g., "FR")
        start_geo: Lat,lng for pickup (e.g., "48.8566,2.3522")
        end_location_code: IATA airport code for dropoff
        end_address: Street address for dropoff
        end_city: City name for dropoff
        end_country: Country code for dropoff
        end_geo: Lat,lng for dropoff
        transfer_type: Type of transfer (PRIVATE, SHARED, TAXI, etc.)
        start_datetime: ISO datetime (YYYY-MM-DDTHH:MM:SS)
        passengers: Number of passengers
        currency: Currency code
    
    Returns:
        API response with transfer offers
    """
    import requests
    
    token = get_token()
    base_url = get_base_url()
    
    # Build request body
    body = {
        "passengers": passengers
    }
    
    # Start location
    if start_location_code:
        body["startLocationCode"] = start_location_code.upper()
    if start_address:
        body["startAddressLine"] = start_address
    if start_city:
        body["startCityName"] = start_city
    if start_country:
        body["startCountryCode"] = start_country.upper()
    if start_geo:
        lat, lng = start_geo.split(",")
        body["startGeoCode"] = start_geo
    
    # End location
    if end_location_code:
        body["endLocationCode"] = end_location_code.upper()
    if end_address:
        body["endAddressLine"] = end_address
    if end_city:
        body["endCityName"] = end_city
    if end_country:
        body["endCountryCode"] = end_country.upper()
    if end_geo:
        body["endGeoCode"] = end_geo
    
    # Other params
    if transfer_type:
        body["transferType"] = transfer_type.upper()
    if start_datetime:
        body["startDateTime"] = start_datetime
    
    response = requests.post(
        f"{base_url}/v1/shopping/transfer-offers",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=body
    )
    
    if response.status_code != 200:
        return {"error": response.json(), "status": response.status_code}
    
    return response.json()


def format_human(data: dict) -> str:
    """Format results in human-readable form."""
    if "error" in data:
        return f"❌ Error: {json.dumps(data['error'], indent=2)}"
    
    offers = data.get("data", [])
    if not offers:
        return "No transfer offers found."
    
    lines = [f"🚗 Found {len(offers)} transfer options:\n"]
    
    for offer in offers:
        transfer_type = offer.get("transferType", "UNKNOWN")
        offer_id = offer.get("id", "")[:12]
        
        # Vehicle info
        vehicle = offer.get("vehicle", {})
        vehicle_desc = vehicle.get("description", "Vehicle")
        seats = vehicle.get("seats", [{}])[0].get("count", "?")
        
        # Price
        quotation = offer.get("quotation", {})
        price = quotation.get("monetaryAmount", "N/A")
        currency = quotation.get("currencyCode", "")
        is_estimated = quotation.get("isEstimated", False)
        
        # Provider
        provider = offer.get("serviceProvider", {})
        provider_name = provider.get("name", "Unknown provider")
        
        # Start/end
        start = offer.get("start", {})
        end = offer.get("end", {})
        start_time = start.get("dateTime", "")[:16].replace("T", " ") if start.get("dateTime") else ""
        
        # Distance
        distance = offer.get("distance", {})
        dist_val = distance.get("value", "")
        dist_unit = distance.get("unit", "")
        
        type_emoji = {
            "PRIVATE": "🚘",
            "SHARED": "🚐",
            "TAXI": "🚕",
            "HOURLY": "⏰",
            "AIRPORT_EXPRESS": "🚄",
            "AIRPORT_BUS": "🚌",
        }.get(transfer_type, "🚗")
        
        lines.append(f"{type_emoji} {transfer_type} - {vehicle_desc}")
        lines.append(f"   💰 {currency} {price}{'~' if is_estimated else ''}")
        lines.append(f"   👥 {seats} seats · {provider_name}")
        if dist_val:
            lines.append(f"   📍 {dist_val} {dist_unit}")
        if start_time:
            lines.append(f"   🕐 {start_time}")
        lines.append(f"   ID: {offer_id}...")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search for airport transfers")
    
    # Start location
    parser.add_argument("--from-airport", help="Pickup airport IATA code")
    parser.add_argument("--from-address", help="Pickup street address")
    parser.add_argument("--from-city", help="Pickup city name")
    parser.add_argument("--from-country", help="Pickup country code (e.g., FR)")
    parser.add_argument("--from-geo", help="Pickup coordinates (lat,lng)")
    
    # End location
    parser.add_argument("--to-airport", help="Dropoff airport IATA code")
    parser.add_argument("--to-address", help="Dropoff street address")
    parser.add_argument("--to-city", help="Dropoff city name")
    parser.add_argument("--to-country", help="Dropoff country code")
    parser.add_argument("--to-geo", help="Dropoff coordinates (lat,lng)")
    
    # Other options
    parser.add_argument("--date", required=True, help="Pickup date (YYYY-MM-DD)")
    parser.add_argument("--time", required=True, help="Pickup time (HH:MM)")
    parser.add_argument("--passengers", "-p", type=int, default=1, help="Number of passengers")
    parser.add_argument("--type", "-t", choices=TRANSFER_TYPES, help="Transfer type")
    parser.add_argument("--currency", default="GBP", help="Currency code")
    parser.add_argument("--format", choices=["json", "human"], default="json")
    
    args = parser.parse_args()
    
    # Build datetime
    start_datetime = f"{args.date}T{args.time}:00"
    
    result = search_transfers(
        start_location_code=args.from_airport,
        start_address=args.from_address,
        start_city=args.from_city,
        start_country=args.from_country,
        start_geo=args.from_geo,
        end_location_code=args.to_airport,
        end_address=args.to_address,
        end_city=args.to_city,
        end_country=args.to_country,
        end_geo=args.to_geo,
        transfer_type=args.type,
        start_datetime=start_datetime,
        passengers=args.passengers,
        currency=args.currency
    )
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
