from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# Manages active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# WebSocket endpoint
@app.websocket("/ws/game")
async def game_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Player says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A player has disconnected.")

players = ["Alice", "Bob", "Charlie"]
@app.get("/players")
def get_players():
    return {"players": players}

@app.get("/players/search")
def search_player(name: str):
    if name in players:
        return {"message": f"Player {name} found!"}
    return {"message": f"Player {name} not found!"}

from pydantic import BaseModel

class Player(BaseModel):
    name: str

@app.post("/players")
def add_player(player: Player):
    players.append(player.name)
    return {"message": f"Player {player.name} added!"}
