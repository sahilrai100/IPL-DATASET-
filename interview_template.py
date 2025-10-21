from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
from typing import Optional
import pandas as pd
from openai import OpenAI
from playwright.sync_api import sync_playwright
# from fastapi import HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

# Load CSV
df = pd.read_csv('matches.csv')

class Match(BaseModel):
    season: int
    city: str
    date: str
    team1: str
    team2: str
    toss_winner: str
    toss_decision: str
    result: str
    dl_applied: int
    winner: str
    win_by_runs: int
    win_by_wickets: int
    player_of_match: str
    venue: str
    umpire1: str
    umpire2: str

# POST - Add new match
@app.post("/add-match")
def add_match(match: Match):
    global df
    
    new_row = {
        'season': match.season,
        'city': match.city,
        'date': match.date,
        'team1': match.team1,
        'team2': match.team2,
        'toss_winner': match.toss_winner,
        'toss_decision': match.toss_decision,
        'result': match.result,
        'dl_applied': match.dl_applied,
        'winner': match.winner,
        'win_by_runs': match.win_by_runs,
        'win_by_wickets': match.win_by_wickets,
        'player_of_match': match.player_of_match,
        'venue': match.venue,
        'umpire1': match.umpire1,
        'umpire2': match.umpire2
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return {"message": "Match added!", "data": new_row}

# PUT - Update match
@app.put("/update-match/{index}")
def update_match(index: int, match: Match):
    global df
    
    if index >= len(df):
        return {"error": "Match not found"}
    
    df.at[index, 'season'] = match.season
    df.at[index, 'city'] = match.city
    df.at[index, 'date'] = match.date
    df.at[index, 'team1'] = match.team1
    df.at[index, 'team2'] = match.team2
    df.at[index, 'toss_winner'] = match.toss_winner
    df.at[index, 'toss_decision'] = match.toss_decision
    df.at[index, 'result'] = match.result
    df.at[index, 'dl_applied'] = match.dl_applied
    df.at[index, 'winner'] = match.winner
    df.at[index, 'win_by_runs'] = match.win_by_runs
    df.at[index, 'win_by_wickets'] = match.win_by_wickets
    df.at[index, 'player_of_match'] = match.player_of_match
    df.at[index, 'venue'] = match.venue
    df.at[index, 'umpire1'] = match.umpire1
    df.at[index, 'umpire2'] = match.umpire2
    
    return {"message": "Match updated!", "index": index}

# DELETE - Delete match
@app.delete("/delete-match/{index}")
def delete_match(index: int):
    global df
    
    if index >= len(df):
        return {"error": "Match not found"}
    
    df = df.drop(index).reset_index(drop=True)
    
    return {"message": "Match deleted!", "index": index}

# Setup Cerebras
llm_client = OpenAI(
    api_key="csk_h3cxfxjnyrjfkhx3e9h9chj9pkch23345n9444xn9dv5dpkf",
    base_url="https://api.cerebras.ai/v1"
)

# Helper function to clean data
def clean_data(data):
    """Convert DataFrame to JSON-safe format"""
    return json.loads(df.fillna("").to_json(orient='records'))

# ========== PANDAS ENDPOINTS ==========

@app.get("/")
def home():
    return {"message": "IPL Interview API", "total_matches": len(df)}

@app.get("/all")
def get_all():
    result = df.head(20).fillna("").to_dict(orient='records')
    return result

@app.get("/team/{team_name}")
def get_team_data(team_name: str):
    matches = df[(df['team1'] == team_name) | (df['team2'] == team_name)]
    wins = len(df[df['winner'] == team_name])
    return {
        "team": team_name,
        "total_matches": len(matches),
        "wins": wins,
        "data": matches.head(10).fillna("").to_dict(orient='records')
    }

@app.get("/winners")
def get_winners(limit: int = 5):
    winners = df['winner'].value_counts().head(limit)
    return winners.to_dict()

@app.get("/filter")
def filter_matches(
    team: Optional[str] = None,
    season: Optional[int] = None,
    city: Optional[str] = None
):
    result = df.copy()
    if team:
        result = result[(result['team1'] == team) | (result['team2'] == team)]
    if season:
        result = result[result['season'] == season]
    if city:
        result = result[result['city'] == city]
    return result.head(10).fillna("").to_dict(orient='records')

# ========== LLM ENDPOINTS ==========

@app.get("/ask")
def ask_llm(question: str):
    response = llm_client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": question}]
    )
    return {"question": question, "answer": response.choices[0].message.content}

@app.get("/analyze/{team_name}")
def analyze_team(team_name: str):
    matches = df[(df['team1'] == team_name) | (df['team2'] == team_name)]
    wins = len(df[df['winner'] == team_name])
    
    prompt = f"""Analyze IPL team {team_name}:
    Total matches: {len(matches)}
    Total wins: {wins}
    Win rate: {wins/len(matches)*100:.1f}%
    
    Give brief 2-line analysis."""
    
    response = llm_client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "team": team_name,
        "stats": {"matches": len(matches), "wins": wins},
        "analysis": response.choices[0].message.content
    }

# ========== PLAYWRIGHT ENDPOINT ==========

@app.get("/scrape")
def scrape_website(url: str = "https://example.com"):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)  # 10 second timeout
            
            title = page.title()
            
            # Try to get h1, but don't fail if it doesn't exist
            try:
                heading = page.locator('h1').first.inner_text(timeout=5000)
            except:
                heading = "No heading found"
            
            browser.close()
            
            return {"url": url, "title": title, "heading": heading}
    except Exception as e:
        return {"url": url, "error": str(e), "message": "Failed to scrape website"}