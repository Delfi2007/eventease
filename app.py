from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv 
import google.generativeai as genai 

# Load environment variables from .env file
load_dotenv()

# --- Firebase Initialization ---
try:
    # Get Firebase credentials JSON string from environment variable
    firebase_config_json = os.getenv("FIREBASE_CONFIG_JSON")

    if not firebase_config_json:
        raise ValueError("FIREBASE_CONFIG_JSON environment variable not set.")

    # Load JSON string into a Python dictionary
    cred_dict = json.loads(firebase_config_json)

    # Initialize Firebase Admin SDK with credentials from dictionary
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully from environment variable.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit()

# --- Flask App Setup ---
app = Flask(__name__)
# IMPORTANT: Change this for production! Use a strong, random key.
app.secret_key = 'your_super_secret_key_here' # For example: os.urandom(24)

# Configure Gemini API
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('models/gemini-2.0-flash') # This line still needs to be adjusted later
    print("Gemini AI initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini AI: {e}")
    gemini_model = None

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
        # As discussed, for this MVP, we are simplifying login verification
        # using the Admin SDK to check if a user with the email exists.
        # A real app would use the Firebase Client SDK for password validation
        # and token exchange for server-side session management.
        user_record = auth.get_user_by_email(email)
        # In a real scenario, you'd also verify the password here securely
        # if this was a purely server-side auth, but Firebase Admin SDK
        # does not expose password verification.
        return user_record, None
    except auth.AuthError as e:
        return None, "Invalid email or password." # Generic message for security
    except Exception as e:
        return None, str(e)


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')


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

@app.route('/manager/post_job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session.get('user_type') != 'manager':
        flash('Please login as an Event Manager to post a job.', 'danger')
        return redirect(url_for('manager_login_register'))

    if request.method == 'POST':
        job_title = request.form['job_title']
        description = request.form['description']
        required_staff_count = request.form['required_staff_count']
        job_date = request.form['job_date']
        job_time = request.form['job_time']
        location = request.form['location']
        pay_rate = request.form['pay_rate']
        category = request.form['category']

        # Basic validation
        if not all([job_title, description, required_staff_count, job_date, job_time, location, pay_rate, category]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('post_job'))

        try:
            # Convert staff count to integer
            required_staff_count = int(required_staff_count)
        except ValueError:
            flash('Required Staff Count must be a number.', 'danger')
            return redirect(url_for('post_job'))

        try:
            # Save job to Firestore
            job_data = {
                'manager_id': session['user_id'],
                'manager_email': session['user_email'],
                'job_title': job_title,
                'description': description,
                'required_staff_count': required_staff_count,
                'job_date': job_date,
                'job_time': job_time,
                'location': location,
                'pay_rate': pay_rate,
                'category': category,
                'status': 'active', # Initial status
                'posted_at': firestore.SERVER_TIMESTAMP
            }
            db.collection('jobs').add(job_data)
            flash('Job posted successfully!', 'success')
            return redirect(url_for('manager_dashboard'))
        except Exception as e:
            flash(f'Error posting job: {e}', 'danger')

    return render_template('post_job.html')

@app.route('/manager/my_jobs')
def manager_my_jobs():
    if 'user_id' not in session or session.get('user_type') != 'manager':
        flash('Please login as an Event Manager to view your jobs.', 'danger')
        return redirect(url_for('manager_login_register'))

    manager_id = session['user_id']
    jobs_ref = db.collection('jobs').where('manager_id', '==', manager_id).order_by('posted_at', direction=firestore.Query.DESCENDING)
    my_jobs = []
    for doc in jobs_ref.stream():
        job_data = doc.to_dict()
        job_data['id'] = doc.id # Store the document ID
        my_jobs.append(job_data)

    return render_template('manager_my_jobs.html', my_jobs=my_jobs, user_email=session['user_email'])

@app.route('/manager/job/<job_id>/applications')
def view_job_applications(job_id):
    if 'user_id' not in session or session.get('user_type') != 'manager':
        flash('Please login as an Event Manager to view applications.', 'danger')
        return redirect(url_for('manager_login_register'))

    # Verify that the job belongs to the logged-in manager
    job_doc = db.collection('jobs').document(job_id).get()
    if not job_doc.exists or job_doc.to_dict().get('manager_id') != session['user_id']:
        flash('You are not authorized to view applications for this job.', 'danger')
        return redirect(url_for('manager_my_jobs')) # Redirect back to my jobs list

    job_title = job_doc.to_dict().get('job_title', 'Unknown Job')

    applications_ref = db.collection('applications').where('job_id', '==', job_id).order_by('applied_at', direction=firestore.Query.ASCENDING)
    applications = []
    for doc in applications_ref.stream():
        app_data = doc.to_dict()
        app_data['id'] = doc.id # Store the application ID
        applications.append(app_data)

    return render_template('manager_applications.html',
                           job_title=job_title,
                           applications=applications,
                           job_id=job_id,
                           user_email=session['user_email'])

@app.route('/manager/application/<application_id>/<action>')
def accept_reject_application(application_id, action):
    if 'user_id' not in session or session.get('user_type') != 'manager':
        flash('Please login as an Event Manager to manage applications.', 'danger')
        return redirect(url_for('manager_login_register'))

    if action not in ['accept', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('manager_dashboard')) # Or redirect to a specific error page

    try:
        app_ref = db.collection('applications').document(application_id)
        application_doc = app_ref.get()

        if not application_doc.exists:
            flash('Application not found.', 'danger')
            return redirect(url_for('manager_my_jobs'))

        app_data = application_doc.to_dict()
        job_id = app_data.get('job_id')

        # Security Check: Ensure the manager owns this job
        job_doc = db.collection('jobs').document(job_id).get()
        if not job_doc.exists or job_doc.to_dict().get('manager_id') != session['user_id']:
            flash('You are not authorized to manage this application.', 'danger')
            return redirect(url_for('manager_my_jobs'))

        # Update application status
        app_ref.update({'status': action}) # 'accept' or 'reject'

        flash(f'Application {action}ed successfully!', 'success')
        return redirect(url_for('view_job_applications', job_id=job_id))

    except Exception as e:
        flash(f'Error processing application: {e}', 'danger')
        # Try to redirect back to the applications page if job_id is known
        if 'job_id' in locals(): # Check if job_id was successfully retrieved earlier
            return redirect(url_for('view_job_applications', job_id=job_id))
        else:
            return redirect(url_for('manager_my_jobs'))

@app.route('/manager/generate_job_description', methods=['POST'])
def generate_job_description():
    if 'user_id' not in session or session.get('user_type') != 'manager':
        return jsonify({'error': 'Unauthorized'}), 401

    job_title = request.json.get('job_title')
    category = request.json.get('category')

    if not job_title or not category:
        return jsonify({'error': 'Job title and category are required.'}), 400

    if not gemini_model: # Check if Gemini was initialized
        return jsonify({'error': 'Gemini AI not available. Please check server logs.'}), 500

    try:
        prompt = f"Write a brief (2-3 sentences), engaging, professional job description for a '{category}' position titled '{job_title}'. Focus on attracting suitable candidates."

        # Using generate_content for the actual API call
        response = gemini_model.generate_content(prompt)

        # Access the text from the response
        generated_text = response.text

        return jsonify({'description': generated_text})
    except Exception as e:
        print(f"Error generating description with Gemini AI: {e}")
        return jsonify({'error': f'Failed to generate description: {e}'}), 500

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


@app.route('/worker/jobs')
def view_jobs():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        flash('Please login as a Worker to view jobs.', 'danger')
        return redirect(url_for('worker_login_register'))

    jobs_ref = db.collection('jobs').where('status', '==', 'active').order_by('posted_at', direction=firestore.Query.DESCENDING)
    jobs = []
    for doc in jobs_ref.stream():
        job_data = doc.to_dict()
        job_data['id'] = doc.id # Store the document ID
        jobs.append(job_data)

    return render_template('worker_jobs.html', jobs=jobs, user_email=session['user_email'])


@app.route('/worker/apply_job/<job_id>')
def apply_job(job_id):
    if 'user_id' not in session or session.get('user_type') != 'worker':
        flash('Please login as a Worker to apply for jobs.', 'danger')
        return redirect(url_for('worker_login_register'))

    worker_id = session['user_id']
    worker_email = session['user_email']

    # Check if the worker has already applied for this job
    # Use a composite query for both job_id and worker_id
    existing_application_query = db.collection('applications') \
        .where('job_id', '==', job_id) \
        .where('worker_id', '==', worker_id) \
        .limit(1).get() # limit(1) makes it efficient as we only need to know if one exists

    if existing_application_query: # if the list is not empty
        for doc in existing_application_query: # iterate to check if any document exists
            flash('You have already applied for this job.', 'info')
            return redirect(url_for('view_jobs'))

    try:
        # Fetch job details to save with the application (optional but good for context)
        job_doc = db.collection('jobs').document(job_id).get()
        if not job_doc.exists:
            flash('Job not found.', 'danger')
            return redirect(url_for('view_jobs'))

        job_data = job_doc.to_dict()

        # Save application to Firestore
        application_data = {
            'job_id': job_id,
            'job_title': job_data.get('job_title'), # Store title for easier display later
            'manager_id': job_data.get('manager_id'),
            'worker_id': worker_id,
            'worker_email': worker_email,
            'status': 'pending', # Status: 'pending', 'accepted', 'rejected', 'withdrawn'
            'applied_at': firestore.SERVER_TIMESTAMP
        }
        db.collection('applications').add(application_data)
        flash('Your application has been submitted!', 'success')
        return redirect(url_for('view_jobs'))
    except Exception as e:
        flash(f'Error applying for job: {e}', 'danger')
        return redirect(url_for('view_jobs'))

@app.route('/worker/my_applications')
def worker_my_applications():
    if 'user_id' not in session or session.get('user_type') != 'worker':
        flash('Please login as a Worker to view your applications.', 'danger')
        return redirect(url_for('worker_login_register'))

    worker_id = session['user_id']
    applications_ref = db.collection('applications').where('worker_id', '==', worker_id).order_by('applied_at', direction=firestore.Query.DESCENDING)
    my_applications = []

    for app_doc in applications_ref.stream():
        app_data = app_doc.to_dict()
        app_data['id'] = app_doc.id # Store the application document ID

        # Fetch associated job details
        job_id = app_data.get('job_id')
        if job_id:
            job_doc = db.collection('jobs').document(job_id).get()
            if job_doc.exists:
                job_data = job_doc.to_dict()
                app_data['job_title'] = job_data.get('job_title', 'N/A')
                app_data['job_location'] = job_data.get('location', 'N/A')
                app_data['job_date'] = job_data.get('job_date', 'N/A')
            else:
                app_data['job_title'] = 'Job Not Found'
                app_data['job_location'] = 'N/A'
                app_data['job_date'] = 'N/A'
        else:
            app_data['job_title'] = 'N/A'
            app_data['job_location'] = 'N/A'
            app_data['job_date'] = 'N/A'

        my_applications.append(app_data)

    return render_template('worker_my_applications.html', my_applications=my_applications, user_email=session['user_email'])

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