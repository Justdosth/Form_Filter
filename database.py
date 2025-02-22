from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON

db = SQLAlchemy()


class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # اطلاعات هویتی
    full_name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    national_code = db.Column(db.String(50), nullable=False)
    language_proficiency = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=False)  # "خانم" یا "آقا"
    marital_status = db.Column(db.String(50), nullable=False)
    special_care_companion = db.Column(db.String(10), nullable=True)  # "بله" یا "خیر"
    companion_details = db.Column(db.Text, nullable=True)

    # اطلاعات دسترسی
    emergency_contact = db.Column(db.String(50), nullable=False)
    landline = db.Column(db.String(50), nullable=True)
    mobile = db.Column(db.String(50), nullable=False)
    residence_address = db.Column(db.String(255), nullable=True)

    # سرویس‌های قابل ارائه (Stored as a comma-separated string)
    services_offered = db.Column(JSON, nullable=True)  

    # سایر خدمات
    extra_services = db.Column(JSON, nullable=True)
    driving_capability = db.Column(db.String(10), nullable=True)  # "بله" یا "خیر"
    vehicle_details = db.Column(db.Text, nullable=True)

    # محدودیت‌ها
    limitations = db.Column(JSON, nullable=True)

    home_size_restriction = db.Column(db.String(255), nullable=True)
    home_type_restriction = db.Column(db.String(255), nullable=True)
    relatives_presence = db.Column(db.String(255), nullable=True)

    # شیفت‌های کاری
    preferred_shifts = db.Column(db.String(500), nullable=True)

    # توانایی کار با تجهیزات
    equipment_experience = db.Column(JSON, nullable=True)

    # شغل مورد نظر و توضیحات مصاحبه
    desired_job = db.Column(db.String(255), nullable=True)
    interviewer_comments = db.Column(db.Text, nullable=True)

    # Relationships with other tables
    acquaintances = db.relationship('Acquaintance', backref='form', lazy=True)
    certificates = db.relationship('Certificate', backref='form', lazy=True)
    work_experiences = db.relationship('WorkExperience', backref='form', lazy=True)

    def __repr__(self):
        return f'<FormData {self.full_name}>'


class Acquaintance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form_data.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    relation = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Acquaintance {self.name} ({self.relation})>'


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form_data.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)  # عنوان مدرک
    institution = db.Column(db.String(200), nullable=False)  # محل اخذ
    year = db.Column(db.String(10), nullable=True)  # سال اخذ

    def __repr__(self):
        return f'<Certificate {self.title} - {self.institution}>'


class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form_data.id'), nullable=False)

    company_name = db.Column(db.String(200), nullable=False)  # نام شرکت یا کارفرما
    responsibilities = db.Column(db.Text, nullable=True)  # شرح مسئولیت‌ها
    reason_for_leaving = db.Column(db.Text, nullable=True)  # علت ترک کار
    company_contact = db.Column(db.String(50), nullable=True)  # شماره تماس شرکت

    def __repr__(self):
        return f'<WorkExperience {self.company_name}>'



def create_db(app):
    with app.app_context():
        db.create_all()
