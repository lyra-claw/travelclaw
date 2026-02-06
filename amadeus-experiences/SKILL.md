---
name: amadeus-experiences
description: Find tours, activities, attractions and points of interest via Amadeus API. Discover things to do at destinations. Use when user asks "things to do in [city]", "tours in [place]", "attractions near me", "activities in [destination]".
homepage: https://github.com/lyra-claw/travelclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "🎯",
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

# Amadeus Experiences Skill 🎯

Find tours, activities, and points of interest via Amadeus API.

## Setup

Same credentials as amadeus-flights:

```bash
export AMADEUS_API_KEY="your-api-key"
export AMADEUS_API_SECRET="your-api-secret"
export AMADEUS_ENV="test"
```

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Tours & Activities | `scripts/activities.py` | `--city Barcelona` |
| Points of Interest | `scripts/poi.py` | `--city Paris --category SIGHTS` |

## Capabilities

### 1. Tours & Activities

Find bookable experiences:

```bash
# By city name
python3 <skill>/scripts/activities.py --city "Barcelona" --format human

# By coordinates
python3 <skill>/scripts/activities.py --lat 41.3851 --lng 2.1734 --radius 10 --format human

# Get activity details
python3 <skill>/scripts/activities.py --id "23642" --format human
```

**Built-in cities:** paris, london, barcelona, rome, amsterdam, berlin, madrid, lisbon, prague, vienna, new york, tokyo, dubai, singapore

### 2. Points of Interest (DEPRECATED)

⚠️ The POI API has been decommissioned by Amadeus. Use `activities.py` instead.

### 3. Search by Area

Search within a geographic square:

```bash
# Activities in a bounding box
python3 <skill>/scripts/activities.py --north 48.9 --south 48.8 --east 2.4 --west 2.3

# POIs in a bounding box
python3 <skill>/scripts/poi.py --north 41.4 --south 41.35 --east 2.2 --west 2.15
```

## Output Example

### Activities
```
🎯 Found 15 activities:

🎫 Skip-the-line Sagrada Familia Tour 📷
   💰 From EUR 45.00
   ⭐ 4.8
   📝 Explore Gaudí's masterpiece with an expert guide...
   ID: 23642

🎫 Barcelona Gothic Quarter Walking Tour
   💰 From EUR 25.00
   ⭐ 4.6
   📝 Discover hidden gems in the medieval quarter...
   ID: 23789
```

## Scripts

| Script | Status | Notes |
|--------|--------|-------|
| `activities.py` | ✅ Ready | Tours & activities search |
| `poi.py` | ❌ Deprecated | API decommissioned |
| `auth.py` | ✅ Internal | OAuth management |

## ⚠️ Notes

- Test environment may have limited activity coverage
- Activities include booking links for purchase
- POI data is reference data (free tier)
