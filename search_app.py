data = [
    {"name": "카페", "building": "병원", "floor": 1},
    {"name": "응급실", "building": "병원", "floor": 1},
]

while True:
    query = input("검색어 입력: ")

    for item in data:
        if query in item["name"]:
            print(item["name"], "-", item["building"], item["floor"], "층")