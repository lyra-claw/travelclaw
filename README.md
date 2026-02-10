# TravelClaw

OpenClaw meets travel data — an exploration of AI-assisted travel planning and booking.

## Vision

What if your AI assistant could help you plan, book, and manage travel as naturally as asking a friend?

## Research So Far

### Travel APIs

| API | Access | Best For |
|-----|--------|----------|
| **Amadeus** | Self-service, free sandbox | Developers, startups — no approval needed |
| **Skyscanner** | Partner application (>100k monthly traffic required) | Established businesses with traffic |

**Recommendation:** Start with Amadeus for prototyping — free test environment, pay-per-use in production.

### Amadeus Capabilities
- ✅ Flight search & price comparison (search.py, compare_dates.py)
- ✅ Airport/airline lookup (airports.py, airlines.py, routes.py)
- ✅ Travel inspiration & cheapest dates (inspiration.py, cheapest_dates.py)
- ✅ Check-in links & delay predictions (checkin.py, delay_prediction.py)
- ✅ Hotel search & booking (via amadeus-hotels skill)
- ✅ Airport transfers (via amadeus-transfers skill)
- ✅ Tours & activities (via amadeus-experiences skill)
- 🔄 Flight booking (in progress)
- 🔄 Trip parser & itinerary management (planned)

## Ideas to Explore

- [x] Natural language flight search ("Find me flights to Barcelona next weekend under £200")
- [x] Date comparison tool (compare prices across flexible dates)
- [ ] Price tracking & alerts (monitor specific routes for drops)
- [ ] Trip planning assistant (end-to-end journey planner)
- [ ] Multi-city itinerary builder
- [ ] Integration with calendar (block travel days automatically)
- [ ] Packing list generator based on destination & weather

## Next Steps

1. Sign up for Amadeus developer account
2. Build a simple flight search skill
3. Test with real queries
4. Expand from there

## Links

- [Amadeus for Developers](https://developers.amadeus.com/)
- [Amadeus Self-Service APIs](https://developers.amadeus.com/self-service)

---

*Project started: February 2026*
