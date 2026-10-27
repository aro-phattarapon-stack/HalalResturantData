import pandas as pd

# ระบุ path ของไฟล์ที่ต้องการตรวจสอบ (เช่น ไฟล์ของ google maps หรือ wongnai)
file_path = "Data/google/google.csv"

# อ่านไฟล์
df = pd.read_csv(file_path)

print(f"จำนวนแถวทั้งหมด: {len(df)} | จำนวนคอลัมน์: {len(df.columns)}\n")
print(f"{'ลำดับ':<5} | {'ชื่อคอลัมน์ (CSS)':<30} | {'ตัวอย่างข้อมูลจริง'}")
print("-" * 75)

for idx, col in enumerate(df.columns):
    # ดึงค่าแรกที่ไม่ใช่ค่าว่าง (NaN)
    non_null_series = df[col].dropna()
    sample_val = non_null_series.iloc[0] if not non_null_series.empty else "ว่างเปล่า (All NaN)"
    
    # จัดรูปแบบข้อความไม่ให้ล้นบรรทัด
    sample_str = str(sample_val).replace("\n", " ")[:35]
    print(f"{idx:<5} | {col:<30} | {sample_str}")