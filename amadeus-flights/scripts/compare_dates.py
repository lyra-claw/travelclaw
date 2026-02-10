#!/usr/bin/env python3
"""
Compare Flight Prices Across Multiple Dates

Searches for flights on multiple departure dates and compares prices
to help find the cheapest option when you have flexibility.

Usage:
    # Compare specific dates
    python3 compare_dates.py --from LHR --to BCN --dates 2026-03-15,2026-03-16,2026-03-17
    
    # Compare date range with trip duration
    python3 compare_dates.py --from LHR --to BCN --start 2026-03-15 --end 2026-03-22 --duration 7
    
    # Round trip comparison
    python3 compare_dates.py --from LHR --to BCN --dates 2026-03-15,2026-03-16 --return-after 7
    
    # Compare weekends in March
    python3 compare_dates.py --from LHR --to BCN --start 2026-03-01 --end 2026-03-31 --weekends-only
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from search import search_flights


def parse_date(date_str: str) -> datetime:
    """Parse YYYY-MM-DD string to datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def format_date(dt: datetime) -> str:
    """Format datetime to YYYY-MM-DD."""
    return dt.strftime("%Y-%m-%d")


def generate_date_range(
    start_date: str,
    end_date: str,
    weekends_only: bool = False,
    weekdays_only: bool = False,
) -> List[str]:
    """Generate list of dates between start and end."""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    dates = []
    current = start
    
    while current <= end:
        # Filter by day of week if needed
        if weekends_only and current.weekday() >= 5:  # Sat=5, Sun=6
            dates.append(format_date(current))
        elif weekdays_only and current.weekday() < 5:  # Mon-Fri
            dates.append(format_date(current))
        elif not weekends_only and not weekdays_only:
            dates.append(format_date(current))
        
        current += timedelta(days=1)
    
    return dates


def compare_dates(
    origin: str,
    destination: str,
    dates: List[str],
    return_after_days: Optional[int] = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    travel_class: Optional[str] = None,
    nonstop: bool = False,
    max_price: Optional[int] = None,
    currency: str = "GBP",
) -> dict:
    """
    Search flights for multiple departure dates and compare prices.
    
    Args:
        origin: Origin airport code
        destination: Destination airport code
        dates: List of departure dates to compare
        return_after_days: Days after departure for return (None for one-way)
        adults: Number of adults
        children: Number of children
        infants: Number of infants
        travel_class: Travel class filter
        nonstop: Only direct flights
        max_price: Maximum price filter
        currency: Currency code
    
    Returns:
        Dict with comparison results
    """
    results = []
    
    print(f"🔍 Comparing prices for {len(dates)} dates...", file=sys.stderr)
    
    for i, departure_date in enumerate(dates, 1):
        print(f"  [{i}/{len(dates)}] Checking {departure_date}...", file=sys.stderr)
        
        # Calculate return date if round trip
        return_date = None
        if return_after_days:
            dep_dt = parse_date(departure_date)
            ret_dt = dep_dt + timedelta(days=return_after_days)
            return_date = format_date(ret_dt)
        
        try:
            data = search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                children=children,
                infants=infants,
                travel_class=travel_class,
                nonstop=nonstop,
                max_results=5,  # Just get top 5 for comparison
                max_price=max_price,
                currency=currency,
            )
            
            offers = data.get("data", [])
            
            if offers:
                # Get cheapest offer
                cheapest = offers[0]
                price = cheapest.get("price", {})
                total = float(price.get("grandTotal", price.get("total", 0)))
                
                # Get flight details
                itineraries = cheapest.get("itineraries", [])
                outbound = itineraries[0] if itineraries else {}
                segments = outbound.get("segments", [])
                
                # Count stops
                stops = len(segments) - 1
                
                # Get carrier info
                dictionaries = data.get("dictionaries", {})
                carriers = dictionaries.get("carriers", {})
                carrier_code = segments[0].get("carrierCode", "") if segments else ""
                carrier_name = carriers.get(carrier_code, carrier_code)
                
                results.append({
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "price": total,
                    "currency": price.get("currency", currency),
                    "stops": stops,
                    "carrier": carrier_name,
                    "carrier_code": carrier_code,
                    "offers_found": len(offers),
                })
            else:
                results.append({
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "price": None,
                    "currency": currency,
                    "offers_found": 0,
                    "error": "No flights found",
                })
        
        except Exception as e:
            results.append({
                "departure_date": departure_date,
                "return_date": return_date,
                "price": None,
                "currency": currency,
                "offers_found": 0,
                "error": str(e),
            })
    
    # Sort by price (None values last)
    results.sort(key=lambda x: (x["price"] is None, x["price"] or float('inf')))
    
    return {
        "origin": origin,
        "destination": destination,
        "comparison": results,
        "cheapest": results[0] if results and results[0]["price"] else None,
    }


def format_human(data: dict) -> str:
    """Format comparison results for human reading."""
    origin = data.get("origin", "???")
    destination = data.get("destination", "???")
    results = data.get("comparison", [])
    
    if not results:
        return "No results to compare."
    
    lines = [f"💰 Price comparison for {origin} → {destination}\n"]
    
    # Currency symbol
    currency = results[0].get("currency", "GBP")
    symbols = {"GBP": "£", "EUR": "€", "USD": "$"}
    symbol = symbols.get(currency, currency + " ")
    
    # Show results
    for result in results:
        date_str = result["departure_date"]
        
        # Format date nicely
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            date_str = dt.strftime("%a %b %d")
            
            if result.get("return_date"):
                ret_dt = datetime.strptime(result["return_date"], "%Y-%m-%d")
                days = (ret_dt - dt).days
                date_str += f" → {ret_dt.strftime('%a %b %d')} ({days}d)"
        except:
            pass
        
        price = result.get("price")
        if price:
            price_str = f"{symbol}{price:,.2f}"
            stops = result.get("stops", 0)
            stop_str = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
            carrier = result.get("carrier", "")
            
            lines.append(f"  {price_str:<12} {date_str:<30} {stop_str:<12} {carrier}")
        else:
            error = result.get("error", "No flights")
            lines.append(f"  {'N/A':<12} {date_str:<30} {error}")
    
    # Highlight cheapest
    cheapest = data.get("cheapest")
    if cheapest and cheapest.get("price"):
        lines.append(f"\n✅ Best deal: {cheapest['departure_date']} at {symbol}{cheapest['price']:,.2f}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare flight prices across multiple dates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare specific dates
  %(prog)s --from LHR --to BCN --dates 2026-03-15,2026-03-16,2026-03-17
  
  # Compare all days in a range
  %(prog)s --from LHR --to BCN --start 2026-03-15 --end 2026-03-22
  
  # Compare weekends only
  %(prog)s --from LHR --to BCN --start 2026-03-01 --end 2026-03-31 --weekends-only
  
  # Round trip comparison (7-day trips)
  %(prog)s --from LHR --to BCN --dates 2026-03-15,2026-03-16 --return-after 7
        """
    )
    
    # Required
    parser.add_argument("--from", dest="origin", required=True,
                        help="Origin airport code (e.g., LHR)")
    parser.add_argument("--to", dest="destination", required=True,
                        help="Destination airport code (e.g., BCN)")
    
    # Date selection (mutually exclusive)
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument("--dates",
                            help="Comma-separated list of dates (YYYY-MM-DD)")
    date_group.add_argument("--start",
                            help="Start date for range (use with --end)")
    
    parser.add_argument("--end",
                        help="End date for range (use with --start)")
    
    # Date filters
    parser.add_argument("--weekends-only", action="store_true",
                        help="Only check Saturdays and Sundays")
    parser.add_argument("--weekdays-only", action="store_true",
                        help="Only check Monday-Friday")
    
    # Trip options
    parser.add_argument("--return-after", type=int, dest="return_after_days",
                        help="Days after departure for return flight (round trip)")
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
    parser.add_argument("--max-price", type=int,
                        help="Maximum price")
    parser.add_argument("--currency", default="GBP",
                        help="Currency code (default: GBP)")
    
    # Output
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Validate date arguments
    if args.start and not args.end:
        parser.error("--start requires --end")
    if args.end and not args.start:
        parser.error("--end requires --start")
    
    # Generate date list
    if args.dates:
        dates = [d.strip() for d in args.dates.split(",")]
    else:
        dates = generate_date_range(
            args.start,
            args.end,
            weekends_only=args.weekends_only,
            weekdays_only=args.weekdays_only,
        )
    
    if not dates:
        print("Error: No dates to compare", file=sys.stderr)
        sys.exit(1)
    
    if len(dates) > 31:
        print(f"Warning: Comparing {len(dates)} dates may take a while...", file=sys.stderr)
    
    try:
        result = compare_dates(
            origin=args.origin,
            destination=args.destination,
            dates=dates,
            return_after_days=args.return_after_days,
            adults=args.adults,
            children=args.children,
            infants=args.infants,
            travel_class=args.travel_class,
            nonstop=args.nonstop,
            max_price=args.max_price,
            currency=args.currency,
        )
        
        if args.format == "human":
            print(format_human(result))
        else:
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
