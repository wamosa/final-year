from sqlalchemy.orm import joinedload
from models import Patient, HealthStatus

def fetch_patient_data(patient_id):
    # Fetch patient data from the database
    patient = Patient.query.filter_by(id=patient_id).first()
    
    # Fetch associated health status records
    health_status = HealthStatus.query.filter_by(patient_id=patient_id).all()

    # Return the data in a structured format
    return {
        "name": patient.name,
        "age": patient.age,
        "health_status": [
            {
                 # Assuming 'date' is a field you want to include in the report
                "age": hs.age,
                "sex": hs.sex,
                "chest_pain_type": hs.chest_pain_type,
                "bp": hs.bp,
                "cholesterol": hs.cholesterol,
                "max_heart_rate": hs.max_heart_rate,
                "fasting_blood_sugar": hs.fasting_blood_sugar,
                "resting_ecg": hs.resting_ecg,
                "exercise_angina": hs.exercise_angina,
                "oldpeak": hs.oldpeak,
                "st_slope": hs.st_slope,
            } for hs in health_status
        ],
    }