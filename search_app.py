import sys

# 1. 데이터 리스트 (딕셔너리 형태)
# 별도의 파일 없이 코드에 직접 포함하여 파일 경로 오류를 방지합니다.
facilities = [
    {"name": "응급실", "build": "병원", "floor": "1", "room": "", "cat": "진료"},
    {"name": "소아응급실", "build": "병원", "floor": "1", "room": "", "cat": "진료"},
    {"name": "영상의학과", "build": "병원", "floor": "2", "room": "", "cat": "진료"},
    {"name": "CT검사실", "build": "병원", "floor": "2", "room": "", "cat": "검사"},
    {"name": "MRI검사실", "build": "병원", "floor": "2", "room": "", "cat": "검사"},
    {"name": "카페", "build": "병원", "floor": "1", "room": "", "cat": "편의"},
    {"name": "카페", "build": "성의회관", "floor": "1", "room": "", "cat": "편의"},
    {"name": "편의점", "build": "병원", "floor": "1", "room": "", "cat": "편의"},
    {"name": "전자파실험실", "build": "옴니버스파크A", "floor": "8", "room": "8128", "cat": "실험실"},
    {"name": "세포배양실", "build": "옴니버스파크A", "floor": "8", "room": "8135", "cat": "실험실"},
    {"name": "대강의실", "build": "옴니버스파크C", "floor": "3", "room": "", "cat": "강의실"},
    {"name": "휴게실", "build": "옴니버스파크C", "floor": "2", "room": "", "cat": "편의"},
    {"name": "장례식장", "build": "장례식장", "floor": "1", "room": "", "cat": "시설"},
]

print("-" * 40)
print("▶ 시스템 시작됨 (이 문구가 보이나요?)")
print("-" * 40)

while True:
    # 사용자 입력 받기
    print("\n[안내] 찾으시는 시설명을 입력하세요. (종료: q)")
    user_input = input(">> 검색어: ").strip()

    # 종료 조건
    if user_input.lower() == 'q':
        print("프로그램을 종료합니다.")
        break

    if not user_input:
        print("검색어를 입력해 주세요.")
        continue

    # 검색 수행
    found_count = 0
    print(f"\n--- '{user_input}' 검색 결과 ---")
    
    for f in facilities:
        # 이름이나 건물명에 검색어가 포함되어 있는지 확인
        if user_input in f['name'] or user_input in f['build']:
            room_str = f"({f['room']}호)" if f['room'] else ""
            print(f"[{f['cat']}] {f['name']}")
            print(f"   위치: {f['build']} {f['floor']}층 {room_str}")
            print("-" * 30)
            found_count += 1

    if found_count == 0:
        print("검색 결과가 없습니다. 다시 입력해 보세요.")

# 프로그램이 갑자기 꺼지는 것을 방지하기 위해 마지막에 대기
input("\n엔터를 누르면 완전히 종료됩니다.")