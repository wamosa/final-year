from flask import Flask, render_template, request, redirect, url_for, session , flash
import joblib
from flask_sqlalchemy import SQLAlchemy
from models import db, Doctor  

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to maintain user sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/heart_db'
 # Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications

# Initialize the SQLAlchemy instance with the Flask app
db.init_app(app)  # After creating the Flask app

with app.app_context():
    db.create_all()
    print("Tables created successfully.")


# Load your trained model from Google Colab
model = joblib.load('model\model (1).pkl')

# Simulate users for role-based login
users = {
    'admin': {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
    'doctor': {'username': 'doctor', 'password': 'doctor123', 'role': 'doctor'},
    'assistant': {'username': 'assistant', 'password': 'assistant123', 'role': 'assistant'}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['role'] = user['role']
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user['role'] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif user['role'] == 'assistant':
            return redirect(url_for('assistant_dashboard'))
    return "Invalid credentials, please try again."

@app.route('/admin')
def admin_dashboard():
    if session.get('role') == 'admin':
        return render_template('admin.html')  # Render the admin dashboard template
    return redirect(url_for('index'))  # Redirect if not admin
# Route to add a new doctor
@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if session.get('role') == 'admin':  # Check if the user is an admin
        name = request.form.get('name')# Get the doctor's name from the form
        specialization = request.form.get('specialization')  # Get the doctor's specialization
        
        # Create a new doctor instance
        new_doctor = Doctor(name=name, specialization=specialization)
        
        # Add the new doctor to the session and commit to the database
        db.session.add(new_doctor)
        db.session.commit()

        flash('Doctor added successfully!', 'success')  # Flash a success message
        return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
    return redirect(url_for('index'))  # Redirect if not admin

@app.route('/doctor')
def doctor_dashboard():
    if session.get('role') == 'doctor':
        return render_template('doctor.html')
    return redirect(url_for('index'))

@app.route('/assistant')
def assistant_dashboard():
    if session.get('role') == 'assistant':
        return render_template('assistant.html')
    return redirect(url_for('index'))

# Route for input features form
@app.route('/input', methods=['GET', 'POST'])
def input_features():
    if request.method == 'POST':
        # Capture all features from the form
        age = request.form['age']
        sex = request.form['sex']
        chest_pain_type = request.form['chest_pain_type']
        bp = request.form['bp']
        cholesterol = request.form['cholesterol']
        fasting_blood_sugar = request.form['fasting_blood_sugar']
        resting_ecg = request.form['resting_ecg']
        max_heart_rate = request.form['max_heart_rate']
        exercise_angina = request.form['exercise_angina']
        oldpeak = request.form['oldpeak']
        st_slope = request.form['st_slope']
        
        # Model expects input in a certain format; adjust as needed
        features = [[
            int(age), int(sex), int(chest_pain_type), int(bp), int(cholesterol),
            int(fasting_blood_sugar), int(resting_ecg), int(max_heart_rate), 
            int(exercise_angina), float(oldpeak), int(st_slope)
        ]]
        
        prediction = model.predict(features)  # Use the model to predict based on input
        return render_template('results.html', result=prediction)
    return render_template('input.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
