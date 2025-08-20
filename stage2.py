# stage2.py (güncel)
import json
from typing import List, Optional, Callable
import httpx  # <-- Aşama 2: httpx eklendi

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

class Library:
    def __init__(self, file_name="library.json", http_get: Optional[Callable]=None):
        self.books: List[Book] = []
        self.file_name = file_name
        self._http_get = http_get or httpx.get  # <-- DI: testlerde sahte istek enjekte edebilmek için
        self.load_books()

    def load_books(self):
        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = []
                for d in data:
                    isbn = d.get("isbn") or d.get("ISBN")
                    self.books.append(Book(d["title"], d["author"], str(isbn)))
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            self.books = []

    def save_books(self):
        data = [{"title": b.title, "author": b.author, "isbn": b.isbn} for b in self.books]
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_book(self, book: Book) -> bool:
        if any(b.isbn == book.isbn for b in self.books):
            return False
        self.books.append(book)
        self.save_books()
        return True

    def remove_book(self, isbn: str) -> bool:
        before = len(self.books)
        self.books = [b for b in self.books if b.isbn != isbn]
        removed = len(self.books) < before
        if removed:
            self.save_books()
        return removed

    def list_books(self) -> List[Book]:
        return self.books

    def find_book(self, isbn: str) -> Optional[Book]:
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    # === AŞAMA 2: ISBN'den otomatik ekleme ===
    def add_book_by_isbn(self, isbn: str) -> bool:
        """Open Library'den (isbn.json) title/authors çekip Book ekler. Başarılıysa True."""
        # Önce zaten var mı?
        if self.find_book(isbn):
            return False

        try:
            # 1) Kitap temel bilgisi
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            resp = self._http_get(url, timeout=10)
            if resp.status_code == 404:
                return False
            resp.raise_for_status()
            data = resp.json()

            title = data.get("title")
            authors_keys = [a.get("key") for a in data.get("authors", []) if a.get("key")]

            # 2) Yazar isimleri (varsa tek tek çek)
            names = []
            for key in authors_keys:
                try:
                    a_resp = self._http_get(f"https://openlibrary.org{key}.json", timeout=10)
                    if a_resp.status_code == 200:
                        a_data = a_resp.json()
                        name = a_data.get("name")
                        if name:
                            names.append(name)
                except Exception:
                    # Yazar adını çekemesek de kitabı ekleyebiliriz
                    continue

            author = ", ".join(names) if names else "Unknown"
            if not title:
                # Bazı eksik cevaplarda title olmayabilir
                return False

            return self.add_book(Book(title=title, author=author, isbn=isbn))

        except httpx.HTTPStatusError:
            return False
        except httpx.RequestError:
            # ağ/timeout/dns vs
            return False

def print_menu():
    print("\n=== Kütüphane Menüsü ===")
    print("1. Kitap Ekle (ISBN ile otomatik)")
    print("2. Kitap Sil")
    print("3. Kitapları Listele")
    print("4. Kitap Ara")
    print("5. Çıkış")

def main():
    lib = Library("library.json")
    while True:
        print_menu()
        choice = input("Seçiminiz (1-5): ").strip()

        if choice == "1":
            isbn = input("ISBN: ").strip()
            if not isbn:
                print("⚠ ISBN boş olamaz.")
                continue
            ok = lib.add_book_by_isbn(isbn)
            if ok:
                print("✅ Kitap eklendi (Open Library).")
            else:
                print("⚠ Eklenemedi (yanlış ISBN, ağ hatası ya da zaten kayıtlı olabilir).")

        elif choice == "2":
            isbn = input("Silinecek kitabın ISBN'i: ").strip()
            ok = lib.remove_book(isbn)
            print("🗑️ Silindi." if ok else "⚠ Bu ISBN bulunamadı.")

        elif choice == "3":
            books = lib.list_books()
            if not books:
                print("📭 Kütüphane boş.")
            else:
                print("\n— Kayıtlı Kitaplar —")
                for i, b in enumerate(books, 1):
                    print(f"{i}. {b}")

        elif choice == "4":
            isbn = input("Aranacak ISBN: ").strip()
            b = lib.find_book(isbn)
            print(b if b else "⚠ Kitap bulunamadı.")

        elif choice == "5":
            print("👋 Görüşürüz!")
            break
        else:
            print("⚠ Geçersiz seçim, 1-5 arası deneyin.")

if __name__ == "__main__":
    main()
