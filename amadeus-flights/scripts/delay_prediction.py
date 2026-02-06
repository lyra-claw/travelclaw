#!/usr/bin/env python3
"""
Flight Delay Prediction - Predict flight delay probabilities.

Uses Amadeus Flight Delay Prediction API to estimate the probability
of a flight being delayed based on historical data and ML models.

Usage:
    python3 delay_prediction.py --origin LHR --destination BCN --date 2026-03-15 --time 09:00 --carrier BA --number 456
"""

import argparse
import json
import os
import sys

# Add parent dir for auth module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_token

def predict_delay(
    origin: str,
    destination: str,
    departure_date: str,
    departure_time: str,
    carrier: str,
    flight_number: str,
    aircraft_code: str = None,
    duration: int = None
) -> dict:
    """
    Predict delay probability for a specific flight.
    
    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        departure_time: Local departure time (HH:MM)
        carrier: Airline IATA code
        flight_number: Flight number (without carrier prefix)
        aircraft_code: Aircraft type code (optional)
        duration: Flight duration in minutes (optional)
    
    Returns:
        API response with delay predictions
    """
    import requests
    
    token = get_token()
    env = os.environ.get("AMADEUS_ENV", "test")
    base_url = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
    
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "departureTime": departure_time,
        "carrierCode": carrier.upper(),
        "flightNumber": flight_number
    }
    
    if aircraft_code:
        params["aircraftCode"] = aircraft_code
    if duration:
        params["duration"] = f"PT{duration}M"
    
    response = requests.get(
        f"{base_url}/v1/travel/predictions/flight-delay",
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
    
    predictions = data.get("data", [])
    if not predictions:
        return "No delay prediction available for this flight."
    
    pred = predictions[0]
    flight_id = pred.get("id", "Unknown")
    result = pred.get("result", "UNKNOWN")
    
    lines = [f"🛫 Delay Prediction for {flight_id}\n"]
    
    # Result interpretation
    result_emoji = {
        "LESS_THAN_30_MINUTES": "✅",
        "BETWEEN_30_AND_60_MINUTES": "⚠️",
        "BETWEEN_60_AND_120_MINUTES": "🟠",
        "OVER_120_MINUTES_OR_CANCELLED": "🔴"
    }.get(result, "❓")
    
    result_text = {
        "LESS_THAN_30_MINUTES": "Likely on time (< 30 min delay)",
        "BETWEEN_30_AND_60_MINUTES": "Possible delay (30-60 min)",
        "BETWEEN_60_AND_120_MINUTES": "Significant delay risk (60-120 min)",
        "OVER_120_MINUTES_OR_CANCELLED": "High delay/cancellation risk (> 120 min)"
    }.get(result, result)
    
    lines.append(f"{result_emoji} Prediction: {result_text}\n")
    
    # Show probability breakdown
    probabilities = pred.get("probability", [])
    if probabilities:
        lines.append("📊 Probability breakdown:")
        for prob in probabilities:
            delay_type = prob.get("result", "")
            value = float(prob.get("probability", 0)) * 100
            
            delay_label = {
                "LESS_THAN_30_MINUTES": "On time (< 30 min)",
                "BETWEEN_30_AND_60_MINUTES": "30-60 min delay",
                "BETWEEN_60_AND_120_MINUTES": "60-120 min delay",
                "OVER_120_MINUTES_OR_CANCELLED": "> 120 min / cancelled"
            }.get(delay_type, delay_type)
            
            bar = "█" * int(value / 5)
            lines.append(f"   {value:5.1f}% {bar} {delay_label}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Predict flight delay probability")
    parser.add_argument("--origin", "-o", required=True, help="Origin airport IATA code")
    parser.add_argument("--destination", "-d", required=True, help="Destination airport IATA code")
    parser.add_argument("--date", required=True, help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--time", required=True, help="Departure time (HH:MM)")
    parser.add_argument("--carrier", "-c", required=True, help="Airline IATA code")
    parser.add_argument("--number", "-n", required=True, help="Flight number")
    parser.add_argument("--aircraft", help="Aircraft type code (optional)")
    parser.add_argument("--duration", type=int, help="Flight duration in minutes (optional)")
    parser.add_argument("--format", choices=["json", "human"], default="json",
                        help="Output format (default: json)")
    
    args = parser.parse_args()
    
    result = predict_delay(
        origin=args.origin,
        destination=args.destination,
        departure_date=args.date,
        departure_time=args.time,
        carrier=args.carrier,
        flight_number=args.number,
        aircraft_code=args.aircraft,
        duration=args.duration
    )
    
    if args.format == "human":
        print(format_human(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
