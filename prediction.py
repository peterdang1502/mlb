def predict(away_pitcher, home_pitcher, away_score, home_score, away_era, home_era):
    home_score -= away_era - away_pitcher
    away_score -= home_era - home_pitcher
    print(str(away_score) + " " + str(home_score))

away_pitcher = float(input("away?"))
home_pitcher = float(input("home?"))
count = input("how many games?")
games = []
for i in range(int(count)):
    away_score = int(input("away score?"))
    home_score = int(input("home score?"))
    away_era = float(input("away pitcher?"))
    home_era = float(input("home pitcher?"))
    games.append([away_score, home_score, away_era, home_era])

for game in games:
    predict(away_pitcher, home_pitcher, game[0], game[1], game[2], game[3])
