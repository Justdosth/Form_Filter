import sqlite3

form_structure = {
    "اطلاعات شخصی": {
        "نام": "text",
        "نام خانوادگی": "text",
        "سن": "number",
        "جنس": ["مرد", "زن"],
        "وضعیت تاهل": ["مجرد", "متاهل"],
        "حقوق مورد نظر": "number",
        "تسلط بر زبان‌ها": "text",
        "سابقه کاری": "text",
    },
    "اطلاعات اضافی": {
        "اطلاعات آدرس": ["ساکن تهران", "ساکن کرج", "ساکن شهرستان"],
        "سرویس‌هایی که می‌دهد": ["کودک", "سالمند", "امور تخصصی بیماران"],
        "سرویس‌های اضافه": ["نظافت منزل", "آشپزی", "مهمان داری", "کمک آموزشی", "خرید منزل"],
        "مدرک و گواهی‌نامه‌ها": [
            "فاقد سواد", "زیر دیپلم", "دیپلم", "فوق دیپلم", "لیسانس", "فوق لیسانس", "دکتری"
        ],
        "سایر مدارک متفرقه": "text",
        "محدودیت‌ها": [
            "حیوان خانگی", "متراژ", "منزل قدیمی", "منزل نوساخت",
            "توانایی سفر خارج شهر", "توانایی سفر خارج کشور",
            "خدمت به خانم", "خدمت به آقا"
        ],
    },
    "ترجیحات خدمات": {
        "مناطق مورد نظر جهت خدمت‌دهی": "text",
        "شیفت‌های مورد نظر": "text",
        "تعطیل کاری": ["بله", "خیر"],
        "محدوده جدا": "text",
        "نیاز به نیروی کمکی": ["بله", "خیر"],
        "آوردن همراه": "text",
        "حضور همراه بیمار در منزل": ["بله", "خیر"],
        "توضیحات": "textarea",
    },
}

# Connect to SQLite database
def initialize_database():
    # Fetch data from the database
    conn = sqlite3.connect('instance/form_data.db')
    cursor = conn.cursor()

    # Dynamically generate columns based on orm_structure
    columns = []
    for section, fields in form_structure.items():
        for field, field_type in fields.items():
            if isinstance(field_type, list):  # Dropdown or multi-select
                columns.append(f"'{field}' TEXT")
            elif field_type in ["text", "textarea"]:
                columns.append(f"'{field}' TEXT")
            elif field_type == "number":
                columns.append(f"'{field}' INTEGER")

    # Create table dynamically
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS form_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {', '.join(columns)}
    )
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

# Initialize the database
if __name__ == "__main__":
    initialize_database()
