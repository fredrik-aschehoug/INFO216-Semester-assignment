from fastapi import FastAPI, Depends
from models.models import Item
from services.graphService import GraphService
from services.YagoService import YagoService
# from fastapi_cprofile.profiler import CProfileMiddleware

app = FastAPI()
# app.add_middleware(CProfileMiddleware, enable=True, print_each_request=True, strip_dirs=True, sort_by='cumulative')


@app.get("/", response_model=Item)
async def get_extended_graph(graph: GraphService = Depends(GraphService)):
    await graph.extend()
    graph.annotate_relations()

    return {"graph": str(graph), "notation": graph.notation}
