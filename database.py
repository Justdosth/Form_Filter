from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from sqlalchemy import inspect
from collections import defaultdict
from pprint import pprint
import json


db = SQLAlchemy()


class User(db.Model):
    # اطلاعات هویتی
    national_code = db.Column(db.String(50), nullable=False, primary_key=True)

    full_name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_date_Persian = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    
    language_proficiency = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=False)  # "خانم" یا "آقا"
    marital_status = db.Column(db.String(10), nullable=False)
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
    driving_capability = db.Column(JSON, nullable=True)  # "بله" یا "خیر"
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
        return f'<User {self.full_name}>'


class Acquaintance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('user.national_code'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    relation = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Acquaintance {self.name} ({self.relation})>'


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('user.national_code'), nullable=False)

    title = db.Column(db.String(200), nullable=False)  # عنوان مدرک
    institution = db.Column(db.String(200), nullable=False)  # محل اخذ
    year = db.Column(db.String(10), nullable=True)  # سال اخذ

    def __repr__(self):
        return f'<Certificate {self.title} - {self.institution}>'


class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('user.national_code'), nullable=False)

    company_name = db.Column(db.String(200), nullable=False)  # نام شرکت یا کارفرما
    responsibilities = db.Column(db.Text, nullable=True)  # شرح مسئولیت‌ها
    reason_for_leaving = db.Column(db.Text, nullable=True)  # علت ترک کار
    company_contact = db.Column(db.String(50), nullable=True)  # شماره تماس شرکت

    def __repr__(self):
        return f'<WorkExperience {self.company_name}>'



def create_db(app):
    with app.app_context():
        db.create_all()


# Pre-defined lists for services, limitations, extra services, and equipment experience (can be fetched from DB or config)
# سرویس‌های قابل ارائه
SERVICES_LIST = [
    "امور نظافتی",
    "مراقبت از کودکان",
    "مراقبت از سالمندان",
    "مراقبت از بیماران",
    "مراقبت از معلولین"
]
# توانایی رانندگی
DRIVING_LIST = [
    "ماشین",
    "موتور",
    "وانت",
    "ماشین سنگین",
    "هیچ کدام"
]
# محدودیت‌ها
LIMITATIONS_LIST = [
    "پت",
    "محدودیت جسمی",
    "سفر خارج از شهر",
    "سفر خارج از کشور",
    "اقامت در محل",
    "تعطیل‌کاری",
    "اضافه‌کاری",
    "خدمت به آقا",
    "خدمت به خانم",
    "متراژ منزل",
    "نوع منزل",
    "حضور بستگان در منزل"
]

# سایر خدمات
EXTRA_SERVICES_LIST = [
    "نظافت منزل",
    "آشپزی",
    "مهمانداری",
    "امور آموزشی",
    "امور باغبانی",
    "خرید منزل",
    "تعمیرات",
    "کمک به بیماران خاص یا توانبخشی",
    "جابجایی افراد در منزل",
    "دادن دارو طبق تجویز پزشک",
    "انجام امور اداری خارج از منزل",
    "خدمات مربوط به پت",
    "همراهی خارج از منزل (مدرسه، پارک، مراکز درمانی و ...)"
]

# توانایی کار با تجهیزات
EQUIPMENT_EXPERIENCE_LIST = [
    "فشارسنج",
    "تب سنج",
    "دستگاه تست قندخون",
    "اکسی‌متر",
    "ساکشن",
    "سوند",
    "کولستومی",
    "دستگاه نوار قلب",
    "ویلچر",
    "بالابرهای بیمار",
    "تکنولوژی (گوشی هوشمند، دوربین، کامپیوتر و ...)"
]

COLUMN_LABELS = {
    "full_name": "نام و نام خانوادگی",
    "birth_date": "تاریخ تولد",
    "national_code": "کد ملی",
    "language_proficiency": "مهارت‌های زبانی",
    "gender": "جنسیت",
    "marital_status": "وضعیت تأهل",
    "special_care_companion": "نیاز به همراه مراقبتی خاص",
    "companion_details": "جزئیات همراه",
    "emergency_contact": "شماره تماس اضطراری",
    "landline": "تلفن ثابت",
    "mobile": "تلفن همراه",
    "residence_address": "آدرس محل سکونت",
    "services_offered": "سرویس‌های قابل ارائه:",
    "extra_services": "خدمات اضافی:",
    "driving_capability": "توانایی رانندگی:",
    "vehicle_details": "جزئیات وسیله نقلیه",
    "limitations": "محدودیت‌ها:",
    "home_size_restriction": "محدودیت متراژ خانه",
    "home_type_restriction": "نوع منزل",
    "relatives_presence": "حضور بستگان در منزل",
    "preferred_shifts": "شیفت‌های کاری",
    "equipment_experience": "توانایی کار با تجهیزات:",
    "desired_job": "شغل مورد نظر",
    "interviewer_comments": "توضیحات مصاحبه",
    
    "acquaintances_name": "نام و نام خانوادگی معرف",
    "acquaintances_relation": "نسبت با شما",
    "acquaintances_address": "آدرس محل سکونت فرد",
    "acquaintances_contact": "شماره تماس فرد",

    "certificate_title": "عنوان مدرک",
    "certificate_institution": "محل اخذ",
    "certificate_year": "سال اخذ",

    "work_experience_company_name": "نام شرکت (نام کارفرما)",
    "work_experience_responsibilities": "شرح مسئولیت‌ها",
    "work_experience_reason_for_leaving": "علت قطع همکاری",
    "work_experience_company_contact": "شماره تماس",
}


def generate_form_structure():
    form_structure = defaultdict(dict)
    persian_to_english_mapping = {}

    inspector = inspect(User)
    columns = inspector.columns  

    for column_name, column in columns.items():
        persian_label = COLUMN_LABELS.get(column_name, column_name)  # Get Persian label, default to column name
        persian_to_english_mapping[persian_label] = column_name
        
        if column_name in ['full_name', 'national_code', 'language_proficiency']:
            field_type = 'text'
            form_structure["اطلاعات هویتی"][persian_label] = field_type

        elif column_name in ['birth_date']:
            field_type = 'date'
            form_structure["اطلاعات هویتی"][persian_label] = field_type

        elif column_name in ['gender', 'marital_status']:
            field_type = 'select'
            form_structure["اطلاعات هویتی"][persian_label] = field_type
            if column_name == "gender":
                form_structure["اطلاعات هویتی"][persian_label + "_options"] = ["خانم", "آقا"]
            elif column_name == "marital_status":
                form_structure["اطلاعات هویتی"][persian_label + "_options"] = ["مجرد", "متاهل"]

        elif column_name in ['special_care_companion']:
            field_type = 'select'
            form_structure["اطلاعات هویتی"][persian_label] = field_type
            form_structure["اطلاعات هویتی"][persian_label + "_options"] = ["بله", "خیر"]

        elif column_name in ['companion_details']:
            field_type = 'textarea'
            form_structure["اطلاعات هویتی"][persian_label] = field_type

        elif column_name in ['emergency_contact', 'mobile', 'landline']:
            field_type = 'text'
            form_structure["اطلاعات دسترسی"][persian_label] = field_type
        
        elif column_name in ['residence_address']:
            field_type = 'textarea'
            form_structure["اطلاعات دسترسی"][persian_label] = field_type

        elif column_name in ['services_offered']:
            field_type = 'checkboxes'
            form_structure["سرویس‌های قابل ارائه"][persian_label] = field_type
            form_structure["سرویس‌های قابل ارائه"][persian_label + "_options"] = SERVICES_LIST

        elif column_name in ['extra_services']:
            field_type = 'checkboxes'
            form_structure["سایر خدمات"][persian_label] = field_type
            form_structure["سایر خدمات"][persian_label + "_options"] = EXTRA_SERVICES_LIST

        elif column_name in ['driving_capability']:
            field_type = 'checkboxes'
            form_structure["سرویس‌های قابل ارائه"][persian_label] = field_type
            form_structure["سرویس‌های قابل ارائه"][persian_label + "_options"] = DRIVING_LIST

        elif column_name in ['vehicle_details']:
            field_type = 'textarea'
            form_structure["سرویس‌های قابل ارائه"][persian_label] = field_type

        elif column_name in ['limitations']:
            field_type = 'checkboxes'
            form_structure["محدودیت‌ها"][persian_label] = field_type
            form_structure["محدودیت‌ها"][persian_label + "_options"] = LIMITATIONS_LIST

        elif column_name in ['home_size_restriction', 'home_type_restriction', 'relatives_presence']:
            field_type = 'textarea'
            form_structure["محدودیت‌ها"][persian_label] = field_type

        elif column_name in ['preferred_shifts']:
            field_type = 'text'
            form_structure["شیفت‌های کاری"][persian_label] = field_type

        elif column_name in ['equipment_experience']:
            field_type = 'checkboxes'
            form_structure["توانایی کار با تجهیزات"][persian_label] = field_type
            form_structure["توانایی کار با تجهیزات"][persian_label + "_options"] = EQUIPMENT_EXPERIENCE_LIST

        elif column_name in ['desired_job', 'interviewer_comments']:
            field_type = 'textarea'
            form_structure["شغل مورد نظر و توضیحات مصاحبه"][persian_label] = field_type
    
    # Add dynamic sections to mapping
    dynamic_sections = [
        ("acquaintances_name", "نام و نام خانوادگی معرف"),
        ("acquaintances_relation", "نسبت با شما"),
        ("acquaintances_address", "آدرس محل سکونت فرد"),
        ("acquaintances_contact", "شماره تماس فرد"),
        ("certificate_title", "عنوان مدرک"),
        ("certificate_institution", "محل اخذ"),
        ("certificate_year", "سال اخذ"),

        ("work_experience_company_name", "نام شرکت (نام کارفرما)"),
        ("work_experience_responsibilities", "شرح مسئولیت‌ها"),
        ("work_experience_reason_for_leaving", "علت قطع همکاری"),
        ("work_experience_company_contact", "شماره تماس")
    ]

    for english, persian in dynamic_sections:
        persian_to_english_mapping[persian] = english

    # Add dynamic Acquaintances Section (from the Acquaintance table)
    form_structure["آشنایان"] = []
    acquaintances = Acquaintance.query.all()  # Fetch all acquaintances
    for acquaintance in acquaintances:
        form_structure["آشنایان"].append({
            COLUMN_LABELS["acquaintances_name"]: acquaintance.name,
            COLUMN_LABELS["acquaintances_relation"]: acquaintance.relation,
            COLUMN_LABELS["acquaintances_address"]: acquaintance.address,
            COLUMN_LABELS["acquaintances_contact"]: acquaintance.contact
        })

    # Add dynamic Certificates Section (from the Certificate table)
    form_structure["مدارک"] = []
    certificates = Certificate.query.all()  # Fetch all certificates
    for certificate in certificates:
        form_structure["مدارک"].append({
            COLUMN_LABELS["certificate_title"]: certificate.title,
            COLUMN_LABELS["certificate_institution"]: certificate.institution,
            COLUMN_LABELS["certificate_year"]: certificate.year
        })

    # Add dynamic Work Experiences Section (from the WorkExperience table)
    form_structure["سوابق کاری"] = []
    work_experiences = WorkExperience.query.all()  # Fetch all work experiences
    for work in work_experiences:
        form_structure["سوابق کاری"].append({
            COLUMN_LABELS["work_experience_company_name"]: work.company_name,
            COLUMN_LABELS["work_experience_responsibilities"]: work.responsibilities,
            COLUMN_LABELS["work_experience_reason_for_leaving"]: work.reason_for_leaving,
            COLUMN_LABELS["work_experience_company_contact"]: work.company_contact
        })

    # Add empty row structure for adding new data to each dynamic section
    form_structure["آشنایان"].append({
        COLUMN_LABELS["acquaintances_name"]: '',
        COLUMN_LABELS["acquaintances_relation"]: '',
        COLUMN_LABELS["acquaintances_address"]: '',
        COLUMN_LABELS["acquaintances_contact"]: ''
    })

    form_structure["مدارک"].append({
        COLUMN_LABELS["certificate_title"]: '',
        COLUMN_LABELS["certificate_institution"]: '',
        COLUMN_LABELS["certificate_year"]: ''
    })

    form_structure["سوابق کاری"].append({
        COLUMN_LABELS["work_experience_company_name"]: '',
        COLUMN_LABELS["work_experience_responsibilities"]: '',
        COLUMN_LABELS["work_experience_reason_for_leaving"]: '',
        COLUMN_LABELS["work_experience_company_contact"]: ''
    })

    with open("form_structure_format.json", "w", encoding="utf-8") as f:
        json.dump(form_structure, f, indent=2, ensure_ascii=False)
    
    with open("persian_to_english_mapping.json", "w", encoding="utf-8") as f:
        json.dump(persian_to_english_mapping, f, indent=2, ensure_ascii=False)
    
    return form_structure, persian_to_english_mapping
