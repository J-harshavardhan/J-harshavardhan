#!/usr/bin/env python3
"""
generate_gfg_card.py
Fetches live GFG stats and generates a beautiful SVG card.
Uses GFG's own internal API with browser-like headers.
Fallback: uses your latest known stats so card never shows N/A.
"""

import requests
import json
import re
from datetime import datetime
import math

GFG_USERNAME = "jharshavardhan"

# ── Your latest known stats (fallback if API fails) ────────────────────────
# Update these manually when you want to force-refresh
FALLBACK = {
    "solved": 100,
    "score":  273,
    "rank":   5,
    "streak": 13,
    "school": 0,
    "basic":  17,
    "easy":   33,
    "medium": 42,
    "hard":   8,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.geeksforgeeks.org/",
    "Origin": "https://www.geeksforgeeks.org",
    "Connection": "keep-alive",
}


def fetch_stats():
    """Try every known GFG API endpoint."""
    
    apis = [
        # GFG's own practice API endpoints
        f"https://practiceapi.geeksforgeeks.org/api/v1/user/info/?handle={GFG_USERNAME}",
        f"https://practiceapi.geeksforgeeks.org/api/v1/user/?handle={GFG_USERNAME}",
        f"https://practiceapi.geeksforgeeks.org/api/latest/header-web/?",
        # Third-party scrapers
        f"https://geeks-for-geeks-api.vercel.app/{GFG_USERNAME}",
        f"https://gfg-stats.tashif.codes/{GFG_USERNAME}",
        f"https://geeks-for-geeks-stats-api.vercel.app/?raw=y&userName={GFG_USERNAME}",
        f"https://gfg-api-fefa.onrender.com/{GFG_USERNAME}",
    ]

    for url in apis:
        try:
            print(f"Trying: {url}")
            r = requests.get(url, headers=HEADERS, timeout=8)
            print(f"  Status: {r.status_code}")
            if r.status_code != 200:
                continue
            
            d = r.json()
            print(f"  Keys: {list(d.keys())[:8]}")
            
            # Try all known field name patterns
            solved = (
                d.get("totalProblemsSolved")
                or d.get("total_problems_solved")
                or d.get("pod_solved_count")
                or d.get("totalSolved")
                or d.get("Total")
                or (d.get("info") or {}).get("totalProblemsSolved")
                or (d.get("data") or {}).get("total_problems_solved")
                or (d.get("data") or {}).get("pod_solved_count")
            )

            if solved and int(solved) > 0:
                score = (
                    d.get("codingScore") or d.get("overallScore") or d.get("CodingScore")
                    or (d.get("info") or {}).get("codingScore")
                    or (d.get("data") or {}).get("score")
                    or FALLBACK["score"]
                )
                rank = (
                    d.get("instituteRank") or d.get("rank") or d.get("GlobalRank")
                    or (d.get("info") or {}).get("instituteRank")
                    or (d.get("data") or {}).get("institute_rank")
                    or FALLBACK["rank"]
                )
                streak = (
                    d.get("currentStreak") or d.get("streak")
                    or (d.get("info") or {}).get("currentStreak")
                    or (d.get("data") or {}).get("current_streak")
                    or FALLBACK["streak"]
                )
                
                # Difficulty breakdown
                ss = d.get("solvedStats") or d.get("problemsByDifficulty") or d.get("problems_solved") or {}
                
                def get_count(key):
                    v = ss.get(key, {})
                    if isinstance(v, dict): return int(v.get("count", 0))
                    if isinstance(v, list): return len(v)
                    if isinstance(v, (int, str)): return int(v or 0)
                    return int(d.get(key, 0) or 0)
                
                result = {
                    "solved": int(solved),
                    "score":  score,
                    "rank":   rank,
                    "streak": streak,
                    "school": get_count("school"),
                    "basic":  get_count("basic"),
                    "easy":   get_count("easy"),
                    "medium": get_count("medium"),
                    "hard":   get_count("hard"),
                }
                print(f"  ✅ Got data: solved={result['solved']}")
                return result
                
        except Exception as e:
            print(f"  Error: {e}")
            continue

    # Scrape GFG profile HTML as last resort
    try:
        print(f"Trying HTML scrape...")
        r = requests.get(
            f"https://www.geeksforgeeks.org/user/{GFG_USERNAME}/",
            headers={**HEADERS, "Accept": "text/html,application/xhtml+xml"},
            timeout=10
        )
        if r.status_code == 200:
            html = r.text
            def extract(pattern):
                m = re.search(pattern, html)
                return int(m.group(1)) if m else None

            solved = extract(r'"totalProblemsSolved"\s*:\s*(\d+)')
            if solved and solved > 0:
                return {
                    "solved": solved,
                    "score":  extract(r'"codingScore"\s*:\s*(\d+)') or FALLBACK["score"],
                    "rank":   extract(r'"instituteRank"\s*:\s*"?(\d+)"?') or FALLBACK["rank"],
                    "streak": extract(r'"currentStreak"\s*:\s*"?(\d+)"?') or FALLBACK["streak"],
                    "school": extract(r'"school"\s*:\s*\{"count"\s*:\s*(\d+)') or 0,
                    "basic":  extract(r'"basic"\s*:\s*\{"count"\s*:\s*(\d+)') or FALLBACK["basic"],
                    "easy":   extract(r'"easy"\s*:\s*\{"count"\s*:\s*(\d+)') or FALLBACK["easy"],
                    "medium": extract(r'"medium"\s*:\s*\{"count"\s*:\s*(\d+)') or FALLBACK["medium"],
                    "hard":   extract(r'"hard"\s*:\s*\{"count"\s*:\s*(\d+)') or FALLBACK["hard"],
                }
    except Exception as e:
        print(f"  Scrape error: {e}")

    print("⚠️  All APIs failed — using fallback stats")
    return FALLBACK


def make_svg(s):
    solved = int(s["solved"])
    score  = s["score"]
    rank   = s["rank"]
    streak = s["streak"]
    school = int(s.get("school", 0))
    basic  = int(s.get("basic",  0))
    easy   = int(s.get("easy",   0))
    medium = int(s.get("medium", 0))
    hard   = int(s.get("hard",   0))
    total  = school + basic + easy + medium + hard

    # Circle
    R      = 40
    circ   = 2 * math.pi * R
    pct    = min(solved / 250.0, 1.0)
    dash   = round(pct * circ, 1)

    # Bar widths
    def bar(v, mx): return max(4, min(round(v / mx * 230), 230))

    updated = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    return f"""<svg width="500" height="230" viewBox="0 0 500 230"
  xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gb" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#14532d"/>
      <stop offset="100%" stop-color="#166534"/>
    </linearGradient>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1c2333"/>
      <stop offset="100%" stop-color="#161b27"/>
    </linearGradient>
    <linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#16a34a"/>
    </linearGradient>
  </defs>

  <!-- Card -->
  <rect width="500" height="230" rx="12" fill="url(#bg)" stroke="#166534" stroke-width="1.5"/>
  <rect width="500" height="7"   rx="3.5" fill="url(#gb)"/>

  <!-- Header -->
  <circle cx="30" cy="36" r="9" fill="#16a34a"/>
  <text x="30" y="41" font-family="Segoe UI,sans-serif" font-size="11"
        font-weight="900" fill="#fff" text-anchor="middle">GFG</text>
  <text x="50" y="38" font-family="Segoe UI,sans-serif" font-size="14"
        font-weight="700" fill="#f1f5f9" letter-spacing="0.3">GeeksForGeeks Stats</text>
  <text x="50" y="54" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">@{GFG_USERNAME}</text>
  <line x1="16" y1="66" x2="484" y2="66" stroke="#1e293b" stroke-width="1.2"/>

  <!-- Circle -->
  <circle cx="75" cy="126" r="{R}" fill="none" stroke="#1e293b" stroke-width="6"/>
  <circle cx="75" cy="126" r="{R}" fill="none" stroke="url(#cg)"
          stroke-width="6" stroke-linecap="round"
          stroke-dasharray="{dash} {round(circ,1)}"
          stroke-dashoffset="0"
          transform="rotate(-90 75 126)"/>
  <text x="75" y="131" font-family="Segoe UI,sans-serif" font-size="22"
        font-weight="800" fill="#f1f5f9" text-anchor="middle">{solved}</text>
  <text x="75" y="178" font-family="Segoe UI,sans-serif" font-size="9"
        fill="#64748b" text-anchor="middle" letter-spacing="1">SOLVED</text>

  <!-- Stats below circle -->
  <text x="16" y="198" font-family="Segoe UI,sans-serif" font-size="9" fill="#64748b" letter-spacing="0.5">SCORE</text>
  <text x="16" y="213" font-family="Segoe UI,sans-serif" font-size="17" font-weight="700" fill="#4ade80">{score}</text>

  <text x="82" y="198" font-family="Segoe UI,sans-serif" font-size="9" fill="#64748b" letter-spacing="0.5">RANK</text>
  <text x="82" y="213" font-family="Segoe UI,sans-serif" font-size="17" font-weight="700" fill="#fbbf24">#{rank}</text>

  <text x="16" y="225" font-family="Segoe UI,sans-serif" font-size="9" fill="#64748b" letter-spacing="0.5">STREAK · {streak} days 🔥</text>

  <!-- Divider -->
  <line x1="145" y1="74" x2="145" y2="222" stroke="#1e293b" stroke-width="1.2"/>

  <!-- Breakdown header -->
  <text x="163" y="88" font-family="Segoe UI,sans-serif" font-size="9"
        fill="#64748b" letter-spacing="1.2">DIFFICULTY BREAKDOWN</text>

  <!-- School -->
  <text x="163" y="107" font-family="Segoe UI,sans-serif" font-size="11" fill="#7dd3fc">School</text>
  <text x="484" y="107" font-family="Segoe UI,sans-serif" font-size="11" fill="#7dd3fc" text-anchor="end">{school}</text>
  <rect x="163" y="111" width="230" height="5" rx="2.5" fill="#1e293b"/>
  <rect x="163" y="111" width="{bar(school,30)}" height="5" rx="2.5" fill="#7dd3fc"/>

  <!-- Basic -->
  <text x="163" y="129" font-family="Segoe UI,sans-serif" font-size="11" fill="#86efac">Basic</text>
  <text x="484" y="129" font-family="Segoe UI,sans-serif" font-size="11" fill="#86efac" text-anchor="end">{basic}</text>
  <rect x="163" y="133" width="230" height="5" rx="2.5" fill="#1e293b"/>
  <rect x="163" y="133" width="{bar(basic,50)}" height="5" rx="2.5" fill="#86efac"/>

  <!-- Easy -->
  <text x="163" y="151" font-family="Segoe UI,sans-serif" font-size="11" fill="#4ade80">Easy</text>
  <text x="484" y="151" font-family="Segoe UI,sans-serif" font-size="11" fill="#4ade80" text-anchor="end">{easy}</text>
  <rect x="163" y="155" width="230" height="5" rx="2.5" fill="#1e293b"/>
  <rect x="163" y="155" width="{bar(easy,100)}" height="5" rx="2.5" fill="#4ade80"/>

  <!-- Medium -->
  <text x="163" y="173" font-family="Segoe UI,sans-serif" font-size="11" fill="#fb923c">Medium</text>
  <text x="484" y="173" font-family="Segoe UI,sans-serif" font-size="11" fill="#fb923c" text-anchor="end">{medium}</text>
  <rect x="163" y="177" width="230" height="5" rx="2.5" fill="#1e293b"/>
  <rect x="163" y="177" width="{bar(medium,150)}" height="5" rx="2.5" fill="#fb923c"/>

  <!-- Hard -->
  <text x="163" y="195" font-family="Segoe UI,sans-serif" font-size="11" fill="#f87171">Hard</text>
  <text x="484" y="195" font-family="Segoe UI,sans-serif" font-size="11" fill="#f87171" text-anchor="end">{hard}</text>
  <rect x="163" y="199" width="230" height="5" rx="2.5" fill="#1e293b"/>
  <rect x="163" y="199" width="{bar(hard,50)}" height="5" rx="2.5" fill="#f87171"/>

  <!-- Footer -->
  <text x="484" y="222" font-family="Segoe UI,sans-serif" font-size="8"
        fill="#334155" text-anchor="end">Updated: {updated}</text>
</svg>"""


if __name__ == "__main__":
    print(f"🔄 Fetching GFG stats for @{GFG_USERNAME}...")
    stats = fetch_stats()
    print(f"📊 Final stats: {stats}")
    svg = make_svg(stats)
    with open("gfg-stats.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ gfg-stats.svg saved!")
