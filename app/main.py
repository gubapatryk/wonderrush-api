from typing import Union

from fastapi import FastAPI
import asyncio

app = FastAPI()
app.running = True

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

class Room:
    def __init__(self, id):
        self.id = id
        self.player_number = 0
        self.player_dict = {}
        self.timer = 0
        print('zrob zegar')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.update())
    

    async def update(self):
        while app.running:
            self.timer += 1
            print('ummm')
            await asyncio.sleep(1)

    def check_if_player_exists_in_room(player_id : str, room):
        if player_id in room.player_dict:
            print('tak')
            return True
        print('nie')
        return False
            
    def add_player(self, player_id : str):
        if len(self.player_dict) < 3 and self.check_if_player_exists_in_room():
            self.player_dict[player_id] = Player()

@app.get("/update")
def read_root(room_id: str):
    return {"Hello": room_id}

@app.get("/join/{room_id}")
def join_room(room_id: str, player_id: str):
    if room_id in app.s.room_dict:
        print("juz jest")
        return False
    else:
        app.s.create_room(room_id)
        return True

@app.get("/time/{room_id}")
def room_time(room_id: str):
    if room_id in app.s.room_dict:
        return {"time" : app.s.room_dict[room_id].timer}
    else:
        return {"time" : -1}

@app.get("/")
def read_root():
    return {"Game": "Jam"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


app.s = Server()