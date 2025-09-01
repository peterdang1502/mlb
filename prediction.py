import mysql.connector
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mlb"
)
cursor = db.cursor()

def new_score(away_team, home_team, away_era, home_era):
    sql = """SELECT date, away_team, home_team, away_score, home_score, p1.name, p1.era, p2.name, p2.era
        FROM matchups JOIN pitchers AS p1 ON matchups.away_pitcher = p1.id JOIN pitchers AS p2 ON matchups.home_pitcher = p2.id
        WHERE away_team = %s AND home_team = %s"""
    values = (away_team, home_team)
    cursor.execute(sql, values)
    result = cursor.fetchall()
    new_res = []
    for row in result:
        new_res.append([row[0], row[1], row[2], row[3] - (row[8] - home_era), row[4] - (row[6] - away_era)])

    return new_res

away_team = input("away?")
home_team = input("home?")
away_pitcher = float(input("away era?"))
home_pitcher = float(input("home era?"))

sql = """SELECT date, away_team, home_team, away_score, home_score, p1.name, p1.era, p2.name, p2.era
        FROM matchups JOIN pitchers AS p1 ON matchups.away_pitcher = p1.id JOIN pitchers AS p2 ON matchups.home_pitcher = p2.id
        WHERE (away_team = %s AND home_team = %s) OR (away_team = %s AND home_team = %s)"""

values = (away_team, home_team, home_team, away_team)
cursor.execute(sql, values)
result = cursor.fetchall()
for row in result:
    print(row)

print("\n")

new_res = []
new_res.extend(new_score(away_team, home_team, away_pitcher, home_pitcher))
new_res.extend(new_score(home_team, away_team, home_pitcher, away_pitcher))

new_res_sorted = sorted(new_res, key=lambda x: x[0])

for row in new_res_sorted:
    if away_team == row[2]:
        row[1] = away_team
        row[2] = home_team
        temp = row[3]
        row[3] = row[4]
        row[4] = temp
    print(row)