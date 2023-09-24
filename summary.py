import openai
import os
from dotenv import load_dotenv
import csv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

file_name = "full_data.csv"

out = "data_with_summary.csv"

encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1']

def createPrompt(home, away, comment):

    res = ""

    res += "Based on the provided commentary of a soccer game, can you create a paragraph or two to summarize what happened?\n"

    res += f"It is a \"Liga Portugal\" game, {home} (Home) vs. {away} (Away).\n"

    res += "Conclude your text with the full-time result.\n"

    res += "Commentary:\n"

    res += str(comment)
    return res

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
            commentaryFormated = commentary[1:len(commentary) - 1].replace(", ", ",").replace("\"", "").split(',')
            data = commentaryFormated if commentary != "" else []
            info.append([home, away, data, date, hour])

        break  # Exit the loop if successful
    except UnicodeDecodeError:
        continue  # Try the next encoding if decoding fails

for game in info[0:1]:
    prompt = createPrompt(game[0], game[1], game[2])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}]
    )

    english_text = response.choices[0].message.content

    #Translation Here
    portuguese_text = english_text

    with open(f'{game[0]}-{game[1]}-{game[3].replace(".", "-")}-{game[4].replace(":", "-")}.txt', 'w') as file:
        file.write(portuguese_text)



