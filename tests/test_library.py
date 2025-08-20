# tests/test_library_stage2.py
import httpx
from stage2 import Library, Book

class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if 400 <= self.status_code:
            raise httpx.HTTPStatusError("err", request=None, response=None)

def make_fake_http_get_ok():
    """İyi senaryo: ISBN -> kitap json, authors -> isimler"""
    def _fake_get(url, timeout=10):
        if "isbn/9780199535675.json" in url or "isbn/978-0199535675.json" in url:
            return FakeResponse(200, {
                "title": "Ulysses",
                "authors": [{"key": "/authors/OL26320A"}]
            })
        if "/authors/OL26320A.json" in url:
            return FakeResponse(200, {"name": "James Joyce"})
        return FakeResponse(404, {})
    return _fake_get

def make_fake_http_get_404():
    def _fake_get(url, timeout=10):
        return FakeResponse(404, {})
    return _fake_get

def make_fake_http_get_network_error():
    def _fake_get(url, timeout=10):
        raise httpx.RequestError("network fail")
    return _fake_get

def test_add_book_by_isbn_success(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path), http_get=make_fake_http_get_ok())

    ok = lib.add_book_by_isbn("978-0199535675")
    assert ok is True
    # kalıcı yazıldı mı?
    lib2 = Library(str(file_path))
    b = lib2.find_book("978-0199535675")
    assert b is not None
    assert b.title == "Ulysses"
    assert "James Joyce" in b.author

def test_add_book_by_isbn_not_found(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path), http_get=make_fake_http_get_404())

    ok = lib.add_book_by_isbn("0000000000")
    assert ok is False
    assert lib.list_books() == []

def test_add_book_by_isbn_network_error(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path), http_get=make_fake_http_get_network_error())

    ok = lib.add_book_by_isbn("978-0199535675")
    assert ok is False
    assert lib.list_books() == []

def test_add_book_by_isbn_duplicate(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path), http_get=make_fake_http_get_ok())

    assert lib.add_book_by_isbn("978-0199535675") is True
    # ikinci kez aynı ISBN
    assert lib.add_book_by_isbn("978-0199535675") is False
