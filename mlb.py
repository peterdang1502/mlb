import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.mlb.com/schedule"
page = requests.get(URL)

team_abbreviations = {
    "CHC": "Chi Cubs",
    "LAD": "LA Dodgers",
    "NYY": "NY Yankees",
    "AZ": "Arizona",
    "BOS": "Boston",
    "DET": "Detroit",
    "MIL": "Milwaukee",
    "TOR": "Toronto",
    "PHI": "Philadelphia",
    "TB": "Tampa Bay",
    "CIN": "Cincinnati",
    "SEA": "Seattle",
    "STL": "St. Louis",
    "NYM": "NY Mets",
    "ATH": "Sacramento",
    "WSH": "Washington",
    "LAA": "LA Angels",
    "HOU": "Houston",
    "MIA": "Miami",
    "BAL": "Baltimore",
    "MIN": "Minnesota",
    "TEX": "Texas",
    "SF": "SF Giants",
    "ATL": "Atlanta",
    "SD": "San Diego",
    "CLE": "Cleveland",
    "CWS": "Chi Sox",
    "COL": "Colorado",
    "KC": "Kansas City",
    "PIT": "Pittsburgh"
}

stats = [
    "runs-per-game",
    # "at-bats",
    "hits-per-game",
    "home-runs-per-game",
    "singles-per-game",
    "doubles-per-game",
    "triples-per-game",
    "rbis-per-game",
    "walks-per-game",
    "strikeouts-per-game",
    "stolen-bases-per-game",
    # "stolen-bases-attempted",
    # "caught-stealing",
    # "sacrifice-hits",
    # "sacrifice-flys",
    # "left-on-base",
    # "team-left-on-base",
    "hit-by-pitch-per-game",
    # "grounded-into-double-plays",
    # "runners-left-in-scoring-position",
    "total-bases-per-game",
    "batting-average",
    # "slugging-%",
    # "on-base-%",
    "on-base-plus-slugging-pct",
    "outs-pitched-per-game",
    "strikeouts-per-9",
]

inverse_stats = [
    "strikeouts-per-game",
    # "earned-runs-against-per-game",
    "earned-run-average",
    # "walks-plus-hits-per-inning-pitched",
    "hits-per-9",
    "home-runs-per-9",
    "walks-per-9",
    # "strikeouts-per-walk",
    # "shutouts-per-game"
]

def get_stats(type, away, home, score, inverse = False):
    stats_url = "https://www.teamrankings.com/mlb/stat/" + type
    stat_page = requests.get(stats_url)

    stat_soup = BeautifulSoup(stat_page.content, "html.parser")
    away_td = stat_soup.find("td", {"data-sort" : team_abbreviations.get(away)})
    for i in range(10):
        away_td = away_td.next_sibling
    
    home_td = stat_soup.find("td", {"data-sort" : team_abbreviations.get(home)})
    for i in range(8):
        home_td = home_td.next_sibling
    
    away_score = float(away_td.string)
    home_score = float(home_td.string)
    if away_score == home_score:
        return score

    difference = (max(away_score, home_score) - min(away_score, home_score)) / max(away_score, home_score)
    
    # score += (difference if home_score > away_score else -difference) if not inverse else (-difference if home_score > away_score else difference)
    score += (1 if home_score > away_score else -1) if not inverse else (-1 if home_score > away_score else 1)
    return score



soup = BeautifulSoup(page.content, "html.parser")
grid = soup.find("div", {"id": "gridWrapper"})
div = None
for i in range(1, len(list(grid.children))):
    prev = list(grid.children)[i - 1]
    if prev['data-mlb-test'] == 'gameCardTitles' and datetime.strptime(list(prev.children)[1].string, '%b %d').strftime('%b %d') == datetime.today().strftime('%b %d'):
        div = list(grid.children)[i]
        break

for div2 in div.children:
    div3 = list(div2.children)[0]
    away = list(div3.children)[0]
    home = list(div3.children)[2]
    away = list(list(away.div.div.a.children)[1].div.children)[0].string
    home = list(list(home.div.div.a.children)[1].div.children)[0].string
    print(away + " " + home)

    score = 0
    for stat in stats:
        score = get_stats(stat, away, home, score)
    
    for stat in inverse_stats:
        score = get_stats(stat, away, home, score, True)
    print(score)