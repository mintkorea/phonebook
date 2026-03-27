import csv, json

def make_aliases(name):
    return list(set([
        name,
        name.replace("��",""),
        name.lower()
    ]))

data = []

with open("data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        data.append({
            "id": i+1,
            "name": row["name"],
            "aliases": make_aliases(row["name"]),
            "campus": row["campus"],
            "building": row["building"],
            "floor": int(row["floor"]),
            "room": row["room"] or None,
            "category": row["category"]
        })

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data.json �앹꽦 �꾨즺")