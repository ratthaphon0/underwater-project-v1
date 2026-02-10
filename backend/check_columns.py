# import psycopg2
# import os
# from dotenv import load_dotenv
# from pathlib import Path

# # Load .env
# current_dir = Path(__file__).resolve().parent
# env_path = current_dir.parent / '.env'
# if env_path.exists(): load_dotenv(dotenv_path=env_path)
# else: load_dotenv()

# # Config (ใช้ Port 5433 ตามที่คุณตั้งล่าสุด)
# DB_CONFIG = {
#     "dbname": os.getenv("DB_NAME", "underwater_db"),
#     "user": os.getenv("DB_USER", "admin"),
#     "password": os.getenv("DB_PASSWORD", "supaporn2026"),
#     "host": "localhost",
#     "port": os.getenv("DB_PORT", "5433") 
# }

# def check_table_schema(table_name):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         cursor = conn.cursor()
        
#         print(f"\n🔍 Inspecting Table: {table_name}")
#         print("-" * 30)
        
#         sql = """
#             SELECT column_name, data_type, is_nullable 
#             FROM information_schema.columns 
#             WHERE table_name = %s
#             ORDER BY ordinal_position;
#         """
#         cursor.execute(sql, (table_name,))
#         columns = cursor.fetchall()
        
#         if not columns:
#             print("⚠️  Table not found or empty schema!")
#         else:
#             for col in columns:
#                 print(f" - {col[0]} ({col[1]})")
                
#         conn.close()
#     except Exception as e:
#         print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     check_table_schema("sensors")
#     check_table_schema("underwater_data")