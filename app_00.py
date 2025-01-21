from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

form_structure = {
    "اطلاعات شخصی": {
        "نام": "text",
        "نام خانوادگی": "text",
        "سن": "number",
        "جنس": ["مرد", "زن"],
        "وضعیت تاهل": ["مجرد", "متاهل"],
        "حقوق مورد نظر": "text",
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



@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Collect form data
        form_data = {
            field: request.form.getlist(field) if isinstance(options, list) else request.form.get(field)
            for page, fields in form_structure.items()
            for field, options in fields.items()
        }

        # Save data to Excel
        save_path = "responses.xlsx"
        if os.path.exists(save_path):
            existing_data = pd.read_excel(save_path)
            updated_data = pd.concat([existing_data, pd.DataFrame([form_data])], ignore_index=True)
        else:
            updated_data = pd.DataFrame([form_data])
        
        updated_data.to_excel(save_path, index=False)
        return "Form submitted successfully!"

    return render_template("multi_page_form.html", form_structure=form_structure)

if __name__ == "__main__":
    app.run(debug=True)
