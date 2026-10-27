import glob
import pandas as pd
import sqlite3

df_list = []

selected_cols = [
    "sc-1rqxbqo-0 href",
    "epawmp-0 src",
    "epawmp-0 src 2",
    "epawmp-0 src 3",
    "epawmp-0 src 4",
    "epawmp-0 src 5",
    "sc-1qge0b2-0",
    "Gap-sc-ilei7b",
    "sc-1uyabda-0",
    "rg12"
]

new_names = [
    "url", "food_photo1", "food_photo2", "food_photo3", "food_photo4",
    "food_photo5", "restaurant_name", "rating", "review", "price"
]


for file_path in glob.glob("Data/wongnai/*.csv"):
    df = pd.read_csv(file_path)

    clean_temp = df.reindex(columns=selected_cols).copy()
    clean_temp.columns = new_names

    df_list.append(clean_temp)

full_df = pd.concat(df_list, ignore_index=True)
print(f"รวมข้อมูลทั้งหมดได้: {len(full_df)} แถว")

# ลบแถวที่ชื่อร้าน (restaurant_name) หรือ url ซ้ำกัน ให้เหลือไว้แค่แถวแรกที่เจอ
full_df = full_df.drop_duplicates(subset=["url"])
print(f"หลังคัดร้านซ้ำออก เหลือข้อมูลจริง {len(full_df)} แถว")

conn = sqlite3.connect("halal.db")

full_df.to_sql("wongnai_restaurants", conn, if_exists="replace", index=False)

conn.close()
print("บันทึกข้อมูลทั้งหมดลงใน halal.db เรียบร้อยแล้ว!")