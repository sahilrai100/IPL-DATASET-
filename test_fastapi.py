from fastapi import FastAPI
import pandas as pd
import numpy as np

app = FastAPI()
df = pd.read_csv('matches.csv')
df = df.replace({np.nan: None})

@app.get("/")
def home():
    return {"message": "API Working!", "total_matches": len(df)}

@app.get("/matches")
def get_matches():
    return df.head(5).to_dict(orient='records')