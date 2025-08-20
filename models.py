# models.py
from pydantic import BaseModel, Field, field_validator
import re

def normalize_isbn(raw: str) -> str:
    # Tire/boşlukları kaldır
    return re.sub(r"[\s-]", "", str(raw or ""))

class ISBNIn(BaseModel):
    """POST /books body modeli"""
    isbn: str = Field(..., example="978-0321765723", description="10 veya 13 haneli ISBN (tire/boşluk kabul edilir)")

    @field_validator("isbn")
    @classmethod
    def _validate_isbn(cls, v: str) -> str:
        s = normalize_isbn(v)
        if not (len(s) in (10, 13) and s.isdigit()):
            raise ValueError("Geçersiz ISBN biçimi. 10 veya 13 haneli rakam olmalı.")
        return s  # model üstünde normalize edilmiş hali tutacağız

class BookOut(BaseModel):
    """Response modeli"""
    title: str
    author: str
    isbn: str

    # Pydantic v2: dataclass/attr objelerinden alan çekmek için
    model_config = dict(from_attributes=True)
