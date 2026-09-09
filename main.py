from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Aapki 'games.py' file se saara data import ho raha hai
from games import GAMES_DATABASE

app = FastAPI(title="Games Directory API")

# CORS Middleware (Lovable frontend se connect karne ke liye zaroori hai)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model (Data Validation)
class Game(BaseModel):
    id: int
    title: str
    platform: str
    release_year: int
    genre: str
    rating: float
    description: str
    image_url: str
    is_wishlisted: bool

# --- API Endpoints ---

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Games API! Go to /docs for full API documentation."}

# 1. Tamam 200 Games get karne ke liye
@app.get("/api/games", response_model=List[Game], tags=["Games"])
def get_all_games():
    return GAMES_DATABASE

# 2. Kisi ek Game ki detail ID se nikalne ke liye (String/Integer dono ko handle karega)
@app.get("/api/games/{game_id}", response_model=Game, tags=["Games"])
def get_game(game_id: int):
    for game in GAMES_DATABASE:
        # Dono taraf integer check taake ID 25 ya koi bhi ID lazmi match ho jaye
        if int(game["id"]) == int(game_id):
            return game
    raise HTTPException(status_code=404, detail="Game not found")

# 3. Wishlist ko toggle (Add/Remove) karne ke liye
@app.post("/api/games/{game_id}/wishlist", tags=["Games"])
def toggle_wishlist(game_id: int):
    for game in GAMES_DATABASE:
        if int(game["id"]) == int(game_id):
            game["is_wishlisted"] = not game["is_wishlisted"]
            return {
                "success": True, 
                "is_wishlisted": game["is_wishlisted"], 
                "message": f"Wishlist status updated for {game['title']}"
            }
    raise HTTPException(status_code=404, detail="Game not found")
