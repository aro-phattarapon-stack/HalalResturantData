import sqlite3
import pandas as pd
import re
import json

conn = sqlite3.connect('halal.db')
df_g = pd.read_sql("SELECT * FROM google_restaurants", conn)
df_o = pd.read_sql("SELECT * FROM overpass_restaurants", conn)
df_w = pd.read_sql("SELECT * FROM wongnai_restaurants", conn)
# โหลดข้อมูลจากตารางใหม่
df_r = pd.read_sql("SELECT * FROM research_restaurants", conn) 

def clean_name(text):
    if pd.isna(text): 
        return ""
    text = str(text).replace(" ", "").lower()
    
    # 1. ตัดคำทั่วไปและสัญลักษณ์
    text = re.sub(r'(ร้านอาหาร|ร้าน|\(ฮาลาล\)|ฮาลาล|-สาขา.*)', '', text)
    text = re.sub(r'[:\-\(\)]', '', text) 
    
    # 2. ตัดตัวอักษรภาษาอังกฤษทั้งหมด (a-z) 
    # เพราะข้อมูล Wongnai หรือ Google มักชอบใส่วงเล็บชื่อภาษาอังกฤษต่อท้ายชื่อไทย
    text = re.sub(r'[a-z]', '', text)
    
    # 3. ตัดคำอธิบายประเภทอาหารที่มักชอบปนมากับชื่อร้าน
    text = re.sub(r'(อาหารมุสลิม|มุสลิม|อาหาร|อิสลาม)', '', text)
    
    return text

df_g['merge_key'] = df_g['restaurant_name'].apply(clean_name)
df_o['merge_key'] = df_o['restaurant_name'].apply(clean_name)
df_w['merge_key'] = df_w['restaurant_name'].apply(clean_name)
# สร้าง merge_key ให้ตารางใหม่
df_r['merge_key'] = df_r['restaurant_name'].apply(clean_name) 

# เปลี่ยนชื่อคอลัมน์ที่มีโอกาสซ้ำกันก่อน Merge (เพิ่ม district_g และ name_r, category_r, district_r)
df_g = df_g.rename(columns={'restaurant_name': 'name_g', 'rating': 'rating_g', 'category': 'category_g', 'district': 'district_g'})
df_o = df_o.rename(columns={'restaurant_name': 'name_o', 'category': 'category_o'})
df_w = df_w.rename(columns={'restaurant_name': 'name_w', 'rating': 'rating_w'})
df_r = df_r.rename(columns={'restaurant_name': 'name_r', 'category': 'category_r', 'district': 'district_r'})

# รวมข้อมูลแบบ Outer Join เข้าด้วยกันทั้งหมด 4 ตาราง
df_merge = pd.merge(df_g, df_o, on='merge_key', how='outer')
df_merge = pd.merge(df_merge, df_w, on='merge_key', how='outer')
df_merge = pd.merge(df_merge, df_r, on='merge_key', how='outer')

# ยุบรวมชื่อร้านจากทั้ง 4 แหล่ง
df_merge['name'] = df_merge['name_g'].combine_first(df_merge['name_w']).combine_first(df_merge['name_o']).combine_first(df_merge['name_r'])
df_merge = df_merge.dropna(subset=['name']).drop_duplicates(subset=['name']).reset_index(drop=True)

df_final = pd.DataFrame()
df_final['id'] = df_merge.index + 1
df_final['name'] = df_merge['name']
# เติมเต็ม district จาก Google ก่อน ถ้าไม่มีให้ใช้จาก Research
df_final['district'] = df_merge['district_g'].combine_first(df_merge['district_r']) 
df_final['zone'] = None
# นำประเภทอาหารจาก Research มาร่วมด้วย
df_final['cuisine'] = df_merge['category_g'].combine_first(df_merge['category_o']).combine_first(df_merge['cuisine']).combine_first(df_merge['category_r'])
df_final['priceLevel'] = df_merge['price_range'].combine_first(df_merge['price'])
df_final['minPrice'] = None
df_final['maxPrice'] = None
df_final['rating'] = df_merge['rating_g'].combine_first(df_merge['rating_w'])
df_final['halalStatus'] = "muslim-friendly"
df_final['description'] = df_merge['review']
df_final['menu'] = json.dumps([])
df_final['openingHours'] = None
df_final['amenities'] = json.dumps([])
df_final['latitude'] = df_merge['latitude']
df_final['longitude'] = df_merge['longitude']
df_final['verified'] = False
df_final['image'] = df_merge['food_photo1'].combine_first(df_merge['photo_url'])

df_final.to_sql('merged_restaurants_json', conn, if_exists='replace', index=False)
print(f"บันทึกข้อมูลสำเร็จ จำนวน: {len(df_final)} ร้าน")
conn.close()