import requests
import json
from pathlib import Path

# หาก URL หลักล่มบ่อย สามารถเปลี่ยนไปใช้ Server สำรองได้ เช่น 
# url = "https://lz4.overpass-api.de/api/interpreter" 
url = "https://overpass-api.de/api/interpreter"

query = """
[out:json][timeout:60];
(
  nwr["amenity"~"restaurant|cafe|fast_food"](19.80, 99.70, 20.10, 100.00);
);
out center;
"""

# เก็บแค่ User-Agent ไว้เพื่อแสดงตัวตน เอา Accept ออกเพื่อเลี่ยง 406 จาก Nginx
headers = {
    "User-Agent": "DataEngineerPractice_ChiangRai/1.0" 
}

# กลับมาใช้ data={"data": query} ซึ่ง requests จะทำการแปลงเป็น application/x-www-form-urlencoded ให้โดยอัตโนมัติ
response = requests.post(url, data={"data": query}, headers=headers, timeout=60)

print("Status:", response.status_code)

if response.status_code == 200:
    data = response.json()
    elements = data.get('elements', [])
    print(f"ดึงข้อมูลสำเร็จ พบร้านอาหารจำนวน: {len(elements)} แห่ง")
    
    output_file = Path("chiangrai_restaurants.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"บันทึกข้อมูลลงไฟล์ {output_file} เรียบร้อยแล้ว")
else:
    print("เกิดข้อผิดพลาดในการดึงข้อมูล:")
    print(response.text)