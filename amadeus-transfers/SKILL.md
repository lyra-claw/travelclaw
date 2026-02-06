---
name: amadeus-transfers
description: Search and book airport transfers, taxis, and private cars via Amadeus API. Find transportation from airports to hotels or addresses. Use when user asks for "airport transfer", "taxi from airport", "car service", "private transfer".
homepage: https://github.com/lyra-claw/travelclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "🚗",
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

# Amadeus Transfers Skill 🚗

Search and book airport transfers via the Amadeus Self-Service API.

## Setup

Same credentials as amadeus-flights:

```bash
export AMADEUS_API_KEY="your-api-key"
export AMADEUS_API_SECRET="your-api-secret"
export AMADEUS_ENV="test"  # or "production"
```

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Search transfers | `scripts/search.py` | `--from-airport CDG --to-address "..." --date 2026-03-15 --time 10:30` |

## Transfer Types

| Type | Description |
|------|-------------|
| PRIVATE | Private car, point to point |
| SHARED | Shared shuttle |
| TAXI | Taxi (price estimated) |
| HOURLY | Chauffeur by the hour |
| AIRPORT_EXPRESS | Express train |
| AIRPORT_BUS | Express bus |

## Capabilities

### 1. Airport to Address

```bash
python3 <skill>/scripts/search.py \
  --from-airport CDG \
  --to-address "Avenue Anatole France, 5" \
  --to-city Paris \
  --to-country FR \
  --date 2026-03-15 \
  --time 10:30 \
  --passengers 2 \
  --format human
```

### 2. Airport to Airport

```bash
python3 <skill>/scripts/search.py \
  --from-airport LHR \
  --to-airport LGW \
  --date 2026-03-15 \
  --time 14:00 \
  --passengers 1 \
  --format human
```

### 3. With Transfer Type

```bash
python3 <skill>/scripts/search.py \
  --from-airport BCN \
  --to-address "La Rambla, 100" \
  --to-city Barcelona \
  --to-country ES \
  --date 2026-03-15 \
  --time 09:00 \
  --type PRIVATE \
  --format human
```

### 4. Using Coordinates

```bash
python3 <skill>/scripts/search.py \
  --from-airport CDG \
  --to-geo "48.8584,2.2945" \
  --date 2026-03-15 \
  --time 12:00 \
  --format human
```

## Output Example

```
🚗 Found 3 transfer options:

🚘 PRIVATE - Mercedes-Benz E-Class or similar
   💰 EUR 85.00
   👥 3 seats · ABC Transfers
   📍 45 KM
   🕐 2026-03-15 10:30
   ID: 0cb11574...

🚕 TAXI - Standard Taxi
   💰 EUR 55.00~
   👥 4 seats · City Cabs
   📍 45 KM
   ID: 1ab22345...
```

## Location Options

You can specify locations using:

- **Airport code:** `--from-airport CDG`
- **Address:** `--to-address "123 Main St" --to-city Paris --to-country FR`
- **Coordinates:** `--to-geo "48.8584,2.2945"`

## ⚠️ Notes

- Test environment has limited provider coverage
- Prices may be estimates (marked with ~)
- Booking requires additional API (not yet implemented)

## Scripts

| Script | Status | Notes |
|--------|--------|-------|
| `search.py` | ✅ Ready | Transfer search |
| `auth.py` | ✅ Internal | OAuth management |
