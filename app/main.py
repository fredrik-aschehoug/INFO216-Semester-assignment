from fastapi import FastAPI, Depends
from models.models import ResponseModel
from services.EnrichmentService import EnrichmentService

app = FastAPI()

# Uncomment this to enable profiling
# from fastapi_cprofile.profiler import CProfileMiddleware
# app.add_middleware(CProfileMiddleware, enable=True, print_each_request=True, strip_dirs=True, sort_by='cumtime')


@app.get("/", response_model=ResponseModel)
async def get_extended_graph(encricher: EnrichmentService = Depends(EnrichmentService)):
    await encricher.extend()

    encricher.annotate_relations()

    return encricher.get_response()
