from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    specialization = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)  # Ensure it's unique
    password = db.Column(db.String(255))  # Consider hashing passwords for security

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    health_records = db.relationship('HealthStatus', backref='patient', lazy=True)

class HealthStatus(db.Model):
    __tablename__ = 'health_status'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)  # Add age column
    sex = db.Column(db.Integer, nullable=False)
    chest_pain_type = db.Column(db.Integer, nullable=False)
    bp = db.Column(db.Integer, nullable=False)
    cholesterol = db.Column(db.Integer, nullable=False)
    max_heart_rate = db.Column(db.Integer, nullable=False)
    fasting_blood_sugar = db.Column(db.Boolean, nullable=False)
    resting_ecg = db.Column(db.Integer, nullable=False)
    exercise_angina = db.Column(db.Boolean, nullable=False)
    oldpeak = db.Column(db.Float, nullable=False)
    st_slope = db.Column(db.Integer, nullable=False)
      