from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from database import db, create_db, User, Acquaintance, Certificate, WorkExperience, generate_form_structure
from datetime import datetime
from threading import Timer
from waitress import serve
from persiantools.jdatetime import JalaliDate
from pprint import pprint
from datetime import datetime
from sqlalchemy import inspect
from flask_cors import CORS
import webbrowser
import sqlite3
import os

def convert_persian_to_gregorian(persian_date):
    """
    Converts a Persian (Jalali) date string (e.g., '1403/12/08') to a Gregorian date string ('YYYY-MM-DD').
    """
    try:
        if persian_date:
            year, month, day = map(int, persian_date.split('/'))
            gregorian_date = JalaliDate(year, month, day).to_gregorian()
            return gregorian_date.strftime('%Y-%m-%d')  # Convert to string format
        return None  # Return None if the date is empty
    except Exception as e:
        print(f"Error converting Persian date: {str(e)}")
        return None

app = Flask(__name__)
CORS(app)

# Set the secret key for sessions
app.config['SECRET_KEY'] = os.urandom(24)  # This generates a random 24-byte key

# Configure the database URI (use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database tables (if they don't exist yet)
create_db(app)

# Initialize global variables with app context
with app.app_context():
    form_structure, persian_to_english_mapping = generate_form_structure()


@app.route("/", methods=["GET", "POST"])
def home():
    
    return render_template('multi_page_form.html', form_structure=form_structure, persian_to_english_mapping=persian_to_english_mapping)


@app.route('/submit-form', methods=['POST'])

def submit_form():
    try:
         # 1️⃣ Get Actual Columns from User Model
        user_columns = list(inspect(User).c.keys())  # Get column names as a list

        # 2️⃣ Dynamically Collect User Data
        user_data = {}
        for persian_key, english_key in persian_to_english_mapping.items():
            if english_key in user_columns:  # Only keep valid columns
                value = request.form.get(english_key)
                if english_key in ["special_care_companion", "driving_capability"]:
                    user_data[english_key] = True if value == "on" else False
                elif english_key == "birth_date" and value:
                    user_data["birth_date_Persian"] = value
                    converted_date = convert_persian_to_gregorian(value)  # Ensure this returns 'YYYY-MM-DD'
                    if isinstance(converted_date, str):  # Convert string to Python date object
                        user_data[english_key] = datetime.strptime(converted_date, "%Y-%m-%d").date()
                    else:
                        user_data[english_key] = converted_date  # If already a date, use as is
                elif english_key != "birth_date_Persian":
                    user_data[english_key] = value

        # 3️⃣ Create and Add User Object
        user = User(**user_data)  # Ensure only valid columns are passed
        db.session.add(user)
        db.session.flush()  # Get user.id before inserting related records

        # 4️⃣ Dynamically Collect Acquaintances Data
        acquaintances_data = zip(
            request.form.getlist('آشنایان_نام و نام خانوادگی[]'),
            request.form.getlist('آشنایان_نسبت با شما[]'),
            request.form.getlist('آشنایان_آدرس محل سکونت[]'),
            request.form.getlist('آشنایان_شماره تماس[]')
        )
        
        for name, relation, contact in acquaintances_data:
            if name:
                acquaintance = Acquaintance(user_id=user.national_code, acquaintances_name=name, acquaintances_relation=relation, work_experience_company_contact=contact)
                db.session.add(acquaintance)

        # 5️⃣ Dynamically Collect Certificates
        certificates_data = zip(
            request.form.getlist('مدارک_عنوان مدرک[]'),
            request.form.getlist('مدارک_محل اخذ[]'),
            request.form.getlist('مدارک_سال اخذ[]')
        )

        for title, institution, year in certificates_data:
            if title:
                certificate = Certificate(user_id=user.national_code, certificate_title=title, certificate_institution=institution, certificate_year=year)
                db.session.add(certificate)

        # 6️⃣ Dynamically Collect Work Experience
        work_experience_data = zip(
            request.form.getlist('سوابق کاری_نام شرکت (نام کارفرما)[]'),
            request.form.getlist('سوابق کاری_شرح مسئولیت‌ها[]'),
            request.form.getlist('سوابق کاری_علت قطع همکاری[]')
        )

        for company_name, responsibilities, reason in work_experience_data:
            if company_name:
                work_exp = WorkExperience(user_id=user.national_code, work_experience_company_name=company_name, work_experience_responsibilities=responsibilities, work_experience_reason_for_leaving=reason)
                db.session.add(work_exp)

        # 7️⃣ Commit all data to the database
        db.session.commit()
        return jsonify({"success": True, "message": "Form submitted successfully!"})  # Send JSON response

    except Exception as e:
        db.session.rollback()
        error_type = type(e).__name__  # Get the error type
        error_message = str(e)  # Get the actual error message
        return jsonify({"success": False, "error_type": error_type, "message": error_message})

@app.route('/view-data')
def view_data():
    # Fetch form data
    conn = sqlite3.connect('instance/form_data.db')
    cursor = conn.cursor()
    
    # Fetch data from the main form_data table
    cursor.execute("SELECT * FROM User")  # Adjust table name if needed
    form_data_rows = cursor.fetchall()
    
    # # Fetch data from additional tables (e.g., acquaintances, certificates, work experience)
    # cursor.execute("SELECT * FROM acquaintances")  # Replace with your actual table name
    # acquaintances_rows = cursor.fetchall()

    # cursor.execute("SELECT * FROM certificates")  # Replace with your actual table name
    # certificates_rows = cursor.fetchall()

    # cursor.execute("SELECT * FROM work_experience")  # Replace with your actual table name
    # work_experience_rows = cursor.fetchall()
    
    conn.close()
    

    # Now, pass the data to the template for rendering
    return render_template(
        'view_data.html',
        form_data_rows=form_data_rows
    )


def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=2000)
