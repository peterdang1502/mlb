import requests
from bs4 import BeautifulSoup
from datetime import datetime

team_abbreviations = {
    "ARI": "Arizona",
    "ATL": "Atlanta",
    "BAL": "Baltimore",
    "BOS": "Boston",
    "CHC": "Chi Cubs",
    "CWS": "Chi Sox",
    "CIN": "Cincinnati",
    "CLE": "Cleveland",
    "COL": "Colorado",
    "DET": "Detroit",
    "HOU": "Houston",
    "KCR": "Kansas City",
    "LAA": "LA Angels",
    "LAD": "LA Dodgers",
    "MIA": "Miami",
    "MIL": "Milwaukee",
    "MIN": "Minnesota",
    "NYM": "NY Mets",
    "NYY": "NY Yankees",
    "OAK": "Sacramento",
    "PHI": "Philadelphia",
    "PIT": "Pittsburgh",
    "SDP": "San Diego",
    "SFG": "SF Giants",
    "SEA": "Seattle",
    "STL": "St. Louis",
    "TBR": "Tampa Bay",
    "TEX": "Texas",
    "TOR": "Toronto",
    "WSN": "Washington"
}

name_to_short = {
    "D-backs": "ARI",
    "Braves": "ATL",
    "Orioles": "BAL",
    "Red Sox": "BOS",
    "Cubs": "CHC",
    "White Sox": "CWS",
    "Reds": "CIN",
    "Guardians": "CLE",
    "Rockies": "COL",
    "Tigers": "DET",
    "Astros": "HOU",
    "Royals": "KCR",
    "Angels": "LAA",
    "Dodgers": "LAD",
    "Marlins": "MIA",
    "Brewers": "MIL",
    "Twins": "MIN",
    "Mets": "NYM",
    "Yankees": "NYY",
    "Athletics": "OAK",
    "Phillies": "PHI",
    "Pirates": "PIT",
    "Padres": "SDP",
    "Giants": "SFG",
    "Mariners": "SEA",
    "Cardinals": "STL",
    "Rays": "TBR",
    "Rangers": "TEX",
    "Blue Jays": "TOR",
    "Nationals": "WSN"
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

def get_stats(type, away_teams, home_teams, scores, inverse = False):
    stats_url = "https://www.teamrankings.com/mlb/stat/" + type
    stat_page = requests.get(stats_url)

    stat_soup = BeautifulSoup(stat_page.content, "html.parser")

    n = len(away_teams)
    for i in range(n):
        away_team = away_teams[i]
        home_team = home_teams[i]

        away_td = stat_soup.find("td", {"data-sort" : team_abbreviations.get(away_team)})
        for j in range(10):
            away_td = away_td.next_sibling
        
        home_td = stat_soup.find("td", {"data-sort" : team_abbreviations.get(home_team)})
        for j in range(8):
            home_td = home_td.next_sibling
        
        away_score = float(away_td.string)
        home_score = float(home_td.string)
        if away_score == home_score:
            continue

        # difference = (max(away_score, home_score) - min(away_score, home_score)) / max(away_score, home_score)
        # score += (difference if home_score > away_score else -difference) if not inverse else (-difference if home_score > away_score else difference)

        scores[i] += (1 if home_score > away_score else -1) if not inverse else (-1 if home_score > away_score else 1)


URL = "https://www.mlb.com/scores/" + datetime.today().strftime("%Y-%m-%d")
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
grid = soup.find("div", {"id": "gridWrapper"})

games = grid.find_all("div", {"data-test-mlb": "singleGameContainer"})
away_teams = []
home_teams = []
scores = []

for game in games:
    teams = game.find_all("div", {"data-mlb-test": "teamRecordWrapper"})
    away = teams[0]
    home = teams[1]

    away_team = away.find("a")["data-team-name"]
    home_team = home.find("a")["data-team-name"]

    away_team = name_to_short[away_team]
    home_team = name_to_short[home_team]
    away_teams.append(away_team)
    home_teams.append(home_team)
    scores.append(0)

for stat in stats:
    get_stats(stat, away_teams, home_teams, scores)

for stat in inverse_stats:
    get_stats(stat, away_teams, home_teams, scores, True)

n = len(away_teams)
for i in range(n):
    print(away_teams[i] + " " + home_teams[i] + " " + str(scores[i]))

    # score = 0
    # for stat in stats:
    #     score = get_stats(stat, away_team, home_team, score)

    # for stat in inverse_stats:
    #     score = get_stats(stat, away_team, home_team, score, True)
    # print(score)