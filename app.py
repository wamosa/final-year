from flask import Flask, send_file,render_template, request, redirect, url_for, session, flash
import joblib
from io import BytesIO
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate
from models import db, Doctor ,HealthStatus, Patient 
from utils import fetch_patient_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to maintain user sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/heart_db'  # Updated with password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications

# Initialize the SQLAlchemy instance with the Flask app
db.init_app(app)  # After creating the Flask app
# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Place your migrate initialization here

with app.app_context():
    db.create_all()
    print("Tables created successfully.")

# Load your trained model from Google Colab
model = joblib.load('model/model (1).pkl')

# Simulate users for role-based login
users = {
    'admin': {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
    'assistant': {'username': 'assistant', 'password': 'assistant123', 'role': 'assistant'}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if it's an admin, doctor, or assistant
    user = Doctor.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = user.username
        session['role'] = 'doctor'
        return redirect(url_for('doctor_dashboard'))

    admin_user = users.get(username)
    if admin_user and admin_user['password'] == password:
        session['username'] = username
        session['role'] = admin_user['role']
        return redirect(url_for(f"{admin_user['role']}_dashboard"))

    flash("Invalid credentials. Please try again.", "danger")
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    query = request.args.get('query', '')
    if query:
        doctors = Doctor.query.filter(Doctor.name.ilike(f'%{query}%')).all()
    else:
        doctors = Doctor.query.all()

    return render_template('admin.html', doctors=doctors)

# Route to add a new doctor
@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if session.get('role') != 'admin':  # Check if the user is an admin
        return redirect(url_for('index'))  # Redirect if not admin

    name = request.form.get('name')  # Get the doctor's name from the form
    specialization = request.form.get('specialization')  # Get the doctor's specialization
    username = request.form.get('username')  # Get the doctor's username
    password = request.form.get('password')  # Get the doctor's password

    # Create a new doctor instance
    new_doctor = Doctor(name=name, specialization=specialization, username=username, password=password)

    # Add the new doctor to the session and commit to the database
    db.session.add(new_doctor)
    db.session.commit()

    flash('Doctor added successfully!', 'success')  # Flash a success message
    return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

# Route to delete a doctor
@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    doctor = Doctor.query.get(doctor_id)
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor removed successfully!', 'success')
    else:
        flash('Doctor not found.', 'danger')

    return redirect(url_for('admin_dashboard'))
# route to generate reports
@app.route('/generate_pdf_report', methods=['POST'])
def generate_pdf_report():
    patient_name= request.form.get('patient_name')
    # Fetch patient data by name (assuming names are unique or using a query to get the first match)
    patient = Patient.query.filter_by(name=patient_name).first()

    if not patient:
        # Handle the case where the patient name is not found
        return "Patient not found", 404
    
    # Fetch health status data
    patient_data = fetch_patient_data(patient.id)
    
    

    # Create a PDF report
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, f"Patient Report")
    p.drawString(100, 730, f"Name: {patient_data['name']}")
    p.drawString(100, 710, f"Age: {patient_data['age']}")
    
    # Add health status information
    p.drawString(100, 690, "Health Status:")
    y_position = 670
    for status in patient_data['health_status']:
        # Add each health status attribute to the PDF
        p.drawString(100, y_position, f"Age: {status['age']}, Sex: {status['sex']}")
        y_position -= 20
        p.drawString(100, y_position, f"Chest Pain Type: {status['chest_pain_type']}, BP: {status['bp']}")
        y_position -= 20
        p.drawString(100, y_position, f"Cholesterol: {status['cholesterol']}, Max Heart Rate: {status['max_heart_rate']}")
        y_position -= 20
        p.drawString(100, y_position, f"Fasting Blood Sugar: {status['fasting_blood_sugar']}, Resting ECG: {status['resting_ecg']}")
        y_position -= 20
        p.drawString(100, y_position, f"Exercise Angina: {status['exercise_angina']}, Oldpeak: {status['oldpeak']}")
        y_position -= 20
        p.drawString(100, y_position, f"ST Slope: {status['st_slope']}")
        y_position -= 30  # Add some space between records

        # Break to the next page if needed
        if y_position < 50:
            p.showPage()
            y_position = 750

    # Finalize the PDF
    p.showPage()   
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"patient_report_{patient_data['name']}.pdf")

@app.route('/generate_form')
def generate_form():
    return render_template('report_form.html')


@app.route('/doctor', methods=['GET', 'POST'])
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        # Create and add the new patient
        new_patient = Patient(name=name, age=age, gender=gender)
        db.session.add(new_patient)
        db.session.commit()

        flash('Patient added successfully!', 'success')
        return redirect(url_for('input_features'))  # Redirect to input features after adding a patient
    patients = Patient.query.all()  # Fetch all patients with records
    return render_template('doctor.html', patients=patients)

@app.route('/assistant')
def assistant_dashboard():
    if session.get('role') == 'assistant':
        return render_template('assistant.html')
    return redirect(url_for('index'))
@app.route('/results')
def results():
    # Retrieve the prediction result from session
    prediction = session.get('prediction')

    if prediction is None:
        flash('No prediction available. Please enter the patient data.', 'warning')
        return redirect(url_for('input_features'))

    # Map the prediction result to a meaningful message
    result_message = "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected"

    # Render the results.html template with the prediction message
    return render_template('results.html', result=result_message)


# Route for input features form
@app.route('/input', methods=['GET', 'POST'])
def input_features():
    patients = Patient.query.all()  # Fetch all patients

    if request.method == 'POST':
        patient_id = request.form['patient_id']  # Capture selected patient ID
        age = request.form['age']  # Capture age input
        sex = request.form['sex']  # Capture sex input (0 for female, 1 for male)
        chest_pain_type = request.form['chest_pain_type']
        bp = request.form['bp']
        cholesterol = request.form['cholesterol']
        fasting_blood_sugar = request.form['fasting_blood_sugar']
        resting_ecg = request.form['resting_ecg']
        max_heart_rate = request.form['max_heart_rate']
        exercise_angina = request.form['exercise_angina']
        oldpeak = request.form['oldpeak']
        st_slope = request.form['st_slope']

        # Format input features for prediction
        features = [[
            int(age), int(sex),int(chest_pain_type), int(bp), int(cholesterol),
            int(fasting_blood_sugar), int(resting_ecg), int(max_heart_rate),
            int(exercise_angina), float(oldpeak), int(st_slope)
        ]]
        prediction = model.predict(features)[0]  # Predict health status
        # Store the prediction in the session
        session['prediction'] = int(prediction)

        # Optionally, you can save the health status to the database here
        health_status_record = HealthStatus(
            patient_id=patient_id,
            age=int(age),  # Store age
            sex=int(sex),  # Store sex (0 or 1)
        
            chest_pain_type=int(chest_pain_type),
            bp=int(bp),
            cholesterol=int(cholesterol),
            fasting_blood_sugar=bool(int(fasting_blood_sugar)),
            resting_ecg=int(resting_ecg),
            max_heart_rate=int(max_heart_rate),
            exercise_angina=bool(int(exercise_angina)),
            oldpeak=float(oldpeak),
            st_slope=int(st_slope)
        )
        db.session.add(health_status_record)
        db.session.commit()

        flash('Prediction saved successfully!', 'success')
        return redirect(url_for('results'))

    return render_template('input.html', patients=patients)

        

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
