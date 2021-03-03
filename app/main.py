from fastapi import FastAPI, Depends
from models.models import Item
from services.graphService import GraphService
from services.YagoService import YagoService


app = FastAPI()


@app.get("/", response_model=Item)
async def get_extended_graph(graph: GraphService = Depends(GraphService)):

    graph.extend()
    graph.annotate_relations()

    return {"graph": str(graph), "notation": graph.notation}
