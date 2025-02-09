from pydantic import BaseModel


class Stock(BaseModel):
    name: str
    rating: float
    reason: str


class Sector(BaseModel):
    name: str
    rating: float
    reason: str


class StockAnalysis(BaseModel):
    rating: float
    stock: list[Stock]
    sectors: list[Sector]