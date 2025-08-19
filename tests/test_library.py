# tests/test_library.py
import json
from stage1 import Book, Library

def test_add_and_persist(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path))

    b = Book("Ulysses", "James Joyce", "978-0199535675")
    ok = lib.add_book(b)
    assert ok is True

    # JSON gerçekten yazıldı mı?
    assert file_path.exists()
    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["title"] == "Ulysses"

    # Uygulama yeniden açılmış gibi yeni Library yarat ve yükleniyor mu?
    lib2 = Library(str(file_path))
    assert len(lib2.list_books()) == 1
    loaded = lib2.find_book("978-0199535675")
    assert loaded is not None
    assert loaded.title == "Ulysses"

def test_remove_book(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path))

    lib.add_book(Book("Book A", "Auth A", "111"))
    lib.add_book(Book("Book B", "Auth B", "222"))
    assert len(lib.list_books()) == 2

    ok = lib.remove_book("111")
    assert ok is True
    assert lib.find_book("111") is None
    assert len(lib.list_books()) == 1

def test_duplicate_isbn_blocked(tmp_path):
    file_path = tmp_path / "library.json"
    lib = Library(str(file_path))

    assert lib.add_book(Book("X", "Y", "999")) is True
    # aynı ISBN tekrar eklenmesin
    assert lib.add_book(Book("X2", "Y2", "999")) is False
    assert len(lib.list_books()) == 1
