from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from database import db, create_db, User, Acquaintance, Certificate, WorkExperience, generate_form_structure, User
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
        # Ensure it's a string and contains Unicode escape sequences
        if isinstance(s, str) and ('\\u' in s or '\\\\u' in s):
            return json.loads(f'{s}')  # Decode the escaped Unicode string
        return s  # Return as is if no escaping detected
    except json.JSONDecodeError:
        return s  # Return original string if decoding fails

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
                # value = decode_unicode_string(value)  # Decode any Unicode sequences

                # Handle JSON Fields (Checkboxes to JSON format)
                if english_key in JSON_FIELDS_MAPPING:
                    # Get the predefined list for the field
                    field_list = JSON_FIELDS_MAPPING[english_key]
                    # Get list of selected values for this field
                    selected_values = request.form.getlist(english_key)
                    # Create JSON object mapping each service to 1 (selected) or 0 (unselected)
                    json_data = {item: (1 if item in selected_values else 0) for item in field_list}
                    # 🔥 Convert to JSON string before storing in the database (without escaping Unicode)
                    user_data[english_key] = json.dumps(json_data, ensure_ascii=False)
                    print(user_data[english_key])
                
                # Handle Boolean Fields (special_care_companion, driving_capability)
                elif english_key in ["special_care_companion", "driving_capability"]:
                    user_data[english_key] = True if value == "on" else False
                
                # Handle Birth Date (persian to gregorian and age calculation)
                elif english_key == "birth_date" and value:
                    user_data["birth_date_Persian"] = value
                    converted_date = convert_persian_to_gregorian(value)  # Ensure this returns 'YYYY-MM-DD'
                    age = calculate_age(converted_date)
                    user_data["age"] = age
                    if isinstance(converted_date, str):  # Convert string to Python date object
                        user_data[english_key] = datetime.strptime(converted_date, "%Y-%m-%d").date()
                    else:
                        user_data[english_key] = converted_date  # If already a date, use as is
                
                # Handle other fields that are neither JSON nor Boolean
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
        # print(acquaintances_data)
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
                    # row = list(row)
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

@app.route('/search', methods=['GET'])
def search_database():
    # Check if the request is to clear filters
    clear_filters = request.args.get("clear_filters", "false").lower() == "true"

    if clear_filters:
        return redirect(url_for('view_data'))  # Render the full dataset view

    query = request.args.get("query", "")
    selected_columns = request.args.get("columns", "[]")
    min_value = request.args.get("min", "")
    max_value = request.args.get("max", "")
    dynamic_filter = request.args.get("dynamicFilter", "")

    try:
        selected_columns = json.loads(selected_columns) if selected_columns else []
    except json.JSONDecodeError:
        selected_columns = []

    conn = sqlite3.connect("instance/form_data.db")
    cursor = conn.cursor()

    # Fetch column names dynamically
    cursor.execute("PRAGMA table_info(user)")  
    all_columns = [col[1] for col in cursor.fetchall()]  

    if selected_columns:
        selected_columns = [col for col in selected_columns if col in all_columns]
    else:
        selected_columns = all_columns  # Default to all columns if none selected

    sql_query = f"SELECT {', '.join(all_columns)} FROM user WHERE 1=1"
    params = []

    if query and selected_columns:
        search_conditions = [f"{col} LIKE ?" for col in selected_columns]
        sql_query += f" AND ({' OR '.join(search_conditions)})"
        params.extend([f"%{query}%"] * len(selected_columns))

    # Apply filtering based on dynamically selected numeric columns
    if min_value and selected_columns:
        for column in selected_columns:
            min_column = column  # Assume first selected column is numeric
            sql_query += f" AND {min_column} >= ?"
            params.append(min_value)

    if max_value and selected_columns:
        for column in selected_columns:
            max_column = column  # Assume first selected column is numeric
            sql_query += f" AND {max_column} <= ?"
            params.append(max_value)

    if dynamic_filter and selected_columns:
        # Create a list of conditions for each selected column
        conditions = []
        for column in selected_columns:
            conditions.append(f"{column} LIKE ?")
        
        # Join all conditions with "OR" (to match any column)
        sql_query += " AND (" + " OR ".join(conditions) + ")"
        
        # Append the filter value for each condition
        params.extend([f"%{dynamic_filter}%"] * len(selected_columns))

    print("Executing Query:", sql_query)  # Debugging
    print("With Parameters:", params)  # Debugging

    cursor.execute(sql_query, params)
    results = cursor.fetchall()
    conn.close()

    results = [
        [decode_unicode_string(cell) if isinstance(cell, str) else cell for cell in row]
        for row in results
    ]

    print(results)

    # Process JSON fields (like services, limitations, etc.)
    for row in results:
        for i, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('{') and cell.endswith('}'):  # Check if it's JSON
                try:
                    json_data = json.loads(cell)
                    row[i] = ", ".join([key for key, value in json_data.items() if value == 1])
                except Exception as e:
                    row[i] = f"Invalid JSON: {e}"
    
    return jsonify(results)

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect("instance/form_data.db")
    cursor = conn.cursor()

    try:
        # Define related tables to delete user data
        related_tables = ["Acquaintance", "Certificate", "Work_Experience"]

        for table in related_tables:
            cursor.execute(f"DELETE FROM {table} WHERE form_id = ?", (user_id,))

        # Delete from the main user table
        cursor.execute("DELETE FROM user WHERE national_code = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=2000)


