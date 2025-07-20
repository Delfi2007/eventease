from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- Firebase Initialization ---
try:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit()

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # IMPORTANT: Change this for production!

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# --- Common Authentication Functions ---
def register_user(email, password, user_type):
    try:
        user = auth.create_user(email=email, password=password)
        # Store additional user info in Firestore
        db.collection('users').document(user.uid).set({
            'email': email,
            'user_type': user_type,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return user, None
    except Exception as e:
        return None, str(e)

def login_user(email, password):
    try:
        # Firebase Admin SDK doesn't directly log in users or handle passwords
        # We'll simulate login success by trying to get user by email and then
        # relying on frontend JavaScript (which we won't build in this MVP)
        # or implicitly trusting the credentials for our server-side auth check.
        # For this MVP, we will only check if user exists. Real login would use
        # Firebase Client SDK on frontend or more complex server-side token verification.
        user_record = auth.get_user_by_email(email)
        # For a real app, you would verify the password here too (e.g. via client-side SDK)
        # For server-side validation, we are simply confirming the user exists in Firebase Auth.
        # The password itself is not exposed or verifiable by the Admin SDK.
        return user_record, None
    except auth.AuthError as e:
        return None, "Invalid email or password." # Generic message for security
    except Exception as e:
        return None, str(e)


# --- Event Manager Routes ---
@app.route('/manager_login_register', methods=['GET', 'POST'])
def manager_login_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        action = request.form['action'] # 'register' or 'login'

        if action == 'register':
            user, error = register_user(email, password, 'manager')
            if user:
                flash('Manager account created successfully! Please login.', 'success')
                return redirect(url_for('manager_login_register')) # Redirect to login part
            else:
                flash(f'Registration failed: {error}', 'danger')
        elif action == 'login':
            user, error = login_user(email, password)
            if user:
                user_doc = db.collection('users').document(user.uid).get()
                if user_doc.exists and user_doc.to_dict().get('user_type') == 'manager':
                    session['user_id'] = user.uid
                    session['user_email'] = user.email
                    session['user_type'] = 'manager'
                    flash('Manager logged in successfully!', 'success')
                    return redirect(url_for('manager_dashboard'))
                else:
                    flash('Not an Event Manager account or user type mismatch.', 'danger')
            else:
                flash(f'Login failed: {error}', 'danger')

    return render_template('manager_login_register.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'manager':
        flash('Please login as an Event Manager to access this page.', 'danger')
        return redirect(url_for('manager_login_register'))
    return render_template('manager_dashboard.html', user_email=session['user_email'])


# --- Worker Routes ---
@app.route('/worker_login_register', methods=['GET', 'POST'])
def worker_login_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        action = request.form['action'] # 'register' or 'login'

        if action == 'register':
            user, error = register_user(email, password, 'worker')
            if user:
                flash('Worker account created successfully! Please login.', 'success')
                return redirect(url_for('worker_login_register')) # Redirect to login part
            else:
                flash(f'Registration failed: {error}', 'danger')
        elif action == 'login':
            user, error = login_user(email, password)
            if user:
                user_doc = db.collection('users').document(user.uid).get()
                if user_doc.exists and user_doc.to_dict().get('user_type') == 'worker':
                    session['user_id'] = user.uid
                    session['user_email'] = user.email
                    session['user_type'] = 'worker'
                    flash('Worker logged in successfully!', 'success')
                    return redirect(url_for('worker_dashboard'))
                else:
                    flash('Not a Worker account or user type mismatch.', 'danger')
            else:
                flash(f'Login failed: {error}', 'danger')

    return render_template('worker_login_register.html')


@app.route('/worker_dashboard')
def worker_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        flash('Please login as a Worker to access this page.', 'danger')
        return redirect(url_for('worker_login_register'))
    return render_template('worker_dashboard.html', user_email=session['user_email'])


# --- Logout Route (Common for both) ---
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_type', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)