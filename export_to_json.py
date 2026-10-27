import sqlite3
import pandas as pd
import numpy as np
import json
from pathlib import Path

# 1. กำหนด Path 
current_dir = Path(__file__).resolve().parent
db_path = current_dir / "halal.db"
json_output_path = current_dir / "halal_restaurants.json"

# 2. เชื่อมต่อฐานข้อมูลและดึงข้อมูล
conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT * FROM merged_restaurants_json", conn)
conn.close()

# 3. แปลงคอลัมน์ที่เป็น JSON String (menu, amenities) กลับเป็น Python List
# เพื่อให้เวลาเซฟเป็นไฟล์ JSON มันจะกลายเป็น Array จริงๆ ไม่ใช่ข้อความ
df['menu'] = df['menu'].apply(lambda x: json.loads(x) if pd.notna(x) and x != "" else [])
df['amenities'] = df['amenities'].apply(lambda x: json.loads(x) if pd.notna(x) and x != "" else [])

# 4. จัดการค่าว่าง (Missing Values) แบบเด็ดขาด
df = df.astype(object) # บังคับให้ทุกคอลัมน์รองรับค่า None
df = df.replace({np.nan: None}) # แทนที่ NaN ด้วย None เพื่อให้เซฟเป็น null

# 5. แปลง DataFrame เป็น List of Dictionaries
records = df.to_dict(orient='records')

# 6. บันทึกเป็นไฟล์ JSON
with open(json_output_path, 'w', encoding='utf-8') as f:
    # ensure_ascii=False ทำให้ภาษาไทยไม่กลายเป็นตัวอักขระยึกยือ (\u0e23...)
    # indent=4 ทำให้ไฟล์ JSON มีการเว้นบรรทัดและย่อหน้า อ่านง่าย (Pretty Print)
    json.dump(records, f, ensure_ascii=False, indent=4)

print(f"ส่งออกไฟล์ JSON สำเร็จ! บันทึกไว้ที่: {json_output_path}")