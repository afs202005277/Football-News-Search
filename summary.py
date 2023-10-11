import csv
import random
import expressions
import csv
import sys

sys.path.append('./scraping/db')

from db import DB

file_name = "full_data.csv"

encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1']


def summarize(game):
    home, away, events, date, hour, winner = game

    home_winning_start, away_winning_start, draw_start = expressions.createStartExpressions(home, away)

    text = ""

    if winner == "home":
        text += home_winning_start[random.randint(0, 4)] + " Resumo do Jogo: "
    elif winner == "away":
        text += away_winning_start[random.randint(0, 4)] + " Resumo do Jogo: "
    elif winner == "draw":
        text += draw_start[random.randint(0, 4)] + " Resumo do Jogo: "

    for event in events:
        if event == '': continue
        try:
            temp, name = event.split(' - ')
            if '(' in name:
                name = name.split('(')[0]
            minute, eve = temp.split('\' ')
            minute = minute[:len(minute) - 1]
            eve = eve.lower()
        except:
            continue

        goal_home_eve, goal_away_eve, own_goal_home_eve, own_goal_away_eve, yellow_card_eve, red_card_eve, penalty_missed_home_eve, penalty_missed_away_eve = expressions.createExpressions(
            home, away, minute, name)

        if eve == 'goal_home':
            text += goal_home_eve[random.randint(0, 4)] + " "
        elif eve == 'goal_away':
            text += goal_away_eve[random.randint(0, 4)] + " "
        elif 'yellow' in eve:
            text += yellow_card_eve[random.randint(0, 4)] + " "
        elif 'red' in eve:
            text += red_card_eve[random.randint(0, 4)] + " "
        elif eve == 'own_home':
            text += own_goal_home_eve[random.randint(0, 4)] + " "
        elif eve == 'own_away':
            text += own_goal_away_eve[random.randint(0, 4)] + " "
        elif eve == 'penalty_missed_home':
            text += penalty_missed_home_eve[random.randint(0, 4)] + " "
        elif eve == 'penalty_missed_away':
            text += penalty_missed_away_eve[random.randint(0, 4)] + " "

    return text


for encoding in encodings_to_try:
    try:
        # Read the contents of the file with the specified encoding
        with open(file_name, 'r', encoding=encoding) as file:
            lines = file.readlines()

        info = []

        for line in lines:
            csv_reader = csv.reader([line])
            parsed_line = next(csv_reader)
            home = parsed_line[1]
            away = parsed_line[2]
            commentary = parsed_line[3]
            date = parsed_line[5]
            hour = parsed_line[6]
            winner = parsed_line[11].lower()
            commentaryFormated = commentary[1:len(commentary) - 1].replace(", ", ",").replace("\"", "").split(',')
            data = commentaryFormated if commentary != "" else []
            info.append([home, away, data, date, hour, winner])

        break  # Exit the loop if successful
    except UnicodeDecodeError:
        continue  # Try the next encoding if decoding fails

db = DB()

for game in info:
    text = summarize(game)
    db.insert_new_game_report((game[0], game[1], game[5], f"{game[3]} {game[4]}", text))

db.close()
