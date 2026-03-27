print("프로그램 시작")

data = [
    {"name": "카페", "building": "병원", "floor": 1},
    {"name": "응급실", "building": "병원", "floor": 1},
]

while True:
    query = input("검색어 입력: ")

    if query == "exit":
        break

    found = False

    for item in data:
        if query in item["name"]:
            print(f"{item['name']} - {item['building']} {item['floor']}층")
            found = True

    if not found:
        print("결과 없음")