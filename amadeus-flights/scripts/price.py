#!/usr/bin/env python3
"""
Confirm flight offer pricing via Amadeus API.
Use before booking to verify price is still valid.
"""

import argparse
import json
import sys
import time

import requests

from auth import get_auth_header, get_base_url


def make_request(url: str, json_body: dict, retries: int = 3) -> dict:
    """Make POST request with retry logic."""
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"
    
    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=json_body, timeout=60)
        
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        
        if response.status_code == 401:
            raise EnvironmentError("Authentication failed.")
        
        if response.status_code == 400:
            error = response.json().get("errors", [{}])[0]
            raise ValueError(f"Bad request: {error.get('detail', response.text)}")
        
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded")


def confirm_price(offer: dict) -> dict:
    """Confirm pricing for a flight offer."""
    base_url = get_base_url()
    
    body = {
        "data": {
            "type": "flight-offers-pricing",
            "flightOffers": [offer] if isinstance(offer, dict) else offer,
        }
    }
    
    data = make_request(
        f"{base_url}/v1/shopping/flight-offers/pricing",
        body,
    )
    
    return data


def format_human(data: dict) -> str:
    """Format pricing confirmation for human reading."""
    offers = data.get("data", {}).get("flightOffers", [])
    
    if not offers:
        return "No pricing data returned."
    
    lines = ["✅ Price confirmed!\n"]
    
    for offer in offers:
        price = offer.get("price", {})
        total = price.get("grandTotal", price.get("total", "?"))
        currency = price.get("currency", "GBP")
        base = price.get("base", "?")
        
        symbols = {"GBP": "£", "EUR": "€", "USD": "$"}
        symbol = symbols.get(currency, currency + " ")
        
        lines.append(f"💰 Total: {symbol}{total}")
        lines.append(f"   Base fare: {symbol}{base}")
        
        # Fees breakdown
        fees = price.get("fees", [])
        for fee in fees:
            fee_type = fee.get("type", "Fee")
            fee_amount = fee.get("amount", "0")
            if float(fee_amount) > 0:
                lines.append(f"   {fee_type}: {symbol}{fee_amount}")
        
        lines.append("")
        
        # Validity
        last_ticketing = offer.get("lastTicketingDate")
        if last_ticketing:
            lines.append(f"⏰ Book by: {last_ticketing}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Confirm flight offer pricing")
    parser.add_argument("--offer", required=True,
                        help="Flight offer JSON (from search results)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format")
    
    args = parser.parse_args()
    
    try:
        offer = json.loads(args.offer)
        data = confirm_price(offer)
        
        if args.format == "human":
            print(format_human(data))
        else:
            print(json.dumps(data, indent=2))
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON in --offer", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
