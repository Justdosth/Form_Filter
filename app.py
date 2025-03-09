from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from database import db, create_db, User, Acquaintance, Certificate, WorkExperience, generate_form_structure
from database import SERVICES_LIST, DRIVING_LIST, EXTRA_SERVICES_LIST, LIMITATIONS_LIST, EQUIPMENT_EXPERIENCE_LIST
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
import json
import os
from datetime import datetime


JSON_FIELDS_MAPPING = {
    'services_offered': SERVICES_LIST,
    'extra_services': EXTRA_SERVICES_LIST,
    'limitations': LIMITATIONS_LIST,
    'equipment_experience': EQUIPMENT_EXPERIENCE_LIST,
    'driving_capability' : DRIVING_LIST,
    'gender' : ['خانم', 'آقا'],
    'marital_status' : ['مجرد', 'متاهل']
}

def calculate_age(birthdate_str):
    """Calculate age from a birthdate string (YYYY-MM-DD)."""
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    age = int(today.year) - int(birthdate.year)
    return age

def decode_unicode_string(s):
    try:
        # Check if the string has Unicode escape sequences
        if isinstance(s, str) and '\\u' in s:
            return json.loads(f'"{s}"')
        return s
    except json.JSONDecodeError:
        return s

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
                value = decode_unicode_string(value)
                # Handle JSON Fields (Checkboxes to JSON format)
                if english_key in JSON_FIELDS_MAPPING:
                    # Get the predefined list for the field
                    field_list = JSON_FIELDS_MAPPING[english_key]
                    # Get list of selected values for this field
                    selected_values = request.form.getlist(english_key)
                    # Create JSON object mapping each service to 1 (selected) or 0 (unselected)
                    json_data = {item: (1 if item in selected_values else 0) for item in field_list}
                    user_data[english_key] = json_data
                elif english_key in ["special_care_companion", "driving_capability"]:
                    user_data[english_key] = True if value == "on" else False
                elif english_key == "birth_date" and value:
                    user_data["birth_date_Persian"] = value
                    converted_date = convert_persian_to_gregorian(value)  # Ensure this returns 'YYYY-MM-DD'
                    age = calculate_age(converted_date)
                    user_data["age"] = age
                    if isinstance(converted_date, str):  # Convert string to Python date object
                        user_data[english_key] = datetime.strptime(converted_date, "%Y-%m-%d").date()
                    else:
                        user_data[english_key] = converted_date  # If already a date, use as is
                elif english_key != "birth_date_Persian" and english_key != "age":
                    user_data[english_key] = value

        # 3️⃣ Create and Add User Object
        user = User(**user_data)  # Ensure only valid columns are passed
        db.session.add(user)
        db.session.flush()  # Get user.id before inserting related records

        # 4️⃣ Dynamically Collect Acquaintances Data
        acquaintances_data = list(zip(
            request.form.getlist('acquaintances_name'),
            request.form.getlist('acquaintances_relation'),
            request.form.getlist('acquaintances_address'),
            request.form.getlist('acquaintances_contact')
        ))
        print(acquaintances_data)
        for name, relation, address, contact in acquaintances_data:
            if name:
                acquaintance = Acquaintance(form_id=user.national_code, name=name, relation=relation, address=address, contact=contact)
                db.session.add(acquaintance)

        # 5️⃣ Dynamically Collect Certificates
        certificates_data = list(zip(
            request.form.getlist('certificate_title'),
            request.form.getlist('certificate_institution'),
            request.form.getlist('certificate_year')
        ))

        for title, institution, year in certificates_data:
            if title:
                certificate = Certificate(form_id=user.national_code, title=title, institution=institution, year=year)
                db.session.add(certificate)

        # 6️⃣ Dynamically Collect Work Experience
        work_experience_data = list(zip(
            request.form.getlist('work_experience_company_name'),
            request.form.getlist('work_experience_responsibilities'),
            request.form.getlist('work_experience_reason_for_leaving'),
            request.form.getlist('work_experience_company_contact'),
        ))

        for company_name, responsibilities, reason, contact in work_experience_data:
            if company_name:
                work_exp = WorkExperience(form_id=user.national_code, company_name=company_name, responsibilities=responsibilities, reason_for_leaving=reason, company_contact=contact)
                db.session.add(work_exp)

        # 7️⃣ Commit all data to the database
        db.session.commit()
        return jsonify({"success": True, "message": "Form submitted successfully!"})  # Send JSON response

    except Exception as e:
        db.session.rollback()
        error_type = type(e).__name__  # Get the error type
        error_message = str(e)  # Get the actual error message
        print(f"Error: {error_message}")  # Print the error message for debugging
        return jsonify({"success": False, "error_type": error_type, "message": error_message})

@app.route('/view-data')
def view_data():
    conn = sqlite3.connect('instance/form_data.db')
    cursor = conn.cursor()

    # Fetch column names dynamically
    cursor.execute("PRAGMA table_info(User)")  # Get column names of the User table
    column_info = cursor.fetchall()
    column_names = [col[1] for col in column_info]  # Extract column names

    # Fetch data from the User table
    cursor.execute("SELECT * FROM User")
    form_data_rows = cursor.fetchall()

    conn.close()

    # Decode and process each row
    form_data_rows = [
        [decode_unicode_string(cell) if isinstance(cell, str) else cell for cell in row]
        for row in form_data_rows
    ]

    # Process JSON fields (like services, limitations, etc.)
    for row in form_data_rows:
        for i, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('{') and cell.endswith('}'):  # Check if it's JSON
                try:
                    # Try to parse the JSON field
                    json_data = json.loads(cell)
                    # Convert it to a human-readable format (e.g., selected services)
                    row[i] = ", ".join([key for key, value in json_data.items() if value == 1])
                except Exception as e:
                    row[i] = f"Invalid JSON: {e}"

    return render_template(
        'view_data.html',
        column_names=column_names,  # Pass column names to the template
        form_data_rows=form_data_rows,
        JSON_FIELDS_MAPPING=JSON_FIELDS_MAPPING
    )

@app.route('/get_related_data')
def get_related_data():
    user_id = request.args.get('user_id')  # Get the user_id from query params
    table_name = request.args.get('table_name') # Get the table_name from query params

    if not user_id or not table_name:
        return jsonify({"error": "Missing parameters"}), 400

    # Validate table_name against a list of allowed table names to avoid SQL injection
    valid_tables = ["Acquaintance", "Certificate", "Work_Experience"]
    if table_name not in valid_tables:
        return jsonify({"error": "Invalid table name"}), 400

    conn = sqlite3.connect('instance/form_data.db')
    cursor = conn.cursor()

    # Fetch related data from the specified table
    cursor.execute(f"SELECT * FROM {table_name} WHERE form_id = ?", (user_id,))
    data = cursor.fetchall()

    # Get column names
    column_names = [desc[0] for desc in cursor.description]

    conn.close()

    # Convert to list of dictionaries
    results = [dict(zip(column_names, row)) for row in data]

    return jsonify(results)  # Return the fetched data as JSON


def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=2000)
