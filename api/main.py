from fastapi import FastAPI
from services.graphService import parse_input
from pydantic import BaseModel
from typing import Any

app = FastAPI()


class Item(BaseModel):
    graph: Any
    notation: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/kg")
async def get_kg(item: Item):
    return parse_input(item.graph, item.notation)
    # return item
