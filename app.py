from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- Firebase Initialization ---
# Load Firebase credentials from the JSON file
# Ensure 'firebase_credentials.json' is in your project root directory
try:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client() # Firestore database client
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # Exit or handle the error appropriately if Firebase cannot be initialized
    # For development, just print, but for production, this should be more robust.
    exit() # Exiting if credentials fail, crucial for app integrity

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # IMPORTANT: Change this for production!

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manager_login_register')
def manager_login_register():
    return render_template('manager_login_register.html')

@app.route('/worker_login_register')
def worker_login_register():
    return render_template('worker_login_register.html')


if __name__ == '__main__':
    app.run(debug=True)