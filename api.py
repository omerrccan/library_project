# api.py
from fastapi import FastAPI, HTTPException, status
from typing import List
import threading
import os

from stage3 import Library, Book  # mevcut sınıfların
from models import ISBNIn, BookOut  # yeni Pydantic modelleri

app = FastAPI(
    title="Library API",
    description="Basit kütüphane API'si (ISBN ile ekleme, listeleme, silme)",
    version="1.0.0",
)

LIB_FILE = os.getenv("LIBRARY_FILE", "library.json")
lib = Library(LIB_FILE)
lock = threading.Lock()

@app.get("/", tags=["Health"])
def root():
    return {"message": "📚 Library API çalışıyor!"}

@app.get("/books", response_model=List[BookOut], tags=["Books"])
def list_books():
    # Pydantic, Book nesnelerini BookOut'a dönüştürür (from_attributes=True sayesinde)
    return lib.list_books()

@app.post(
    "/books",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Books"],
    responses={
        201: {"description": "Kitap başarıyla eklendi."},
        400: {"description": "Geçersiz ISBN veya zaten mevcut."},
        404: {"description": "ISBN bulunamadı (Open Library)."},
        424: {"description": "Harici servis hatası."},
    },
)
def add_book(isbn_in: ISBNIn):
    # Artık isbn_in.isbn normalize & validate edilmiş halde
    isbn = isbn_in.isbn

    if lib.find_book(isbn):
        raise HTTPException(status_code=400, detail="Bu ISBN zaten kayıtlı.")

    try:
        with lock:
            ok = lib.add_book_by_isbn(isbn)
    except Exception:
        raise HTTPException(status_code=424, detail="Harici servise erişimde beklenmeyen hata.")

    if not ok:
        # Open Library’de bulunamadı / veri eksikliği vs.
        raise HTTPException(status_code=404, detail="ISBN bulunamadı ya da veriler çekilemedi.")

    return lib.find_book(isbn)

@app.delete(
    "/books/{isbn}",
    tags=["Books"],
    responses={
        200: {"description": "Silme başarılı."},
        404: {"description": "Belirtilen ISBN bulunamadı."},
    },
)
def delete_book(isbn: str):
    # Silmede path paramı—normalize/validate istersen models.py’dan fonksiyonu içe alıp kullanabilirsin
    from models import normalize_isbn
    normalized = normalize_isbn(isbn)
    with lock:
        ok = lib.remove_book(normalized)
    if not ok:
        raise HTTPException(status_code=404, detail="Bu ISBN bulunamadı.")
    return {"deleted": True, "isbn": normalized}
