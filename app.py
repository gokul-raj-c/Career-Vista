from flask import Flask, request, jsonify, render_template, redirect, url_for, render_template_string,session,flash
from flask_cors import CORS
import bcrypt
import joblib
from pymongo import MongoClient
import pandas as pd
import joblib


app = Flask(__name__)
CORS(app)
app.secret_key = 'goookul'

from models.academic_model import predict_result_academic


# MongoDB Atlas Connection
client = MongoClient("mongodb+srv://gokulrajc63:epzaHzvtaYnxf4re@todo.1czrgxx.mongodb.net/?retryWrites=true&w=majority&appName=todo")
db = client["career-vista"]
users_collection = db["registration"]

# Routes
@app.route('/')
def home():
    return render_template('./homepage/index.html')

@app.route('/signin')
def signin():
    return render_template('./signin/index.html')

@app.route('/signup')
def signup():
    return render_template('./signup/index.html')

@app.route('/user')
def user():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            name = user.get('name', email.split('@')[0].capitalize())  # fallback to username if name missing
            return render_template('./user/index.html', email=email, name=name)
    return redirect(url_for('signin'))

@app.route('/careerpath')
def careerpath():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            name = user.get('name', email.split('@')[0].capitalize())  # fallback to username if name missing
            return render_template('./user/careerpath.html', email=email, name=name)
    return redirect(url_for('signin'))

@app.route('/streamselection')
def streamselection():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            name = user.get('name', email.split('@')[0].capitalize())  # fallback to username if name missing
            return render_template('./user/streamselection.html', email=email, name=name)
    return redirect(url_for('signin'))

@app.route('/jobrole')
def jobrole():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            name = user.get('name', email.split('@')[0].capitalize())  # fallback to username if name missing
            return render_template('./user/jobrole.html', email=email, name=name)
    return redirect(url_for('signin'))

@app.route('/academic')
def academic():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            name = user.get('name', email.split('@')[0].capitalize())  # fallback to username if name missing
            return render_template('./user/academic.html', email=email, name=name)
    return redirect(url_for('signin'))
    
@app.route('/signout')
def signout():
    session.clear()
    return render_template_string("""
        <script>
            alert("You have been signed out successfully!");
            window.location.href = "{{ url_for('home') }}";
        </script>
    """)



@app.route('/userregistration', methods=['GET', 'POST'])
def userregistration():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return render_template_string("""
                <script>
                    alert("Account already exists!");
                    window.location.href = "{{ url_for('home') }}";
                </script>
            """)

        # Hash and store password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            "name": name,
            "contact": contact,
            "email": email,
            "password": hashed_pw
        })

        return render_template_string("""
            <script>
                alert("Account registered successfully!");
                window.location.href = "{{ url_for('signin') }}";
            </script>
        """)
    else:
        return render_template('./signup/index.html')
    
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({"email": email})

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                session['email'] = email
                return render_template_string("""
                    <script>
                        alert("Login successful!");
                        window.location.href = "{{ url_for('user') }}";
                    </script>
                """)
            else:
                return render_template_string("""
                    <script>
                        alert("Incorrect password!");
                        window.location.href = "{{ url_for('signin') }}";
                    </script>
                """)
        else:
            return render_template_string("""
                <script>
                    alert("Account not found!");
                    window.location.href = "{{ url_for('signup') }}";
                </script>
            """)
    else:
        return render_template('./signin/index.html')
    
@app.route('/academic-prediction', methods=['GET', 'POST'])
def academic_model_prediction():
    email = session['email']
    user = users_collection.find_one({'email': email})
    name = user.get('name', email.split('@')[0].capitalize())

    if request.method == 'POST':
        try:
            # Collect form data
            hours_studied = float(request.form['hours_studied'])
            attendance = float(request.form['attendance'])
            parental_involvement = int(request.form['parental_involvement'])
            online_resources = int(request.form['online_resources'])
            extra_caricular = int(request.form['extra_caricular'])
            sleep_hours = float(request.form['sleep_hours'])
            prev_scores = float(request.form['previous_score'])
            motivation_level = int(request.form['motivation_level'])
            internet_availability = int(request.form['internet_availability'])
            tutoring_sessions = float(request.form['tutoring_sessions'])
            family_income = int(request.form['family_income'])
            teacher_quality = int(request.form['teacher_quality'])
            school_type = int(request.form['school_type'])
            peer_influence = int(request.form['peer_influence'])
            learning_disability = int(request.form['learning_disabilitity'])
            parental_education = int(request.form['parental_education'])
            distance_from_home = int(request.form['distance_from_home'])
            gender = int(request.form['gender'])

            
            # Create DataFrame for prediction
            val_df = [
                hours_studied, attendance, parental_involvement, online_resources,
                extra_caricular, sleep_hours, prev_scores, motivation_level,
                internet_availability, tutoring_sessions, learning_disability, peer_influence,
                family_income, teacher_quality, school_type, parental_education,
                distance_from_home, gender
            ]

            # Make prediction
            prediction = predict_result_academic(val_df)[0]  # Get single value

            return render_template('./user/academic_result.html', predicted_score=prediction,email=email, name=name)

        except Exception as e:
            import traceback
            print("ERROR:", e)
            traceback.print_exc()
            flash(f"Error: {str(e)}")
            return redirect(url_for('academic'))

    return render_template('academic.html')




if __name__ == '__main__':
    app.run(debug=True)
