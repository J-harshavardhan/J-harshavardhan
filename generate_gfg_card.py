import requests
import json
import os

GFG_USERNAME = "jharshavardhan"

def fetch_gfg_stats(username):
    """Fetch stats from GFG public API"""
    url = f"https://geeks-for-geeks-api.vercel.app/{username}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass

    # Fallback API
    url2 = f"https://gfgstatscard.vercel.app/api/{username}"
    try:
        res = requests.get(url2, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass

    return None

def generate_svg(stats):
    """Generate a dracula-themed SVG card from GFG stats"""

    # Extract values with safe fallbacks
    total       = stats.get("totalProblemsSolved", stats.get("solvedStats", {}).get("total", "N/A"))
    score       = stats.get("codingScore", stats.get("score", "N/A"))
    monthly     = stats.get("monthlyScore", stats.get("monthScore", "N/A"))
    streak      = stats.get("currentStreak", stats.get("streak", "N/A"))
    rank        = stats.get("instituteRank", stats.get("rank", "N/A"))
    basic       = stats.get("basic",   stats.get("solvedStats", {}).get("basic",   {}).get("count", "N/A"))
    easy        = stats.get("easy",    stats.get("solvedStats", {}).get("easy",    {}).get("count", "N/A"))
    medium      = stats.get("medium",  stats.get("solvedStats", {}).get("medium",  {}).get("count", "N/A"))
    hard        = stats.get("hard",    stats.get("solvedStats", {}).get("hard",    {}).get("count", "N/A"))

    # Calculate percentage bars (out of rough totals)
    def pct(val, total_q):
        try:
            return min(int(val) / total_q * 100, 100)
        except:
            return 0

    basic_pct  = pct(basic,  200)
    easy_pct   = pct(easy,   400)
    medium_pct = pct(medium, 600)
    hard_pct   = pct(hard,   200)

    svg = f"""<svg width="495" height="220" viewBox="0 0 495 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="495" height="220" rx="10" fill="#282a36" stroke="#44475a" stroke-width="1"/>

  <!-- Header bar -->
  <rect width="495" height="8" rx="4" fill="#2F8D46" y="0"/>

  <!-- GFG Logo circle -->
  <circle cx="40" cy="42" r="16" fill="#2F8D46" opacity="0.2"/>
  <text x="40" y="47" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold"
        fill="#2F8D46" text-anchor="middle">GFG</text>

  <!-- Title -->
  <text x="68" y="36" font-family="Segoe UI, sans-serif" font-size="15" font-weight="bold"
        fill="#f8f8f2">JAGANNATI_HARSHAVARDHAN</text>
  <text x="68" y="52" font-family="Segoe UI, sans-serif" font-size="11"
        fill="#6272a4">GeeksForGeeks Stats</text>

  <!-- Divider -->
  <line x1="20" y1="65" x2="475" y2="65" stroke="#44475a" stroke-width="1"/>

  <!-- Left column: Total + Score -->
  <text x="40" y="95" font-family="Segoe UI, sans-serif" font-size="11" fill="#6272a4">SOLVED</text>
  <text x="40" y="120" font-family="Segoe UI, sans-serif" font-size="36" font-weight="bold" fill="#f8f8f2">{total}</text>

  <text x="40" y="148" font-family="Segoe UI, sans-serif" font-size="11" fill="#6272a4">SCORE</text>
  <text x="40" y="166" font-family="Segoe UI, sans-serif" font-size="20" font-weight="bold" fill="#50fa7b">{score}</text>

  <text x="40" y="186" font-family="Segoe UI, sans-serif" font-size="11" fill="#6272a4">STREAK</text>
  <text x="40" y="204" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#ffb86c">{streak} days 🔥</text>

  <!-- Vertical divider -->
  <line x1="160" y1="75" x2="160" y2="210" stroke="#44475a" stroke-width="1"/>

  <!-- Right column: Difficulty bars -->
  <text x="180" y="90" font-family="Segoe UI, sans-serif" font-size="11" fill="#6272a4">DIFFICULTY BREAKDOWN</text>

  <!-- Basic -->
  <text x="180" y="113" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2">Basic</text>
  <text x="460" y="113" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2" text-anchor="end">{basic}</text>
  <rect x="180" y="117" width="270" height="6" rx="3" fill="#44475a"/>
  <rect x="180" y="117" width="{int(basic_pct * 2.7)}" height="6" rx="3" fill="#8be9fd"/>

  <!-- Easy -->
  <text x="180" y="143" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2">Easy</text>
  <text x="460" y="143" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2" text-anchor="end">{easy}</text>
  <rect x="180" y="147" width="270" height="6" rx="3" fill="#44475a"/>
  <rect x="180" y="147" width="{int(easy_pct * 2.7)}" height="6" rx="3" fill="#50fa7b"/>

  <!-- Medium -->
  <text x="180" y="173" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2">Medium</text>
  <text x="460" y="173" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2" text-anchor="end">{medium}</text>
  <rect x="180" y="177" width="270" height="6" rx="3" fill="#44475a"/>
  <rect x="180" y="177" width="{int(medium_pct * 2.7)}" height="6" rx="3" fill="#ffb86c"/>

  <!-- Hard -->
  <text x="180" y="203" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2">Hard</text>
  <text x="460" y="203" font-family="Segoe UI, sans-serif" font-size="12" fill="#f8f8f2" text-anchor="end">{hard}</text>
  <rect x="180" y="207" width="270" height="6" rx="3" fill="#44475a"/>
  <rect x="180" y="207" width="{int(hard_pct * 2.7)}" height="6" rx="3" fill="#ff5555"/>
</svg>"""

    return svg


def generate_fallback_svg():
    """Generate SVG with hardcoded current stats if API fails"""
    class FallbackStats:
        pass
    stats = {
        "totalProblemsSolved": 95,
        "codingScore": 255,
        "monthlyScore": 56,
        "currentStreak": 13,
        "instituteRank": "#10",
        "basic": 17,
        "easy": 32,
        "medium": 38,
        "hard": 8
    }
    return generate_svg(stats)


if __name__ == "__main__":
    print(f"Fetching GFG stats for: {GFG_USERNAME}")
    stats = fetch_gfg_stats(GFG_USERNAME)

    if stats:
        print(f"Stats fetched successfully: {json.dumps(stats, indent=2)[:300]}")
        svg_content = generate_svg(stats)
    else:
        print("API fetch failed — using fallback hardcoded stats")
        svg_content = generate_fallback_svg()

    with open("gfg-stats.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("gfg-stats.svg written successfully!")
