# 🏆 2026 World Cup — Three-Lens Prediction

An interactive model and dashboard comparing three ways of predicting the 2026 World Cup winner:

1. **🗳️ What people predict** — crowd wisdom from a LinkedIn poll
2. **📊 What the data says** — Elo ratings (every international match since 1901, importance-weighted) run through 200,000 Monte Carlo simulations of the remaining bracket
3. **🤖 What an AI-assisted model says** — a base rating from Elo and FIFA points (60/40), adjusted for tournament form and player quality (Transfermarkt squad market values), then blended with de-vigged betting-market odds

**Live dashboard:** https://dmatinho.github.io/world-cup-2026-predictor/.

## How it works

- Each match is decided by an Elo-based win probability: `P = 1 / (1 + 10^(−ΔElo/400))`. 

- The bracket (two semifinals + final) is simulated 200,000 times in the browser; Why 200,000? Because simulations are random, running them twice gives slightly different answers — that wobble shrinks with more runs. The noise on a probability estimate is roughly √(p(1−p)/n): at 10,000 runs, a "35%" could read anywhere from 34% to 36%; at 200,000 runs it's stable to about ±0.2% — steadier than the inputs themselves. Beyond that, more simulations add compute, not accuracy: the answer is only as good as the ratings going in. 

- Why Monte Carlo?": A tournament isn't one prediction — it's a chain of them. To win, a team must survive its semifinal and beat whoever emerges from the other side, and each possible opponent changes the odds. Instead of trying to write one giant formula, Monte Carlo just plays out the whole bracket over and over, flipping a weighted coin for every match (weighted by Elo strength). A team's title probability is simply the share of simulated tournaments it wins. Same technique banks use for risk and forecasters use for elections.

## Data sources

- Elo & FIFA ratings: worldfootballrankings.com (Jul 9, 2026) 
- Odds: FanDuel/ESPN (Jul 3–9, 2026) 
- Squad values: Transfermarkt (2026 WC squads) 
- Data is embedded in `index.html` and updated manually.

## Run the model yourself

The same model is available as a standalone script:

    python3 wc2026_model.py

Edit `SEMIFINAL_1`, `SEMIFINAL_2`, and `POLL` at the top of the file,
then run — it prints all three lenses and saves `wc2026_results.csv`.

---

- Powered By Fable 5 - Claude

- Built with ❤️‍🔥 by [Daniela Matinho](https://www.linkedin.com/in/danielamatinho) · AI, Actually Newsletter
