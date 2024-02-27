from pydantic import BaseModel, Field


# define function structure in pydantic

class CardInfo(BaseModel):
    id_list: str = Field(..., description="Classification category", default_factory=None)
    name: str = Field(..., description="card name", default_factory=None)
    desc: str = Field(..., description="card description", default_factory=None)
    due: str = Field(..., description="Card due date", default_factory=None)
    start: str = Field(..., description="Card start date", default_factory=None)
    url_source: str = Field(..., description="Card url source", default_factory=None)
