import glob
import pandas as pd
import sqlite3

df_list = []

# คัดเลือกคอลัมน์ที่ต้องการจากผลลัพธ์ test.py
selected_cols = [
    "OSrXXb",           # 0: ชื่อร้าน
    "rllt__details",    # 1: หมวดหมู่ (ฮาลาล)
    "yi40Hd",           # 2: เรตติ้ง
    "RDApEe",           # 3: จำนวนรีวิว
    "rllt__details 2",  # 4: ช่วงราคา
    "rllt__details 3",  # 5: ที่อยู่/อำเภอ
    "wA1Bge src"        # 11: ลิงก์รูปภาพ
]

new_names = [
    "restaurant_name",
    "category",
    "rating",
    "review_count",
    "price_range",
    "district",
    "photo_url"
]

# 1. วนลูปอ่านทุกไฟล์ใน Data/google/
for file_path in glob.glob("Data/google/*.csv"):
    df = pd.read_csv(file_path)
    
    clean_temp = df.reindex(columns=selected_cols).copy()
    clean_temp.columns = new_names
    df_list.append(clean_temp)

# 2. รวมตาราง
google_df = pd.concat(df_list, ignore_index=True)

# 3. คลีนข้อความเบื้องต้น
# ตัดจุดหน้าคำว่า ฮาลาล (เช่น "·  · ฮาลาล" -> "ฮาลาล")
google_df["category"] = google_df["category"].astype(str).str.replace(r"[·\s]", "", regex=True)

# ลบวงเล็บออกจากจำนวนรีวิว (เช่น "(197)" -> "197")
google_df["review_count"] = google_df["review_count"].astype(str).str.replace(r"[()]", "", regex=True)

# ลบแถวที่ชื่อร้านซ้ำกัน
google_df = google_df.drop_duplicates(subset=["restaurant_name"])

print(f"รวมข้อมูล Google Maps ทั้งหมดได้: {len(google_df)} ร้าน")
print(google_df.head(3))

# 4. บันทึกลง halal.db
conn = sqlite3.connect("halal.db")
google_df.to_sql("google_restaurants", conn, if_exists="replace", index=False)
conn.close()

print("บันทึกตาราง google_restaurants ลงใน halal.db เรียบร้อยแล้ว")