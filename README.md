# StatScout

**Status:** 🚧 In Development (Not Yet Deployed)

A multi-sport analytics platform designed to aggregate historical performance data and live betting lines to generate hit rates, trust scores, and prop recommendations across NBA and European soccer leagues.

---

## What it will do

StatScout is being built to go beyond basic prop tools that just show a line and hit rate:

- **Adjustable line slider:** drag the O/U line and hit rate recalculates instantly from raw game arrays, no server round-trip
- **Trust score (0-100):** a weighted formula combining hit rate, sample size, line deviation from expected, recent trend, and bookmaker consensus
- **Parlay builder:** add NBA player props and soccer match/player legs to a shared sidebar with combined odds calculated live
- **AI parlay generator:** selects high-trust legs automatically and explains reasoning
- **Soccer win probability:** Poisson distribution model computing home/draw/away probabilities from expected goals

---

## Planned sports coverage

### NBA
Props: Points, Rebounds, Assists, Steals, Blocks, 3PM, PRA, PA, PR, RA

- Hit rates from historical game logs (PostgreSQL)
- Live bookmaker lines via The Odds API
- Quarter breakdown and team performance insights
- Player detail modal with trend chart

### Soccer (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)

**Match Totals:**
- O/U goals line with Over%, BTTS%, expected total, avg goals
- Win probability: Poisson model (home/draw/away) as stacked bar
- Team goal props: per-team scoring line slider
- Trust score: 5-factor weighted formula

**Player Props:**
- Markets: Goals O/U, Shots O/U, Assists O/U, Score or Assist O/U, GK Clean Sheet
- Per-player adjustable line slider, hit rate computed live from stored arrays
- Bar graph showing last 15 games (green = hit, red = miss)
- Filters by market, team, position

---

## Tech stack (Planned)

| Layer | Technology | Target Host |
|---|---|---|
| Frontend | React (Vite), Tailwind CSS | Vercel |
| Backend | Flask (Python), Gunicorn | Render |
| Database | PostgreSQL (serverless) | Neon Tech |

---

## Architecture highlights (Planned)

### Caching strategy for cold starts
Render's free tier spins down after 15 minutes of inactivity. The planned solution uses a layered cache:

1. In-memory dict (instant, lives for worker lifetime)
2. `/tmp` JSON file (survives worker restarts, loaded at startup)
3. Background thread rebuild (never blocks the request)
4. UptimeRobot pings `/api/health` every 5 min to keep the service warm

### Trust score formula (NBA)
Rather than showing raw hit rate alone (which can be misleading with small samples), each prop will get a 0-100 trust score:

```
Trust = (hitRate * 0.30) + (sampleSizeScore * 0.20) + (lineDeviationScore * 0.25) + (recentTrendScore * 0.15) + (bookmakerConsensusScore * 0.10)
```

### Soccer win probability (Poisson model)
For each fixture, expected home and away goals will be derived from venue-specific historical averages. The Poisson distribution will be summed to compute P(home win), P(draw), P(away win):

```python
for h in range(9):
    for a in range(9):
        p = poisson(lambda_home, h) * poisson(lambda_away, a)
        if h > a: home_prob += p
        elif h == a: draw_prob += p
        else: away_prob += p
```

### Soccer player data pipeline
Player prop data will come from Understat's API (session-based scraping). The pipeline will:

1. Visit league/player page to obtain session cookies
2. Call `getLeagueData/{league}/{season}` for player roster
3. Call `getPlayerData/{id}` per player for match-by-match stats
4. Incremental weekly updates, only fetches games since last known date per player

---

## Data sources (Planned)

| Source | Data |
|---|---|
| NBA API (nba_api) | Player game logs |
| The Odds API | Live betting lines (NBA + soccer) |
| football-data.org | Historical soccer match results |
| Understat.com | Soccer player per-match stats |

---

## Running locally

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (or use a serverless connection string)

### Backend setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # add your API keys
python app.py
```

Required env vars: `DATABASE_URL`, `ODDS_API_KEY`, `FOOTBALL_DATA_KEY`

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173` by default.

---

## Project status

This is an active development project. See the [issues](https://github.com/zoebur404/Scoutprops/issues) for upcoming features and current work.

**Next milestones:**
- [ ] Backend API setup and database schema
- [ ] NBA data ingestion pipeline
- [ ] Basic frontend layout and routing
- [ ] Initial prop display and line slider
- [ ] Trust score implementation
