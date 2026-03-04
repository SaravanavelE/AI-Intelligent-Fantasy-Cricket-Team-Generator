#  CricTech AI-Intelligent-Fantasy-Cricket-Team-Generator
CricTech AI is an intelligent fantasy cricket team generation system
developed for the CricTech Gameathon.\
The system combines historical IPL statistics, current season
performance, weather insights, and AI reasoning using Google's Gemini
API to generate optimized fantasy cricket teams.

The goal of this project is to demonstrate how AI‑assisted analytics can
improve fantasy sports decision‑making.

## Demo video:
https://github.com/user-attachments/assets/f579d24d-0be0-4cc3-9b4b-d608a49334ce

------------------------------------------------------------------------

## Features

-   AI‑powered fantasy team reasoning using Google Gemini
-   Player performance analysis using historical IPL statistics
-   Weather‑aware team selection logic
-   Automatic API key switching to handle rate limits
-   Modular Python architecture for easy extension
-   Docker container support for reproducible deployment

------------------------------------------------------------------------

## Tech Stack

-   Python
-   Pandas
-   Google Gemini API
-   REST APIs
-   Docker
-   CSV based analytics datasets

------------------------------------------------------------------------

## Project Architecture

User Input\
→ Match & Player Data Loader\
→ Data Processing (Pandas)\
→ Weather & Condition Logic\
→ Gemini AI Reasoning Engine\
→ Fantasy Team Recommendation

------------------------------------------------------------------------

## Project Structure

crictech_gameathon_codes/

-   app.py -- main application logic\
-   requirements.txt -- project dependencies\
-   Dockerfile -- container configuration\
-   .env -- environment variables for API keys

Datasets: - CricTech_IPL_General_Info.csv\
- CricTech_Player_Old_Stats.csv\
- CricTech_Bats_2025Stats.csv\
- CricTech_Bowlers_2025Stats.csv

------------------------------------------------------------------------

## Installation

Clone the repository

git clone https://github.com/SaravanavelE/AI-Intelligent-Fantasy-Cricket-Team-Generator.git cd crictech-ai

Install dependencies

pip install -r requirements.txt

Configure environment variables

Create a `.env` file and add:

GEMINI_API_KEY=your_key

Run the application

python app.py

------------------------------------------------------------------------

## Docker Deployment

Build the container

docker build -t crictech-ai .

Run the container

docker run crictech-ai

------------------------------------------------------------------------

## How It Works

1.  Player statistics are loaded from structured CSV datasets.
2.  Weather conditions influence the fantasy team strategy.
3.  Historical player performance is analyzed.
4.  Gemini AI evaluates the context and suggests the best team
    combination.
5.  The system outputs an optimized fantasy cricket team.

------------------------------------------------------------------------

## Future Improvements

-   BERT based player classification
-   Real‑time match data integration
-   Dream11 scoring prediction
-   Web dashboard using Streamlit
-   ML based team optimization
