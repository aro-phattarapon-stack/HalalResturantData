import json
import pandas as pd
import sqlite3

with open("chiangrai_restaurants.json", "r", encoding="utf-8") as f:
    data = json.load(f)

elements = data.get("elements", [])
halal_restaurants = []

# คำสำคัญที่บ่งบอกว่าเป็นร้านอาหารฮาลาลหรืออาหารอิสลาม
keywords = ["ฮาลาล", "มุสลิม", "อิสลาม", "halal"]

for item in elements:
    tags = item.get("tags", {})
    name = tags.get("name")
    
    if not name:
        continue

    cuisine = tags.get("cuisine", "").lower()
    diet_halal = tags.get("diet:halal", "").lower()
    name_lower = name.lower()

    # ตรวจสอบเงื่อนไข:
    # 1. มีคำว่า halal ใน cuisine หรือ diet:halal เป็น yes
    # 2. หรือมีคำสำคัญเกี่ยวกับฮาลาล/อิสลามอยู่ในชื่อร้าน
    is_tag_halal = ("halal" in cuisine) or (diet_halal == "yes")
    is_name_halal = any(kw in name_lower for kw in keywords)

    if is_tag_halal or is_name_halal:
        lat = item.get("lat") or (item.get("center", {}).get("lat") if item.get("center") else None)
        lon = item.get("lon") or (item.get("center", {}).get("lon") if item.get("center") else None)

        halal_restaurants.append({
            "osm_id": item.get("id"),
            "restaurant_name": name,
            "category": tags.get("amenity"),
            "cuisine": tags.get("cuisine"),
            "diet_halal": tags.get("diet:halal"),
            "latitude": lat,
            "longitude": lon,
            "source": "overpass"
        })

# แปลงเป็น DataFrame
halal_df = pd.DataFrame(halal_restaurants)
halal_df = halal_df.drop_duplicates(subset=["osm_id"])

print(f"พบร้านอาหารฮาลาลจาก Overpass ทั้งหมด: {len(halal_df)} ร้าน")
print(halal_df[["restaurant_name", "cuisine", "diet_halal", "latitude", "longitude"]])

# 1. เชื่อมต่อฐานข้อมูลเดิม
conn = sqlite3.connect("halal.db")

# 2. บันทึกตาราง overpass_restaurants
halal_df.to_sql("overpass_restaurants", conn, if_exists="replace", index=False)

# 3. ปิดการเชื่อมต่อ
conn.close()
print("บันทึกข้อมูล Overpass ลงใน halal.db เรียบร้อยแล้ว!")