import sys
import os
import time
import pandas as pd
import requests
import datetime
import csv
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Load multiple Gemini API keys
api_keys = [
    os.getenv("GEMINI_API_KEY4"),
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY1"),
    os.getenv("GEMINI_API_KEY2"),
    os.getenv("GEMINI_API_KEY3")
]
api_keys = [key for key in api_keys if key]

# Configure initial Gemini model
current_key_index = 0
genai.configure(api_key=api_keys[current_key_index])
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

def switch_api_key():
    global current_key_index, model
    current_key_index += 1
    if current_key_index >= len(api_keys):
        sys.exit(1)
    genai.configure(api_key=api_keys[current_key_index])
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Load CSV files
df = pd.read_csv("CricTech_IPL_General_Info.csv")
players_old = pd.read_csv("CricTech_Player_Old_Stats.csv")
bats_stats = pd.read_csv("CricTech_Bats_2025Stats.csv")
bowlers_stats = pd.read_csv("CricTech_Bowlers_2025Stats.csv")

# Configuration settings
weather_team_config = {
    "sunny": [5, 2, 2, 2], "cloudy": [3, 3, 3, 2], "clear sky": [4, 3, 2, 2],
    "rainy": [4, 2, 3, 2], "windy": [3, 4, 2, 2], "foggy": [2, 4, 3, 2],
    "humid": [3, 3, 3, 2], "cold": [3, 4, 2, 2], "autumn": [3, 3, 3, 2],
    "overcast": [2, 4, 3, 2], "dewy": [4, 2, 3, 2], "unknown": [3, 4, 2, 2]
}
pitch_team_config = {
    "batting-friendly": [5, 2, 2, 2], "spin-friendly": [3, 3, 3, 2],
    "balanced": [4, 3, 2, 2], "bowler-friendly": [3, 4, 2, 2],
    "slow, spin-friendly": [3, 3, 3, 2], "seam-friendly": [2, 4, 3, 2],
    "new venue": [3, 3, 3, 2]
}

# Helper Functions
def classify_weather(description):
    description = description.lower()
    for key in weather_team_config:
        if key in description:
            return key, weather_team_config[key]
    return "unknown", weather_team_config["unknown"]

def classify_pitch(pitch_type):
    return pitch_team_config.get(pitch_type.lower(), [3, 4, 2, 2])

def merge_team_configs(weather_config, pitch_config):
    combined = [(w + p) // 2 for w, p in zip(weather_config, pitch_config)]
    diff = 11 - sum(combined)
    combined[0] += diff
    return combined

def get_forecast(lat, lon, match_datetime):
    API_KEY = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and "list" in data:
        forecast_data = data["list"]
        best_match = min(forecast_data, key=lambda x: abs(datetime.datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - match_datetime))
        description = best_match["weather"][0]["description"]
        _, weather_config = classify_weather(description)
        return weather_config
    return weather_team_config["unknown"]

def get_dream11_team(player_data, required, playing_today, players_old, bats_stats, bowlers_stats):
    prompt_main = f"""
            You are a professional fantasy cricket expert.
            Use previous matches performances in past year and IPL 2025 for New Players to assign the best team.
            Only select(must):

            - {required['BAT']} BAT
            - {required['BOWL']} BOWL
            - {required['ALL']} ALL
            - {required['WK']} WK
            Total should be exactly 11 players. Select also 4 substitutes as:
            - 1 BAT
            - 1 ALL
            - 1 BAT
            - 1 BOWL

            Total credit of main 11 should be <= 100.
            
            Strictly note the details below(must)
            choose
            1 Captain (C) from top player in  BAT,
            1 Vice Captain (VC) from top player in ALL,
            rest are Normal (NA) including substitutes.
            
            dont give any unwanted data in the output
            give C details first, then VC details Then NA details
            Only respond in the following table format:
            Player Name,Team,C/VC

            Here is the players who are in team data:
            {player_data}
            Here is the today's players line up data:
            (The selected players list is should be in this ddataset ["IsPlaying"] == "PLAYING")
            {playing_today}
            Here is the players old data:
            {players_old}
            Here is the batsman 2025 stats data:
            {bats_stats}
            Here is the bowler 205 stats
            {bowlers_stats}
            
    """

    while True:
        try:
            response = model.generate_content(prompt_main, generation_config={"temperature": 0.0})
            output = response.text.strip()
            lines = output.splitlines()
            rows = []

            for line in lines[1:]:
                if not line.strip() or line.lower().startswith("team,"):
                    continue
                parts = [x.strip() for x in line.split(",")]
                if len(parts) == 3:
                    rows.append([parts[0], parts[1], parts[2]])
            output_path = os.path.join(os.path.expanduser("~"), "Downloads", "CricTech_output.csv")
            if os.path.exists("/app/Downloads"):
                output_path = "/app/Downloads/CricTech_output.csv"
                
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Player Name", "Team", "C/VC"])
                writer.writerows(rows)

            print("Output saved successfully!")
            break
        except Exception as e:
            print(f"⚠ Error with current API key: {e}")
            switch_api_key()
            time.sleep(1)

def fantasy_selector():
    if len(sys.argv) <2:
        print("❌ Please provide match number as argument.")
        sys.exit(1)

    match_number = int(sys.argv[1])
    match = df[df["Match Number"] == match_number]
    if match.empty:
        print("❌ Invalid Match Number!")
        return

    venue = match.iloc[0]["Venue"]
    home_team = match.iloc[0]["Team1"]
    away_team = match.iloc[0]["Team2"]
    lat, lon = match.iloc[0]["Latitude"], match.iloc[0]["Longitude"]
    pitch_type = match.iloc[0]["Pitch Type"]
    match_date = match.iloc[0]["Date"]
    match_time = match.iloc[0]["Time"]
    match_datetime = datetime.datetime.strptime(f"{match_date} {match_time}", "%Y-%m-%d %H:%M")

    try:
        file_path = os.path.expanduser("~/Downloads/SquadPlayerNames_IndianT20League.xlsx")
        sheet_df = pd.read_excel(file_path, sheet_name=f"Match_{match_number}")
        sheet_df["Player Name"] = sheet_df["Player Name"].str.strip().str.lower()
        sheet_df["Team"] = sheet_df["Team"].str.strip().str.upper()
        playing_today = sheet_df[sheet_df["IsPlaying"] == "PLAYING"].copy()
    except Exception as e:
        print("❌ Error loading Excel sheet:", e)
        home_players = players_old[players_old["Team"] == home_team]
        away_players = players_old[players_old["Team"] == away_team]
        playing_today = pd.concat([home_players[["Player Name", "Team"]], away_players[["Player Name", "Team"]]])

    weather_config = get_forecast(lat, lon, match_datetime)
    pitch_config = classify_pitch(pitch_type)
    final_team_config = merge_team_configs(weather_config, pitch_config)

    required = {
        "BAT": final_team_config[0],
        "ALL": final_team_config[1],
        "BOWL": final_team_config[2],
        "WK": final_team_config[3],
    }

    player_data = ""
    for _, row in playing_today.iterrows():
        player_data += f"{row['Team']},{row['Player Name']},{row['Player Type']},\n"

    get_dream11_team(player_data, required, playing_today, players_old, bats_stats, bowlers_stats)

if __name__ == "__main__":
    fantasy_selector()