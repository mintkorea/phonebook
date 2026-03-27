import json
import csv

# ---------- 데이터 생성 ----------

def make_aliases(name):
    return list(set([
        name,
        name.replace("실",""),
        name.lower()
    ]))

def load_data():
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

    return data


# ---------- 검색 로직 ----------

def search(query, data, category="ALL"):
    query = query.lower()
    results = []

    for item in data:
        score = 0

        if query in item["name"].lower():
            score += 3
        if any(query in a.lower() for a in item["aliases"]):
            score += 2
        if query in item["building"].lower():
            score += 1

        if category != "ALL" and item["category"] != category:
            continue

        if score > 0:
            results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results]


# ---------- CLI UI ----------

def run():
    data = load_data()

    print("🔍 시설 검색 (종료: exit)\n")

    while True:
        query = input("검색어 입력: ")

        if query.lower() == "exit":
            break

        results = search(query, data)

        if not results:
            print("❌ 결과 없음\n")
            continue

        print("\n[검색 결과]")
        for item in results:
            room = f" ({item['room']})" if item["room"] else ""
            print(f"- {item['name']} | {item['building']} {item['floor']}층{room}")

        print()


if __name__ == "__main__":
    run()