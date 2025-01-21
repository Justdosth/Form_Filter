from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Information about the person
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(10))
    salary = db.Column(db.Float)
    language_proficiency = db.Column(db.String(200))
    work_experience = db.Column(db.String(500))

    # Additional information
    address = db.Column(db.String(100))
    country_details = db.Column(db.String(255))
    services_offered = db.Column(db.String(200))
    extra_services = db.Column(db.String(200))
    certifications = db.Column(db.String(200))
    other_documents = db.Column(db.String(500))
    limitations = db.Column(db.String(200))

    # Service Preferences
    preferred_areas = db.Column(db.String(200))
    preferred_shifts = db.Column(db.String(100))
    holiday_work = db.Column(db.String(10))
    separate_zone = db.Column(db.String(100))
    need_helper = db.Column(db.String(10))
    bring_accompanying = db.Column(db.String(100))
    patient_accompanying_at_home = db.Column(db.String(10))
    comments = db.Column(db.Text)

    def __repr__(self):
        return f'<FormData {self.name} {self.last_name}>'

def create_db(app):
    with app.app_context():
        db.create_all()
