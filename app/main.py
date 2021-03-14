from fastapi import FastAPI, Depends
from models.models import Item
from services.EnrichmentService import EnrichmentService
# from fastapi_cprofile.profiler import CProfileMiddleware

app = FastAPI()
# app.add_middleware(CProfileMiddleware, enable=True, print_each_request=True, strip_dirs=True, sort_by='cumulative')


@app.get("/", response_model=Item)
async def get_extended_graph(encricher: EnrichmentService = Depends(EnrichmentService)):
    await encricher.extend()
    encricher.annotate_relations()

    return encricher.get_response()
