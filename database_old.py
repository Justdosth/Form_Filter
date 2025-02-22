from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    national_code = db.Column(db.String(50), nullable=False)

    birth_date = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, nullable=True)

    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(10), nullable=True)

    salary = db.Column(db.Float, nullable=True)

    language_proficiency = db.Column(db.String(200), nullable=True)

    companion = db.Column(db.Boolean, nullable=True)


    
    work_experience = db.Column(db.String(500), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    country_name = db.Column(db.String(255), nullable=True)
    services_offered = db.Column(db.String(200), nullable=True)
    extra_services = db.Column(db.String(200), nullable=True)
    certifications = db.Column(db.String(200), nullable=True)
    other_documents = db.Column(db.String(500), nullable=True)
    limitations = db.Column(db.String(200), nullable=True)
    preferred_areas = db.Column(db.String(200), nullable=True)
    preferred_shifts = db.Column(db.String(100), nullable=True)
    holiday_work = db.Column(db.String(10), nullable=True)
    separate_zone = db.Column(db.String(100), nullable=True)
    need_helper = db.Column(db.String(10), nullable=True)
    bring_accompanying = db.Column(db.String(100), nullable=True)
    patient_accompanying_at_home = db.Column(db.String(10), nullable=True)
    comments = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FormData {self.name} {self.last_name}>'

def create_db(app):
    with app.app_context():
        db.create_all()
