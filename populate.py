from openpyxl import load_workbook
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import datetime
import mysql.connector

link_mapping = {
    "NYY": "NYA",
    "TBR": "TBA",
    "NYM": "NYN",
    "WSN": "WAS",
    "KCR": "KCA",
    "CHW": "CHA",
    "CHC": "CHN",
    "STL": "SLN",
    "LAA": "ANA",
    "LAD": "LAN",
    "SDP": "SDN",
    "SFG": "SFN"
}

short_to_full = {
    "ARI": "ArizonaDiamondbacks",
    "ATL": "AtlantaBraves",
    "BAL": "BaltimoreOrioles",
    "BOS": "BostonRedSox",
    "CHN": "ChicagoCubs",          # CHC → CHN
    "CHA": "ChicagoWhiteSox",      # CHW → CHA
    "CIN": "CincinnatiReds",
    "CLE": "ClevelandGuardians",
    "COL": "ColoradoRockies",
    "DET": "DetroitTigers",
    "MIA": "MiamiMarlins",
    "HOU": "HoustonAstros",
    "KCA": "KansasCityRoyals",     # KCR → KCA
    "ANA": "LosAngelesAngels",     # LAA → ANA
    "LAN": "LosAngelesDodgers",    # LAD → LAN
    "MIL": "MilwaukeeBrewers",
    "MIN": "MinnesotaTwins",
    "NYN": "NewYorkMets",          # NYM → NYN
    "NYA": "NewYorkYankees",       # NYY → NYA
    "ATH": "Athletics",            # OAK → Athletics (kept code simple OAK → ATH)
    "PHI": "PhiladelphiaPhillies",
    "PIT": "PittsburghPirates",
    "SDN": "SanDiegoPadres",       # SDP → SDN
    "SFN": "SanFranciscoGiants",   # SFG → SFN
    "SEA": "SeattleMariners",
    "SLN": "StLouisCardinals",     # STL → SLN
    "TBA": "TampaBayRays",         # TBR → TBA
    "TEX": "TexasRangers",
    "TOR": "TorontoBlueJays",
    "WAS": "WashingtonNationals"   # WSH → WAS
}

name_to_short = {
    "D-backs": "ARI",
    "Braves": "ATL",
    "Orioles": "BAL",
    "Red Sox": "BOS",
    "Cubs": "CHC",
    "White Sox": "CHW",
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
    "Athletics": "ATH",
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

def get_pitcher_id(soup, team):
    try:
        team = soup.find("table", {"id": team + "pitching"})
        pitcher = list(team.tbody.children)[0].th.a
        link = pitcher['href']
        name = pitcher.string

        select = "SELECT id FROM pitchers WHERE name = %s"
        values = (name, )
        cursor.execute(select, values)
        result = cursor.fetchall()

        if len(result) == 0:
            driver.get("https://www.baseball-reference.com" + link)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div = soup.find("div", {"class": "p1"})
            era = list(div.children)[7]
            era = list(era.children)[2].string

            cursor.execute("INSERT INTO pitchers (name, era) VALUES (%s, %s)", (name, float(era)))
            db.commit()

            cursor.execute(select, values)
            result = cursor.fetchall()

        return result[0][0]
    except Exception as e:
        print(e)
        return 

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mlb"
)
cursor = db.cursor()

driver = webdriver.Chrome()
driver.implicitly_wait(10000)

def check_pitcher(name, era):
    select = "SELECT id, era FROM pitchers WHERE name = %s"
    values = (name, )
    cursor.execute(select, values)
    result = cursor.fetchall()

    if result == [] or result[0][1] != era:
        if result == []:
            cursor.execute("INSERT INTO pitchers (name, era) VALUES (%s, %s)", (name, float(era)))
            db.commit()
        else:
            cursor.execute("UPDATE pitchers SET era = %s WHERE name = %s", (float(era), name))
            db.commit()
        
        cursor.execute(select, values)
        result = cursor.fetchall()

    return result[0][0]
        
date = datetime.datetime(2025, 9, 2)

link = "https://www.mlb.com/scores/" + date.strftime("%Y-%m-%d")

page = requests.get(link)

soup = BeautifulSoup(page.content, "html.parser")

links = soup.find_all("a", {"data-mlb-test": "productlink-box"})

for link in links:
    match_link = "https://www.mlb.com" + link["href"]

    header = None
    box = None
    while header == None and box == None:
        driver.get(match_link)
        match_soup = BeautifulSoup(driver.page_source, "html.parser")

        header = match_soup.find("div", {"data-mlb-test": "teamSummaryMatchUpWrapper"})

        box = match_soup.find("div", {"data-mlb-test": "gamedayBoxscoreTeamsWrapper"})

    teams = header.find_all("div", {"data-mlb-test": "teamRecordWrapper"})
    away_team = name_to_short[teams[0].find("div", {"data-mlb-test": "teamNameLabel"}).text]
    home_team = name_to_short[teams[1].find("div", {"data-mlb-test": "teamNameLabel"}).text]

    # print(away_team)
    # print(home_team)

    away_score = int(list(header.children)[1].text)
    home_score = int(list(header.children)[3].text)

    # print(away_score)
    # print(home_score)

    boxes = box.find_all("div", {"data-mlb-test": "gamedayBoxscoreTeamTable"})

    away_box = boxes[1]
    home_box = boxes[3]

    away_pitcher = away_box.find_all("tr")[1]
    home_pitcher = home_box.find_all("tr")[1]

    away_name = away_pitcher.find("a")["aria-label"]
    home_name = home_pitcher.find("a")["aria-label"]

    away_era = away_pitcher.find_all("td")[-1].text
    home_era = home_pitcher.find_all("td")[-1].text

    # print(away_name + " " + away_era)
    # print(home_name + " " + home_era)

    sql = "INSERT INTO matchups (date, away_team, home_team, away_score, home_score, away_pitcher, home_pitcher) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (date.date(), away_team, home_team, away_score, home_score, check_pitcher(away_name, away_era), check_pitcher(home_name, home_era))
    cursor.execute(sql, values)
    db.commit()

driver.quit()