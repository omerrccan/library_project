# Library App — Aşama 1 (CLI)

OOP ile yazılmış basit bir kütüphane uygulaması. Kitap **ekleme**, **silme**, **listeleme** ve **arama** yapar. Veriler `library.json` dosyasında **kalıcı** saklanır.

## Gereksinimler
- Python 3.11+
- (Testler için) `pytest`

## Kurulum
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
