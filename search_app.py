import csv
import io
import time

# 1. 데이터 정의
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

def run_app():
    try:
        print("========================================")
        print(" 시스템을 초기화 중입니다...")
        time.sleep(0.5) # 로딩되는 느낌을 주기 위한 지연
        
        # 데이터 로드
        data = []
        f = io.StringIO(CSV_DATA.strip())
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
        
        print(f" ✅ {len(data)}개의 데이터를 성공적으로 불러왔습니다.")
        print(" 'exit'를 입력하면 프로그램이 종료됩니다.")
        print("========================================\n")

        while True:
            query = input("🔍 검색어를 입력하세요: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', '종료', 'q']:
                print("\n프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
                time.sleep(1)
                break

            # 검색 로직
            results = [item for item in data if query in item['name']]

            if results:
                print(f"\n[검색 결과: {len(results)}건]")
                for res in results:
                    room = f"({res['room']}호)" if res['room'] else ""
                    print(f" - {res['name']} | {res['building']} {res['floor']}층 {room} [{res['category']}]")
                print("-" * 40)
            else:
                print(f" ❌ '{query}'에 대한 검색 결과가 없습니다.\n")

    except Exception as e:
        print(f"‼️ 실행 중 오류가 발생했습니다: {e}")
        input("오류 내용을 확인하신 후 엔터를 눌러주세요...")

if __name__ == "__main__":
    run_app()