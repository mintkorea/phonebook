import csv
import os

def load_data():
    data = []
    file_path = "data.csv"
    
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"⚠️ 오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return []

    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                data.append({
                    "id": i + 1,
                    "name": row.get("name", "이름없음"),
                    "aliases": make_aliases(row.get("name", "")),
                    "campus": row.get("campus", ""),
                    "building": row.get("building", ""),
                    "floor": int(row.get("floor", 0)) if row.get("floor") else 0,
                    "room": row.get("room") or None,
                    "category": row.get("category", "ETC")
                })
            except Exception as e:
                print(f"데이터 로드 중 오류 발생 ({i+1}행): {e}")
                
    return data