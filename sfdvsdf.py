import httpx

resp = httpx.get("https://openlibrary.org/search.json?q=ulysses")
data = resp.json()

isbns = []
for doc in data.get("docs", []):
    if "isbn" in doc:
        isbns.extend(doc["isbn"])

print(isbns[:10])  # ilk 10 ISBN
