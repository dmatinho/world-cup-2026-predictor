# 🏆 2026 World Cup — Three-Lens Prediction

An interactive dashboard comparing three ways of predicting the 2026 World Cup winner:

1. **🗳️ What people predict** — crowd wisdom from a LinkedIn poll
2. **📊 What the data says** — Elo ratings (every international match since 1901, importance-weighted) run through 200,000 Monte Carlo simulations of the remaining bracket
3. **🤖 What an AI-assisted model says** — an ensemble of Elo, FIFA points, tournament form, player quality (Transfermarkt squad market values), and de-vigged betting-market odds

**Live demo:** enable GitHub Pages on this repo (Settings → Pages → Deploy from branch → main, root) and it's served at `https://<username>.github.io/<repo>/`.

## How it works

Each match is decided by an Elo-based win probability: `P = 1 / (1 + 10^(−ΔElo/400))`. The bracket (two semifinals + final) is simulated 200,000 times in the browser; a team's title probability is the share of simulated tournaments it wins. See the "Why Monte Carlo?" section in the dashboard for the full explanation.

## Data sources

Elo & FIFA ratings: worldfootballrankings.com (Jul 9, 2026) · Odds: FanDuel/ESPN (Jul 3–9, 2026) · Squad values: Transfermarkt (2026 WC squads). Data is embedded in `index.html` and updated manually.

---

Built with ❤️‍🔥 by [Daniela Matinho](https://www.linkedin.com/in/danielamatinho) · AI, Actually Newsletter
