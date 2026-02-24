
#import modules
from flask import Flask, request, jsonify, render_template, redirect, url_for, render_template_string,session,flash
from flask_cors import CORS
import bcrypt
import joblib
from pymongo import MongoClient
import pandas as pd
import joblib
from flask_mail import Mail, Message
import random

app = Flask(__name__)
CORS(app)
app.secret_key = 'goookul'


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "teamgarage4web@gmail.com"    
app.config['MAIL_PASSWORD'] = "tptnqdqdzmojldoe"        
app.config['MAIL_DEFAULT_SENDER'] = "your_email@gmail.com"

mail = Mail(app)


#models 
from models.academic_model import predict_result_academic
from models.careerpath_model import predict_result_career
from models.stream_model import predict_result_stream
from models.jobrole_model import predict_job_role

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


@app.route('/forgotpassword')
def forgotpassword():
    return render_template('./forgotpassword/forgotpass.html')


@app.route('/sendotp', methods=['GET', 'POST'])
def sendotp():
    if request.method == 'POST':
        email = request.form.get('email')

        #Check if email exists in DB
        user = users_collection.find_one({"email": email})
        if not user:
            return render_template_string("""
                <script>
                    alert("Email is not registered!");
                    window.location.href = "{{ url_for('forgotpassword') }}";
                </script>
            """)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP & email in session
        session['otp'] = otp
        session['email'] = email

        # Send OTP email
        try:
            msg = Message("Your OTP Code", recipients=[email])
            msg.body = f"""
Hello,

We received a request to reset your account password.  
To proceed, please use the One Time Password (OTP) provided below:

Your OTP: {otp}

This OTP is valid for 5 minutes only.  
Do not share this code with anyone. If you did not request a password reset, please ignore this email or contact our support team immediately.

Thank you,  
CareerVista
"""
            mail.send(msg)
            return render_template_string("""
                <script>
                    alert("OTP has been sent to your registered email!");
                    window.location.href = "{{ url_for('enterotp') }}";
                </script>
            """)
        except Exception as e:
            print("Error sending email:", e)
            return render_template_string("""
                <script>
                    alert("Could not send OTP. Please try again later.");
                    window.location.href = "{{ url_for('forgotpassword') }}";
                </script>
            """)

    return render_template('./forgotpassword/forgotpass.html')


@app.route('/enterotp')
def enterotp():
    return render_template('./forgotpassword/verifyotp.html')

    
@app.route('/verifyotp', methods=['GET', 'POST'])
def verifyotp():
    if request.method == 'POST':
        entered_otp = request.form.get('OTP')

        # OTP Match
        if 'otp' in session and entered_otp == session['otp']:
            return """
                <script>
                    alert("OTP Verified Successfully!");
                    window.location.href = '/newpassword';
                </script>
            """
        else:
            return """
                <script>
                    alert("Invalid OTP! Please try again.");
                    window.location.href = '/forgotpassword';
                </script>
            """

    return render_template('./forgotpassword/verifyotp.html')



@app.route('/newpassword')
def newpassword():
    return render_template('./forgotpassword/newpassword.html')

@app.route('/setnewpassword', methods=['GET', 'POST'])
def setnewpassword():
    if request.method == 'POST':
        newpass = request.form.get('newpass')
        confirmpass = request.form.get('confirmpass')

        # Password mismatch
        if newpass != confirmpass:
            return """
                <script>
                    alert("Passwords do not match!");
                    window.location.href = '/newpassword';
                </script>
            """

        # Session expired
        if 'email' not in session:
            return """
                <script>
                    alert("Session expired. Please try again.");
                    window.location.href = '/forgotpassword';
                </script>
            """

        email = session['email']

        # Hash new password
        hashed_pw = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt())

        # Update MongoDB
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_pw}}
        )

        if result.modified_count > 0:
            message = "Password updated successfully! You can now login."
        else:
            message = "No changes made or user not found."

        # Clear sensitive session data
        session.pop('otp', None)
        session.pop('email', None)

        # Show alert and redirect to signin
        return f"""
            <script>
                alert("{message}");
                window.location.href = '/signin';
            </script>
        """

    return render_template('./forgotpassword/newpassword.html')



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





@app.route('/careerpath-prediction', methods=['GET', 'POST'])
def careerpath_model_prediction():
    email = session['email']
    user = users_collection.find_one({'email': email})
    name = user.get('name', email.split('@')[0].capitalize())

    if request.method == 'POST':
        try:
            stream = int(request.form['streamSelect'])
            learning_style = int(request.form['learningStyle'])
            certification = int(request.form['certifications'])
            

            # Map streams to relevant subjects
            stream_subjects = {
            0: ['Math', 'Physics', 'Chemistry', 'Computer_Science', 'English'],  # science_cs
            3: ['Biology', 'Physics', 'Chemistry', 'Math', 'English'],           # science_bio
            4: ['Biology', 'Physics', 'Chemistry', 'Computer_Science', 'English'], # science_bioip
            2: ['Accountancy', 'Economics', 'Business_Studies', 'Math', 'English'], # commerce
            1: ['History', 'Political_Science', 'Economics', 'Psychology', 'English'] # humanities
            }

            # Collect subject scores for selected stream
            subject_scores = {}
            for subject in stream_subjects.get(stream, []):
                value = request.form.get(subject)
                subject_scores[subject] = float(value) if value else 0

            val_dict = {
            "stream": stream,
            "learning_style": learning_style,
            "certification": certification,
            **subject_scores
            }


            # Make prediction
            prediction = predict_result_career(val_dict)

            return render_template('./user/careerpath_result.html', predicted_value=prediction,email=email, name=name)

        except Exception as e:
            import traceback
            print("ERROR:", e)
            traceback.print_exc()
            flash(f"Error: {str(e)}")
            return redirect(url_for('careerpath'))

    return render_template('careerpath.html')



@app.route('/stream-prediction', methods=['GET', 'POST'])
def stream_model_prediction():
    email = session['email']
    user = users_collection.find_one({'email': email})
    name = user.get('name', email.split('@')[0].capitalize())

    if request.method == 'POST':
        try:
            # Collect form data
            mathMarks = float(request.form['mathMarks'])
            scienceMarks = float(request.form['scienceMarks'])
            englishMarks = float(request.form['englishMarks'])
            socialScienceMarks = float(request.form['socialScienceMarks'])
            itMarks = float(request.form['itMarks'])
            learningStyle = int(request.form['learningStyle'])
            careerInclination = int(request.form['careerInclination'])
            

            # Create DataFrame for prediction
            val_df = [
                mathMarks, scienceMarks,englishMarks, socialScienceMarks, itMarks,
                learningStyle, careerInclination
            ]

            # Make prediction
            prediction = predict_result_stream(val_df)  # Get single value

            return render_template('./user/streamselection_result.html', predicted_stream=prediction,email=email, name=name)

        except Exception as e:
            import traceback
            print("ERROR:", e)
            traceback.print_exc()
            flash(f"Error: {str(e)}")
            return redirect(url_for('streamselection'))

    return render_template('streamselection.html')


@app.route('/jobrole-recommendation', methods=['GET', 'POST'])
def job_role_recommendation():
    email = session['email']
    user = users_collection.find_one({'email': email})
    name = user.get('name', email.split('@')[0].capitalize())

    if request.method == 'POST':
        try:
            # Collect form data
            databaseFundamentals = float(request.form['databaseFundamentals'])
            ComputerArchitecture = float(request.form['ComputerArchitecture'])
            ComputingSystems = float(request.form['ComputingSystems'])
            CyberSecurity = float(request.form['CyberSecurity'])
            Networking = float(request.form['Networking'])
            SoftwareDevelopment = float(request.form['SoftwareDevelopment'])
            ProgrammingSkills = float(request.form['ProgrammingSkills'])
            ProjectManagement = float(request.form['ProjectManagement'])
            ComputerFundamentals = float(request.form['ComputerFundamentals'])
            TechnicalCommunication = float(request.form['TechnicalCommunication'])
            AIMLRating = float(request.form['AIMLRating'])
            SoftwareEngineering = float(request.form['SoftwareEngineering'])
            BusinessAnalysis = float(request.form['BusinessAnalysis'])
            Communicationskills = float(request.form['Communicationskills'])
            DataScience = float(request.form['DataScience'])
            Troubleshootingskills = float(request.form['Troubleshootingskills'])
            GraphicsDesigning = float(request.form['GraphicsDesigning'])
            
            

            # Create DataFrame for prediction
            val_df = [
                databaseFundamentals,ComputerArchitecture,ComputingSystems,CyberSecurity, Networking,
                SoftwareDevelopment, ProgrammingSkills,ProjectManagement,ComputerFundamentals,TechnicalCommunication,
                AIMLRating,SoftwareEngineering,BusinessAnalysis,Communicationskills,DataScience,Troubleshootingskills,GraphicsDesigning

            ]

            # Make prediction
            prediction = predict_job_role(val_df)  # Get single value

            return render_template('./user/jobrole_result.html', predicted_jobrole=prediction,email=email, name=name)

        except Exception as e:
            import traceback
            print("ERROR:", e)
            traceback.print_exc()
            flash(f"Error: {str(e)}")
            return redirect(url_for('jobrole'))

    return render_template('jobrole.html')



if __name__ == '__main__':
    app.run(debug=True)
