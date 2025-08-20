# tests/test_api.py
import os
import importlib
from fastapi.testclient import TestClient

# Basit bir sahte httpx response sınıfı:
def make_fake_response(status_code=200, json_data=None):
    class FakeResp:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data or {}
        def json(self):
            return self._data
        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise Exception(f"HTTP {self.status_code}")
    return FakeResp(status_code, json_data)

def test_list_books_initially_empty(tmp_path, monkeypatch):
    lib_file = tmp_path / "library.json"
    os.environ["LIBRARY_FILE"] = str(lib_file)

    import api
    importlib.reload(api)
    client = TestClient(api.app)

    r = client.get("/books")
    assert r.status_code == 200
    assert r.json() == []

def test_add_book_success(tmp_path, monkeypatch):
    lib_file = tmp_path / "library.json"
    os.environ["LIBRARY_FILE"] = str(lib_file)

    import api
    importlib.reload(api)
    client = TestClient(api.app)

    # Open Library'yi taklit eden http_get
    def fake_http_get(url, timeout=10):
        if "/isbn/" in url:
            return make_fake_response(200, {
                "title": "Test Driven Development",
                "authors": [{"key": "/authors/OL1394243A"}]
            })
        if "/authors/OL1394243A.json" in url:
            return make_fake_response(200, {"name": "Kent Beck"})
        return make_fake_response(404, {})

    # api.lib'i, sahte http_get kullanan yeni bir Library ile değiştir
    from stage3 import Library
    api.lib = Library(str(lib_file), http_get=fake_http_get)

    r = client.post("/books", json={"isbn": "978-0321146533"})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test Driven Development"
    assert data["author"] == "Kent Beck"
    assert data["isbn"] == "9780321146533"  # normalize edilmiş

    # gerçekten kaydedildi mi?
    r2 = client.get("/books")
    assert r2.status_code == 200
    assert len(r2.json()) == 1

def test_add_book_invalid_isbn(tmp_path):
    lib_file = tmp_path / "library.json"
    os.environ["LIBRARY_FILE"] = str(lib_file)

    import api
    importlib.reload(api)
    client = TestClient(api.app)

    r = client.post("/books", json={"isbn": "abc"})
    # Pydantic validator tetiklenir -> FastAPI varsayılanı 422
    assert r.status_code == 422
    body = r.json()
    assert isinstance(body.get("detail"), list)
    # Hata mesajı içinde bizim validator mesajımız geçmeli
    assert any("Geçersiz ISBN" in (e.get("msg") or "") for e in body["detail"])

def test_add_book_not_found_on_openlibrary(tmp_path):
    lib_file = tmp_path / "library.json"
    os.environ["LIBRARY_FILE"] = str(lib_file)

    import api
    importlib.reload(api)
    client = TestClient(api.app)

    # Open Library her zaman 404 dönsün
    def fake_http_get(url, timeout=10):
        return make_fake_response(404, {})

    from stage3 import Library
    api.lib = Library(str(lib_file), http_get=fake_http_get)

    r = client.post("/books", json={"isbn": "9780321765723"})
    assert r.status_code == 404
    assert "bulunamadı" in r.json()["detail"].lower()

def test_delete_book_success(tmp_path):
    lib_file = tmp_path / "library.json"
    os.environ["LIBRARY_FILE"] = str(lib_file)

    import api
    importlib.reload(api)
    client = TestClient(api.app)

    # Ekleme için Open Library çağrısını başarıya çevir
    def fake_http_get(url, timeout=10):
        if "/isbn/" in url:
            return make_fake_response(200, {"title": "Clean Code", "authors": []})
        return make_fake_response(404, {})

    from stage3 import Library
    api.lib = Library(str(lib_file), http_get=fake_http_get)

    # önce ekle
    r_add = client.post("/books", json={"isbn": "978-0132350884"})
    assert r_add.status_code == 201

    # sonra sil
    r_del = client.delete("/books/978-0132350884")
    assert r_del.status_code == 200
    assert r_del.json()["deleted"] is True

    # liste tekrar boş olmalı
    r_list = client.get("/books")
    assert r_list.status_code == 200
    assert r_list.json() == []
