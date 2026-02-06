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
