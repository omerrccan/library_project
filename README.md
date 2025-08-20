# Library App — Aşama 3 (FastAPI REST API)

Bu proje, üç aşamalı bir kütüphane uygulamasıdır.  
Aşama 1’de temel CLI, Aşama 2’de Open Library entegrasyonu, Aşama 3’te ise **FastAPI ile REST API** sunumu yapılmıştır.

---

## Aşama 1: CLI Uygulaması
- Basit bir **komut satırı arayüzü** üzerinden kitap ekleme/silme.
- Kitap bilgileri `library.json` içinde kalıcı saklanır.

**Dosya:** `stage1.py`

---

## Aşama 2: Open Library Entegrasyonu
Aşama 1’e ek olarak **harici API** entegrasyonu eklendi.  
Kullanıcı yalnızca **ISBN** girer; uygulama başlık ve yazar(ları) otomatik çeker.

### Özellikler
- `httpx` ile **Open Library Books API** (`https://openlibrary.org/isbn/{isbn}.json`)
- Yazar adlarını `authors[].key` üzerinden **ek isteklerle** toplar
- **DI (Dependency Injection):** `Library(http_get=...)` ile testlerde sahte istek enjekte edilebilir
- Ağ/404 hatalarında güvenli davranış; aynı ISBN ikinci kez eklenmez

**Dosyalar:**  
- `stage2.py` → Open Library API entegrasyonu  
- `sys_path.py` → PYTHONPATH/test/debug için yardımcı dosya  

---

## Aşama 3: FastAPI REST API
Aşama 1–2’deki kütüphane mantığı **REST API** olarak sunuldu.  
Artık uygulamaya tarayıcı veya API istemcileri (cURL, Postman) ile erişilebiliyor.

### Özellikler
- `GET /books` → Tüm kitapları döndürür  
- `POST /books` → ISBN ile Open Library’den çekip ekler  
- `DELETE /books/{isbn}` → ISBN’e göre siler  
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **JSON response** standartlarına uygun çıktı

### Proje Yapısı
- stage1.py → CLI uygulaması
- stage2.py → Open Library entegrasyonu
- stage3.py / api.py → FastAPI REST API
- library.json → Kitap veritabanı
- tests/ → pytest testleri

---

## Kurulum
```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
