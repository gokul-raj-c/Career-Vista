from flask import Flask, request, jsonify, render_template, redirect, url_for, render_template_string,session
from flask_cors import CORS
import bcrypt
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
app.secret_key = 'goookul'

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

if __name__ == '__main__':
    app.run(debug=True)
