---
name: amadeus-flights
description: Search flights, get prices, and check availability via Amadeus API. Find flights by route, dates, and preferences. Compare prices across airlines. Use when user asks to "find flights", "search flights to [city]", "flight prices", "cheap flights", "flights from X to Y".
homepage: https://github.com/lyra-claw/travelclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "✈️",
        "requires":
          {
            "bins": ["python3"],
            "env": ["AMADEUS_API_KEY", "AMADEUS_API_SECRET"],
          },
        "primaryEnv": "AMADEUS_API_KEY",
        "install":
          [
            {
              "id": "pip-requests",
              "kind": "pip",
              "packages": ["requests"],
              "label": "Install requests (pip)",
            },
          ],
      },
  }
---

# Amadeus Flights Skill ✈️

Search flight prices and availability via the Amadeus Self-Service API.

## Setup

1. **Get API credentials** at https://developers.amadeus.com/self-service
   - Create account → My Apps → Create new app
   - Copy API Key and API Secret

2. **Set environment variables:**
```bash
export AMADEUS_API_KEY="your-api-key"
export AMADEUS_API_SECRET="your-api-secret"
export AMADEUS_ENV="test"  # or "production" for live data
```

3. **Install dependency:**
```bash
pip install requests
```

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Search flights | `scripts/search.py` | `--from LHR --to BCN --date 2026-03-15` |
| Round trip | `scripts/search.py` | `--from LHR --to BCN --date 2026-03-15 --return 2026-03-20` |
| Price offer | `scripts/price.py` | `--offer <offer-json>` |
| Airport lookup | `scripts/airports.py` | `--query "Barcelona"` |
| Airport routes | `scripts/routes.py` | `--airport LHR` |
| Airline routes | `scripts/airline_routes.py` | `--airline BA` |
| Airline lookup | `scripts/airlines.py` | `--code BA,IB` |
| Check-in links | `scripts/checkin.py` | `--airline BA` |
| Find destinations | `scripts/inspiration.py` | `--origin LHR` |
| Cheapest dates | `scripts/cheapest_dates.py` | `--origin LHR --destination BCN` |
| Compare dates | `scripts/compare_dates.py` | `--from LHR --to BCN --dates 2026-03-15,2026-03-16` |

## Capabilities

### 1. Flight Search (One-way)

```bash
python3 <skill>/scripts/search.py \
  --from LHR \
  --to BCN \
  --date 2026-03-15 \
  --adults 1
```

### 2. Flight Search (Round Trip)

```bash
python3 <skill>/scripts/search.py \
  --from LHR \
  --to BCN \
  --date 2026-03-15 \
  --return 2026-03-20 \
  --adults 2
```

### 3. With Preferences

```bash
python3 <skill>/scripts/search.py \
  --from LHR \
  --to JFK \
  --date 2026-03-15 \
  --class BUSINESS \
  --nonstop \
  --max 10
```

**Travel classes:** ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST

### 4. Airport/City Lookup

Find IATA codes:

```bash
python3 <skill>/scripts/airports.py --query "Barcelona"
python3 <skill>/scripts/airports.py --query "London"
```

### 5. Confirm Price

Before booking, confirm an offer is still valid:

```bash
python3 <skill>/scripts/price.py --offer '<offer-json-from-search>'
```

### 6. Airport Routes (Where can I fly from X?)

```bash
python3 <skill>/scripts/routes.py --airport LHR --max 50 --format human
```

Shows all direct destinations from an airport.

### 7. Airline Routes (Where does X fly?)

```bash
python3 <skill>/scripts/airline_routes.py --airline BA --max 50 --format human
```

Shows all destinations served by an airline.

### 8. Airline Code Lookup

```bash
python3 <skill>/scripts/airlines.py --code "BA,IB,VY" --format human
```

Look up airline names by IATA codes.

### 9. Check-in Links

```bash
python3 <skill>/scripts/checkin.py --airline BA --format human
```

Get direct check-in URLs for airlines.

### 10. Flight Inspiration (Where's cheap from X?)

```bash
python3 <skill>/scripts/inspiration.py --origin LHR --format human
python3 <skill>/scripts/inspiration.py --origin LHR --max-price 100 --nonstop
```

Find cheapest destinations from an origin. Options:
- `--date` - Departure date or range
- `--one-way` / `--round-trip` - Filter by trip type
- `--duration` - Trip length in days
- `--nonstop` - Direct flights only
- `--max-price` - Price cap
- `--view-by` - Group by: date, destination, duration, week, country

⚠️ Uses cached data; may have limited results in test environment.

### 11. Cheapest Dates (When's cheap to Y?)

```bash
python3 <skill>/scripts/cheapest_dates.py --origin LHR --destination BCN --format human
python3 <skill>/scripts/cheapest_dates.py --origin LHR --destination BCN --date 2026-03-01,2026-03-31
```

Find the cheapest dates to fly a specific route.

⚠️ Uses cached data; may have limited results in test environment.

### 12. Compare Dates (Which date is cheapest?)

```bash
# Compare specific dates
python3 <skill>/scripts/compare_dates.py \
  --from LHR --to BCN \
  --dates 2026-03-15,2026-03-16,2026-03-17 \
  --format human

# Compare date range
python3 <skill>/scripts/compare_dates.py \
  --from LHR --to BCN \
  --start 2026-03-15 --end 2026-03-22 \
  --format human

# Compare weekends only
python3 <skill>/scripts/compare_dates.py \
  --from LHR --to BCN \
  --start 2026-03-01 --end 2026-03-31 \
  --weekends-only \
  --format human

# Round trip comparison (7-day trips)
python3 <skill>/scripts/compare_dates.py \
  --from LHR --to BCN \
  --dates 2026-03-15,2026-03-16,2026-03-17 \
  --return-after 7 \
  --format human
```

Compare flight prices across multiple specific dates or a date range. Perfect for finding the best departure date when you have flexibility. Unlike `cheapest_dates.py` (which uses cached API data), this script performs real searches for each date to give accurate current prices.

Options:
- `--dates` - Comma-separated list of specific dates
- `--start` / `--end` - Search all dates in range
- `--weekends-only` - Only Saturdays and Sundays
- `--weekdays-only` - Only Monday-Friday
- `--return-after` - Days until return (makes it round trip)
- All standard filters: `--nonstop`, `--class`, `--max-price`, etc.

✅ Uses live flight search API — more accurate than cached date APIs.

## Common Airport Codes

| Code | Airport |
|------|---------|
| LHR | London Heathrow |
| LGW | London Gatwick |
| STN | London Stansted |
| BRS | Bristol |
| BCN | Barcelona |
| CDG | Paris Charles de Gaulle |
| JFK | New York JFK |
| LAX | Los Angeles |
| SFO | San Francisco |
| DXB | Dubai |

## Output Format

Default is JSON. Add `--format human` for readable output:

```
✈️  British Airways BA456
    LHR 08:30 → BCN 11:45 (2h 15m) · Direct
    💰 £89 · Economy
    
✈️  Vueling VY8794
    LGW 14:20 → BCN 17:30 (2h 10m) · Direct
    💰 £52 · Economy
```

## ⚠️ Important Notes

- **Test environment:** Uses cached/sample data — good for development
- **Production:** Real-time prices, requires "Move to Production" in Amadeus dashboard
- **Prices are indicative:** API returns net rates, not retail prices
- **No booking:** This skill searches only; booking requires payment integration

## Limitations

- Rate limits: 10 TPS (test), 40 TPS (production)
- Max 250 offers per search
- Dates must be in future
- Some routes may have limited test data

## Scripts Summary

| Script | Status | Notes |
|--------|--------|-------|
| `search.py` | ✅ Working | Core flight search |
| `price.py` | ✅ Working | Confirm offer pricing |
| `airports.py` | ✅ Working | Airport/city lookup |
| `airlines.py` | ✅ Working | Airline code lookup |
| `routes.py` | ✅ Working | Airport direct destinations |
| `airline_routes.py` | ✅ Working | Airline destinations |
| `checkin.py` | ✅ Working | Check-in links |
| `inspiration.py` | ⚠️ Ready | Cached data API - limited in test |
| `cheapest_dates.py` | ⚠️ Ready | Cached data API - limited in test |
| `compare_dates.py` | ✅ Working | Live date comparison - accurate prices |
| `auth.py` | ✅ Internal | OAuth token management |
