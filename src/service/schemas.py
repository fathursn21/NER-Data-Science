from pydantic import BaseModel, StrictStr
from typing import List

class ArticleRequest(BaseModel):
    title: StrictStr
    body: StrictStr

class EntityItem(BaseModel):
    text: str
    label: str
    start: int
    end: int

class MetaInfo(BaseModel):
    entity_count: int
    model: str

class ExtractionResponse(BaseModel):
    entities: List[EntityItem]
    meta: MetaInfo
