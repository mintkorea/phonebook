from fastapi import FastAPI
import json

app = FastAPI()

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

@app.get("/search")
def search(q: str = "", category: str = "ALL"):
    q = q.lower()
    results = []

    for item in data:
        score = 0

        if q in item["name"].lower():
            score += 3
        if any(q in a.lower() for a in item["aliases"]):
            score += 2
        if q in item["building"].lower():
            score += 1

        if category != "ALL" and item["category"] != category:
            continue

        if score > 0:
            item["score"] = score
            results.append(item)

    return sorted(results, key=lambda x: x["score"], reverse=True)