from fastapi import FastAPI
from services.graphService import get_extended_graph
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
    return get_extended_graph(item.graph, item.notation)
    # return item
