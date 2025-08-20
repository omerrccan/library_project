import json
from typing import List, Optional

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn  # <- tek tip: her yerde küçük harf

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"


class Library:
    def __init__(self, file_name="library.json"):
        self.books = []
        self.file_name = file_name
        self.load_books()

    def load_books(self):
        """JSON'dan kitapları yükle; ISBN/isbN anahtarlarını normalize et."""
        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = []
                for d in data:
                    # Eski kayıtlarda 'ISBN' olabilir; hepsini 'isbn' olarak topla
                    isbn = d.get("isbn") or d.get("ISBN")
                    self.books.append(Book(d["title"], d["author"], str(isbn)))
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            # Bozuk dosya durumunda sıfırla (istersen burada loglayabilirsin)
            self.books = []

    def save_books(self):
        """Kitap listesini JSON'a kaydet (anahtarlar küçük harfli)."""
        data = [{"title": b.title, "author": b.author, "isbn": b.isbn} for b in self.books]
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_book(self, book: Book) -> bool:
        """Yeni kitap ekler; ISBN zaten varsa eklemez."""
        if any(b.isbn == book.isbn for b in self.books):
            return False
        self.books.append(book)
        self.save_books()
        return True

    def remove_book(self, isbn: str) -> bool:
        """ISBN'e göre kitabı siler. Bulursa True, bulamazsa False."""
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


def print_menu():
    print("\n=== Kütüphane Menüsü ===")
    print("1. Kitap Ekle")
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
            title = input("Kitap başlığı: ").strip()
            author = input("Yazar: ").strip()
            isbn = input("ISBN: ").strip()
            if not title or not author or not isbn:
                print("⚠ Alanlar boş olamaz.")
                continue
            ok = lib.add_book(Book(title, author, isbn))
            print("✅ Kitap eklendi." if ok else "⚠ Bu ISBN zaten kayıtlı.")

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
