from flask import Flask, render_template, request, redirect, jsonify
from database import db, FormData, create_db, generate_form_structure  # Import database and models
from threading import Timer
from waitress import serve
from flask_cors import CORS
import webbrowser
import sqlite3

app = Flask(__name__)
CORS(app)

# Configure the database URI (use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database tables (if they don't exist yet)
create_db(app)

@app.route("/", methods=["GET", "POST"])
def home():
    form_structure = generate_form_structure() 
    return render_template('multi_page_form.html', form_structure=form_structure)
def form():
    if request.method == "POST":
        # Collect data from form
        form_data = FormData(
            name=request.form['نام'],
            last_name=request.form['نام خانوادگی'],
            national_code=request.form['کد ملی'],
            birth_date=request.form.get('سن'),
            gender=request.form.get('جنس'),
            marital_status=request.form.get('وضعیت تاهل'),
            salary=request.form.get('حقوق مورد نظر', type=float),
            language_proficiency=request.form.get('تسلط بر زبان‌ها'),
            work_experience=request.form.get('سابقه کاری'),
            
            # Additional Information
            address=request.form.get('اطلاعات آدرس'),
            services_offered=request.form.get('سرویس‌هایی که می‌دهد'),
            extra_services=request.form.get('سرویس‌های اضافه'),
            certifications=request.form.get('مدرک و گواهی‌نامه‌ها'),
            other_documents=request.form.get('سایر مدارک متفرقه'),
            limitations=request.form.get('محدودیت‌ها'),

            # Service Preferences
            preferred_areas=request.form.get('مناطق مورد نظر جهت خدمت‌دهی'),
            preferred_shifts=request.form.get('شیفت‌های مورد نظر'),
            holiday_work=request.form.get('تعطیل کاری'),
            separate_zone=request.form.get('محدوده جدا'),
            need_helper=request.form.get('نیاز به نیروی کمکی'),
            bring_accompanying=request.form.get('آوردن همراه'),
            patient_accompanying_at_home=request.form.get('حضور همراه بیمار در منزل'),
            comments=request.form.get('توضیحات')
        )

        # Save data to database
        try:
            db.session.add(form_data)
            db.session.commit()
            return "اطلاعات با موفقیت ارسال شد!"
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"

    return render_template("multi_page_form.html", form_structure=form_structure)

@app.route('/view-data')
def view_data():
    # Flatten the form structure for headers
    headers = []
    for section, fields in form_structure.items():
        headers.extend(fields.keys())
    
    # Fetch data from the database
    conn = sqlite3.connect('instance/form_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM form_data")  # Adjust table name if needed
    rows = cursor.fetchall()
    conn.close()

    return render_template('view_data.html', headers=headers, rows=rows)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Map Persian field names to model attributes
        field_mapping = {
            "نام": "name",
            "نام خانوادگی": "last_name",
            "سن": "age",
            "جنس": "gender",
            "وضعیت تاهل": "marital_status",
            "کد ملی": "national_code",
            "تسلط بر زبان‌ها": "language_proficiency",
            "سابقه کاری": "work_experience",
            "اطلاعات آدرس": "address",
            "شهرستان": "country_name",
            "سرویس‌هایی که می‌دهد": "services_offered",
            "سرویس‌های اضافه": "extra_services",
            "مدرک و گواهی‌نامه‌ها": "certifications",
            "سایر مدارک متفرقه": "other_documents",
            "محدودیت‌ها": "limitations",
            "مناطق مورد نظر جهت خدمت‌دهی": "preferred_areas",
            "شیفت‌های مورد نظر": "preferred_shifts",
            "تعطیل کاری": "holiday_work",
            "محدوده جدا": "separate_zone",
            "نیاز به نیروی کمکی": "need_helper",
            "آوردن همراه": "bring_accompanying",
            "حضور همراه بیمار در منزل": "patient_accompanying_at_home",
            "توضیحات": "comments",
        }

        # # Map the request form to model fields
        # form_data = {field_mapping[key]: value for key, value in request.form.items() if key in field_mapping}

        # Map the request form to model fields, handling empty strings
        form_data = {
            field_mapping[key]: (value if value.strip() else None)  # Convert empty strings to None
            for key, value in request.form.items()
            if key in field_mapping
        }

        # Optional: If you want to handle the country_name (dynamic field)
        country_name = form_data.get('country_name', None)
        
        # Handle optional `country_name` dynamically
        if 'country_name' not in form_data:
            form_data['country_name'] = None  # Default value if not provided

                # Convert specific fields to their expected types if needed
        if 'salary' in form_data and form_data['salary'] is not None:
            form_data['salary'] = float(form_data['salary'])  # Convert salary to float

        if 'age' in form_data and form_data['age'] is not None:
            form_data['age'] = int(form_data['age'])  # Convert age to int

        # Create a new FormData instance
        new_entry = FormData(**form_data)

        # Save data to the database
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Data submitted successfully!", "status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "status": "error"}), 500



def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=2000)
