from pydantic import BaseModel, validator
from typing import Optional


ACCEPTED_NOTATIONS = ["json-ld", "turtle", "html", "hturtle", "mdata", "microdata", "n3", "nquads", "nt", "rdfa", "rdfa1.0", "rdfa1.1", "trix", "xml"]


class RequestModel(BaseModel):
    graph: str
    in_notation: str
    out_notation: Optional[str] = None

    @validator("in_notation", "out_notation")
    def notation_must_be_supported(cls, v):
        if v not in ACCEPTED_NOTATIONS:
            raise ValueError("in_notation '{}' not supported.".format(v))
        return v


class ResponseModel(BaseModel):
    graph: str
    notation: str
