"""
2026 World Cup Winner Prediction — Three-Lens Model
====================================================
Lens 1: What people predict  -> your LinkedIn poll (fill in POLL below)
Lens 2: What the data says   -> Elo-based Monte Carlo bracket simulation
Lens 3: AI-assisted model    -> ensemble blending Elo, FIFA points,
                                market odds, tournament form, and
                                player quality (squad market value)

HOW TO RUN (Sunday/Monday, once semifinalists are known):
  1. Edit SEMIFINAL_1 and SEMIFINAL_2 below with the final four.
  2. Paste your LinkedIn poll results into POLL.
  3. Optionally refresh ODDS_AMERICAN with the latest numbers.
  4. python3 wc2026_model.py

Data snapshot: July 9, 2026 (worldfootballrankings.com, FanDuel/ESPN,
Transfermarkt)
"""

import random
import csv

# ---------------------------------------------------------------- CONFIG ---

# The four semifinalists — edit these on Sunday.
# France is confirmed; the other three come from:
#   Spain vs Belgium, Argentina vs Switzerland, England vs Norway
SEMIFINAL_1 = ("France", "Spain")       # SF July 14
SEMIFINAL_2 = ("Argentina", "England")  # SF July 15

# LinkedIn poll results — % of votes per team (any scale; normalized later).
# Set to None for teams not in your poll.
POLL = {
    "France": None,
    "Spain": None,
    "Argentina": None,
    "England": None,
}

N_SIMS = 200_000
FORM_WEIGHT = 0.25   # how much recent-form Elo boost feeds the AI lens
SQUAD_ELO = 40       # Elo points per 1 std-dev of (log) squad market value

# ------------------------------------------------------------ TEAM DATA ---
# elo / fifa_pts: July 9, 2026. elo_change: gained during this World Cup.
# odds: American, FanDuel Jul 3 (longshots) + ESPN Jul 9 (favorites).
# value: Transfermarkt squad market value, EUR millions (player ratings proxy).
TEAMS = {
    "France":      {"elo": 1925.86, "fifa": 1870.70, "elo_change": +55.17, "odds": +180,  "value": 1520.0},
    "Argentina":   {"elo": 1925.15, "fifa": 1877.27, "elo_change": +47.88, "odds": +400,  "value": 807.5},
    "Spain":       {"elo": 1912.34, "fifa": 1874.71, "elo_change": +37.63, "odds": +360,  "value": 1220.0},
    "England":     {"elo": 1871.39, "fifa": 1828.02, "elo_change": +43.36, "odds": +460,  "value": 1360.0},
    "Belgium":     {"elo": 1778.36, "fifa": 1742.24, "elo_change": +36.12, "odds": +4500, "value": 547.5},
    "Switzerland": {"elo": 1710.88, "fifa": 1650.06, "elo_change": +60.82, "odds": +5500, "value": 332.5},
    "Norway":      {"elo": 1651.29, "fifa": 1557.44, "elo_change": +93.85, "odds": +4000, "value": 589.9},
}

# ------------------------------------------------------------- HELPERS ---

def elo_win_prob(team_a, team_b, ratings):
    """P(team_a beats team_b) incl. extra time/penalties (no draws)."""
    dr = ratings[team_a] - ratings[team_b]
    return 1.0 / (1.0 + 10 ** (-dr / 400.0))


def american_to_prob(odds):
    """Implied probability from American odds (before de-vig)."""
    return 100 / (odds + 100) if odds > 0 else -odds / (-odds + 100)


def devig(probs):
    total = sum(probs.values())
    return {k: v / total for k, v in probs.items()}


def simulate(ratings, sf1, sf2, n=N_SIMS):
    """Monte Carlo the bracket: two semis + final. Returns P(champion)."""
    wins = {t: 0 for t in (*sf1, *sf2)}
    p_sf1 = elo_win_prob(sf1[0], sf1[1], ratings)
    p_sf2 = elo_win_prob(sf2[0], sf2[1], ratings)
    # cache final matchup probs
    p_final = {}
    for a in sf1:
        for b in sf2:
            p_final[(a, b)] = elo_win_prob(a, b, ratings)
    for _ in range(n):
        f1 = sf1[0] if random.random() < p_sf1 else sf1[1]
        f2 = sf2[0] if random.random() < p_sf2 else sf2[1]
        champ = f1 if random.random() < p_final[(f1, f2)] else f2
        wins[champ] += 1
    return {t: w / n for t, w in wins.items()}

# ---------------------------------------------------------------- LENSES ---

def lens_data():
    """Pure Elo Monte Carlo."""
    ratings = {t: d["elo"] for t, d in TEAMS.items()}
    return simulate(ratings, SEMIFINAL_1, SEMIFINAL_2)


def squad_adjustments():
    """Squad-strength (player quality) signal: z-score of log market value
    across all remaining teams, scaled to Elo points."""
    import math
    logs = {t: math.log(d["value"]) for t, d in TEAMS.items()}
    mean = sum(logs.values()) / len(logs)
    var = sum((v - mean) ** 2 for v in logs.values()) / len(logs)
    std = var ** 0.5
    return {t: SQUAD_ELO * (v - mean) / std for t, v in logs.items()}


def lens_ai():
    """Ensemble rating: Elo + FIFA-points signal + form boost + squad
    strength (player-quality proxy), then averaged with de-vigged market
    odds (market = wisdom of sharp money)."""
    final4 = [*SEMIFINAL_1, *SEMIFINAL_2]
    squad = squad_adjustments()
    ratings = {}
    for t in final4:
        d = TEAMS[t]
        # rescale FIFA points onto Elo-like scale and blend
        base = 0.6 * d["elo"] + 0.4 * (d["fifa"] + 60)
        ratings[t] = base + FORM_WEIGHT * d["elo_change"] + squad[t]
    sim = simulate(ratings, SEMIFINAL_1, SEMIFINAL_2)
    market = devig({t: american_to_prob(TEAMS[t]["odds"]) for t in final4})
    return {t: 0.65 * sim[t] + 0.35 * market[t] for t in final4}


def lens_people():
    """Normalized LinkedIn poll."""
    votes = {t: v for t, v in POLL.items() if v is not None}
    if not votes:
        return None
    return devig(votes)

# ------------------------------------------------------------------ MAIN ---

def main():
    final4 = [*SEMIFINAL_1, *SEMIFINAL_2]
    data = lens_data()
    ai = lens_ai()
    people = lens_people()

    print(f"\n2026 World Cup — title probabilities ({N_SIMS:,} sims)")
    print(f"Semis: {SEMIFINAL_1[0]} v {SEMIFINAL_1[1]} | "
          f"{SEMIFINAL_2[0]} v {SEMIFINAL_2[1]}\n")
    header = f"{'Team':<12}{'Poll':>8}{'Data (Elo)':>12}{'AI model':>10}"
    print(header)
    print("-" * len(header))
    for t in sorted(final4, key=lambda x: -ai[x]):
        poll_s = f"{people[t]*100:5.1f}%" if people and t in people else "   —"
        print(f"{t:<12}{poll_s:>8}{data[t]*100:>11.1f}%{ai[t]*100:>9.1f}%")

    with open("wc2026_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["team", "poll", "data_elo", "ai_model"])
        for t in final4:
            w.writerow([t,
                        round(people[t], 4) if people and t in people else "",
                        round(data[t], 4), round(ai[t], 4)])
    print("\nSaved: wc2026_results.csv")


if __name__ == "__main__":
    main()
