import sqlite3
import pandas as pd
import re
from pathlib import Path

# 1. กำหนด Path เริ่มต้นอ้างอิงจากตำแหน่งของไฟล์ research_clean.py
# Path(__file__).resolve() จะชี้มาที่ไฟล์นี้ ส่วน .parent จะถอยกลับไปที่โฟลเดอร์ cleaning
current_dir = Path(__file__).resolve().parent

# 2. สร้าง Path ไปยังไฟล์ CSV ที่อยู่ในโฟลเดอร์ Data
csv_path = current_dir / "Data" / "Untitled spreadsheet - Sheet1.csv"
df_research = pd.read_csv(csv_path)

df_research = df_research.rename(columns={
    'ร้าน': 'restaurant_name',
    'อำเภอ/ตำบล': 'district',
    'ประเภท': 'category',
    'พิกัด': 'location'
})

def clean_name(text):
    if pd.isna(text): 
        return ""
    text = str(text).replace(" ", "").lower()
    text = re.sub(r'(ร้านอาหาร|ร้าน|\(ฮาลาล\)|ฮาลาล|-สาขา.*)', '', text)
    text = re.sub(r'[:\-\(\)]', '', text) 
    return text

df_research['merge_key'] = df_research['restaurant_name'].apply(clean_name)

# 3. สร้าง Path ไปยังฐานข้อมูล halal.db
# current_dir.parent จะถอยขึ้นไปที่โฟลเดอร์หลัก (HalalResturant)
db_path = current_dir.parent / "halal.db"

# เชื่อมต่อและบันทึกข้อมูล
conn = sqlite3.connect(db_path)
df_research.to_sql('research_restaurants', conn, if_exists='replace', index=False)
print(f"บันทึกข้อมูลตาราง research_restaurants สำเร็จ จำนวน: {len(df_research)} ร้าน")
conn.close()