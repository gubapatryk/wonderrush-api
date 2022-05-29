from typing import Union

from perlin_noise import PerlinNoise
from fastapi import FastAPI
import asyncio
import random

app = FastAPI()
MAP_SIZE_X = 9
MAP_SIZE_Y = 9
ITEMS_TYPES = 3
MAX_SPAWNED = 10

class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def run_main(self):
        while True:
            await asyncio.sleep(0.5)
            self.value += 1

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())
    for room_id in app.s.room_dict:
        app.s.room_dict[room_id].points.update_level()

class Server:
  def __init__(self):
    self.room_dict = {}

  def create_room(self,id):
    r = Room(id)
    self.room_dict[id] = r

  def get_room(self, id):
      return self.room_dict[id]

class Player:
  def __init__(self, id):
    self.id = id
    self.size = 0

class Item:
  def __init__(self, x, y, id):
    self.x = x
    self.y = y
    self.id = id

class Tile:
  def __init__(self, x, y, id):
    self.x = x
    self.y = y
    self.id = id



class Room:
    def __init__(self, id):
        self.id = id
        self.player_number = 0
        self.deltatime = runner.value
        self.tick = 0
        self.door_size = 10
        self.player_dict = {}
        self.winner = ""
        self.map_tiles = None
        self.items = []

    def create_map(self):
        noise = PerlinNoise(octaves=10)
        xpix, ypix = MAP_SIZE_X, MAP_SIZE_Y
        pic = [[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)]
        self.map_tiles = [[Tile(j,i,0) for i in range(xpix)] for j in range(ypix)]
        for j in range(ypix):
            for i in range(xpix):
                if pic[i][j] > 0.05:
                    self.map_tiles[i][j] = Tile(j,i,1)
                if pic[i][j] > 0.1:
                    self.map_tiles[i][j] = Tile(j,i,2)

    def check_if_tile_free(self, x, y):
        for it in self.items:
            if it.x == x and it.y == y:
                return False
        return True

    
    def eat_item(self, x, y):
        for it in self.items:
            if it.x == x and it.y == y:
                self.items.remove(it)
        return True

    def add_item(self):
        for x in range(10):
            x = random.randint(0, MAP_SIZE_X)
            y = random.randint(0, MAP_SIZE_Y)
            id = random.randint(1, ITEMS_TYPES)
            if self.check_if_tile_free(x,y):
                break
            if x == 9:
                return
        item = Item(x,y,id)
        self.items.append(item)

    def update_level(self):
        self.tick += 1
        self.add_item()

    def check_if_player_exists_in_room(self, player_id : str):
        if player_id in self.player_dict:
            return True
        return False
            
    def add_player(self, player_id : str):
        if len(self.player_dict) < 3 and self.check_if_player_exists_in_room(player_id):
            self.player_dict[player_id] = Player()
            self.player_number += 1

app.s = Server()

@app.get("/")
def root():
    return runner.value

@app.get("/join/{room_id}/{player_id}")
def join_room(room_id: str, player_id: str):
    if room_id in app.s.room_dict:
        if app.s.room_dict[room_id].player_number == 1:
            app.s.room_dict[room_id].add_player(player_id)
            return True
        return False
    else:
        app.s.create_room(room_id)
        app.s.room_dict[room_id].create_map()
        app.s.room_dict[room_id].add_player(player_id)
        return True

@app.get("/time/{room_id}")
def room_time(room_id: str):
    if room_id in app.s.room_dict:
        return {"time" : app.s.room_dict[room_id].deltatime}
    else:
        return {"time" : -1}
    
@app.get("/eat/{room_id}/{x}/{y}")
def eat_item(room_id: str, x: int, y: int):
    if room_id in app.s.room_dict:
        app.s.room_dict[room_id].eat_item(x,y)
        return True
    else:
        return False


@app.get("/update/{room_id}")
def update(room_id: str):
    if room_id in app.s.room_dict:
        app.s.room_dict[room_id].update_level()
    
        return {
            "winner" : app.s.room_dict[room_id].winner,
            "player_number" : app.s.room_dict[room_id].player_number,
            "items" : app.s.room_dict[room_id].items
        }
    else:
        return False

@app.get("/win/{room_id}/{player_id}")
def winner(room_id: str, player_id: str):
    app.s.room_dict[room_id].winner = player_id
    return True

@app.get("/reset/{room_id}")
def reset(room_id: str):
    app.s.room_dict.pop(room_id)
