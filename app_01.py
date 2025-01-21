import webbrowser
from threading import Timer
from flask import Flask, render_template, request
import pandas as pd
import os
import logging
from waitress import serve

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="app.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

# Configure the database URI (use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Collect form data
        form_data = {}
        
        # Loop through form structure and get the corresponding form input values
        for page, fields in form_structure.items():
            for field, options in fields.items():
                if isinstance(options, list):  # Select fields with options (dropdowns)
                    form_data[field] = request.form.get(field)
                else:
                    form_data[field] = request.form.get(field)
        
        # Print the collected data for debugging
        print(form_data)

        # Save data to Excel
        save_path = "patient_data.xlsx"
        if os.path.exists(save_path):
            try:
                # Read the existing Excel file
                existing_data = pd.read_excel(save_path)
                # Append new data to the existing dataframe
                updated_data = pd.concat([existing_data, pd.DataFrame([form_data])], ignore_index=True)
            except Exception as e:
                print(f"Error reading existing Excel file: {e}")
                # If reading fails, create a new DataFrame
                updated_data = pd.DataFrame([form_data])
        else:
            # If the file doesn't exist, create a new DataFrame
            updated_data = pd.DataFrame([form_data])
        
        # Write the updated data to the Excel file
        try:
            updated_data.to_excel(save_path, index=False)
            print("Data saved successfully!")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
        
        return "Form submitted successfully!"  # Return success message after submission

    return render_template("multi_page_form.html", form_structure=form_structure)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    
    Timer(1, open_browser).start()  # Open the browser after 1 second
    # app.run(debug=False, use_reloader=False, host="127.0.0.1", port=5000)
    serve(app, host="0.0.0.0", port=5000)
