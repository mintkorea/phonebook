import io
import csv

# 1. 데이터베이스 (CSV 파일을 코드 내부에 포함)
DATA_STR = """name,campus,building,floor,room,category
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

def get_data():
    """문자열 데이터를 리스트로 변환"""
    data = []
    f = io.StringIO(DATA_STR.strip())
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        row['id'] = i + 1
        # 검색용 별칭 (이름에서 '실' 제거 버전 포함)
        row['alias'] = [row['name'], row['name'].replace("실", ""), row['name'].lower()]
        data.append(row)
    return data

def main():
    try:
        facilities = get_data()
        
        print("="*45)
        print("   🏥 성의교정 스마트 건물 안내 시스템")
        print("        (종료하려면 'q'를 입력하세요)")
        print("="*45)

        while True:
            print("\n" + "·"*45)
            query = input("📍 찾으시는 시설이나 건물을 입력하세요: ").strip()

            if query.lower() in ['q', 'exit', '종료']:
                print("\n👋 시스템을 종료합니다. 안녕히 가십시오.")
                break

            if not query:
                continue

            # 검색 로직 (이름, 별칭, 건물명 통합 검색)
            results = []
            for item in facilities:
                if any(query.lower() in a.lower() for a in item['alias']) or query in item['building']:
                    results.append(item)

            # 결과 출력
            if results:
                print(f"\n✨ '{query}' 검색 결과 ({len(results)}건):")
                print("-" * 45)
                for res in results:
                    # 호수 정보가 있으면 표시
                    room_info = f" [{res['room']}호]" if res['room'] else ""
                    print(f"[{res['category']}] {res['name']}")
                    print(f" 🚩 위치: {res['building']} {res['floor']}층{room_info}")
                    print("-" * 20)
            else:
                print(f"\n❌ '{query}'에 대한 정보를 찾을 수 없습니다.")
                print("Tip: '카페', '응급실', '옴니버스' 등으로 검색해 보세요.")

    except Exception as e:
        print(f"\n⚠️ 시스템 오류 발생: {e}")
    
    # 프로그램이 바로 닫히지 않도록 대기
    input("\n[엔터키를 누르면 창이 닫힙니다]")

if __name__ == "__main__":
    main()