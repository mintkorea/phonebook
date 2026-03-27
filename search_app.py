import csv
import io

# ---------- 데이터 (CSV 형식) ----------
CSV_DATA = """name,campus,building,floor,room,category
응급실,성의교정,병원,1,,진료
소아응급실,성의교정,병원,1,,진료
영상의학과,성의교정,병원,2,,진료
CT검사실,성의교정,병원,2,,검사
MRI검사실,성의교정,병원,2,,검사
카페,성의교정,병원,1,,편의
카페,성의교정,성의회관,1,,편의
편의점,성의교정,병원,1,,편의
전자파실험실,성의교정,옴니버스파크A,8,8128,실험실
세포배양실,성의교정,옴니버스파크A,8,8135,실험실
대강의실,성의교정,옴니버스파크C,3,,강의실
휴게실,성의교정,옴니버스파크C,2,,편의
장례식장,성의교정,장례식장,1,,시설"""

# ---------- 로직 함수 ----------

def make_aliases(name):
    """검색 성능을 위해 별칭 생성 (실 제외, 소문자화 등)"""
    return list(set([
        name,
        name.replace("실", ""),
        name.lower()
    ]))

def load_data_from_string(csv_text):
    """텍스트 데이터를 파싱하여 리스트로 반환"""
    data = []
    # io.StringIO를 사용하여 문자열을 파일처럼 읽음
    f = io.StringIO(csv_text.strip())
    reader = csv.DictReader(f)

    for i, row in enumerate(reader):
        data.append({
            "id": i + 1,
            "name": row["name"],
            "aliases": make_aliases(row["name"]),
            "campus": row["campus"],
            "building": row["building"],
            "floor": int(row["floor"]) if row["floor"] else 0,
            "room": row["room"] if row["room"] else None,
            "category": row["category"]
        })
    return data

def search(query, data, category="ALL"):
    """검색어와 데이터를 비교하여 결과 반환"""
    query = query.lower().strip()
    if not query:
        return []
        
    results = []

    for item in data:
        score = 0
        # 1. 이름에 포함된 경우 (가장 높은 점수)
        if query in item["name"].lower():
            score += 3
        # 2. 별칭에 포함된 경우
        elif any(query in a.lower() for a in item["aliases"]):
            score += 2
        # 3. 건물명에 포함된 경우
        elif query in item["building"].lower():
            score += 1

        # 카테고리 필터링
        if category != "ALL" and item["category"] != category:
            continue

        if score > 0:
            results.append((score, item))

    # 점수 높은 순으로 정렬
    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results]

# ---------- 실행 UI ----------

def run():
    # 데이터 로드
    data = load_data_from_string(CSV_DATA)

    print("🏥 성의교정 시설 검색 시스템")
    print("👉 '검색어'를 입력하세요. (종료: exit 또는 q)\n")

    while True:
        query = input("🔍 검색어: ").strip()

        if query.lower() in ["exit", "q", "ㅂㅂ"]:
            print("프로그램을 종료합니다.")
            break

        results = search(query, data)

        if not results:
            print("❌ 검색 결과가 없습니다.\n")
            continue

        print(f"\n✅ {len(results)}개의 결과를 찾았습니다:")
        for item in results:
            room_info = f" ({item['room']}호)" if item["room"] else ""
            print(f"[{item['category']}] {item['name']}")
            print(f"   📍 위치: {item['building']} {item['floor']}층{room_info}")
        print("-" * 30)

if __name__ == "__main__":
    run()