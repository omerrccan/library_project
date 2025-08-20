# Library App — Aşama 2 (Open Library Entegrasyonu)

Aşama 1’deki CLI uygulamasına **harici API** (Open Library) entegrasyonu eklendi. Kullanıcı yalnızca **ISBN** girer; uygulama başlık ve yazar(ları) otomatik çeker ve `library.json`’a **kalıcı** kaydeder.

## Özellikler
- `httpx` ile **Open Library Books API** (`https://openlibrary.org/isbn/{isbn}.json`)
- Yazar adlarını `authors[].key` üzerinden **ek isteklerle** toplar
- **DI (Dependency Injection):** `Library(http_get=...)` ile testlerde sahte istek enjekte edilebilir
- Ağ/404 hatalarında güvenli davranış; aynı ISBN ikinci kez eklenmez

## Proje Yapısı


## Gereksinimler
- Python 3.11+
- Bağımlılıklar: `httpx`, `pytest`

**requirements.txt (önerilen)**


## Kurulum
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt


##Kullanımı
python stage2.py


##Test Çalıştırma
pytest -q