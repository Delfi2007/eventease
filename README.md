# EventEase

## Connecting Event Managers with Skilled Freelancers

EventEase is an innovative web application designed to streamline the event staffing process by providing a dedicated platform where event managers can efficiently find and manage staff, and freelancers can discover relevant job opportunities.

---

## ✨ Features

EventEase offers a range of features tailored for both event managers and workers:

### For Event Managers:
* **Job Posting:** Easily post detailed event job listings with requirements, dates, times, and pay rates.
* **Applicant Management:** View and manage applications for your posted jobs. Accept or reject candidates directly from your dashboard.
* **AI Job Description Generator:** (Powered by Gemini AI) Quickly generate engaging job description snippets based on job title and category, saving time and improving clarity.

### For Event Workers (Freelancers):
* **Job Discovery:** Browse active job postings from various event managers.
* **Easy Application:** Apply for jobs with a streamlined process.
* **Application Tracking:** Monitor the real-time status of your job applications (pending, accepted, rejected).

---

## 🚀 Live Demo

Experience EventEase live!
**Website:** https://eventease-jfw4.onrender.com

---

## 🛠️ Getting Started

Follow these steps to set up and run EventEase on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.8+** (Recommended)
* **pip** (Python package installer)
* **Git** (for cloning the repository)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/eventease.git](https://github.com/your-username/eventease.git)
    cd eventease
    ```
    *(Replace `your-username/eventease.git` with your actual GitHub repository URL)*

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

EventEase uses Firebase for backend services and Gemini AI for content generation. You'll need to set up credentials for both.

1.  **Firebase Credentials:**
    * Obtain your Firebase service account key (a `.json` file) from your Firebase project settings (Project settings -> Service accounts).
    * **Crucially, do NOT commit this file to Git.**
    * For **local development**, create a file named `.env` in the root of your project (same directory as `app.py`).
    * Add your entire Firebase service account JSON content as a single-line string to the `.env` file under a variable, e.g.:
        ```
        FIREBASE_CONFIG_JSON='{"type": "service_account", "project_id": "...", "private_key": "...", "client_email": "...", "token_uri": "...", ...}'
        ```
        * *(You can use the Python script from previous steps to convert your JSON file to a single line).*
    * For **deployment on Render**, you will set this `FIREBASE_CONFIG_JSON` as an environment variable directly in Render's dashboard.

2.  **Gemini AI API Key:**
    * Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).
    * **Do NOT commit this key to Git.**
    * For **local development**, add it to your `.env` file:
        ```
        GEMINI_API_KEY="your_gemini_api_key_here"
        ```
    * For **deployment on Render**, you will set `GEMINI_API_KEY` as an environment variable directly in Render's dashboard.

3.  **Flask Secret Key:**
    * For **local development**, add a strong, random secret key to your `.env` file:
        ```
        FLASK_SECRET_KEY="your_strong_random_secret_key_here"
        ```
        * *(You can generate one using `import os; os.urandom(24)` in a Python console).*
    * For **deployment on Render**, you will set `FLASK_SECRET_KEY` as an environment variable directly in Render's dashboard.

### Running the Application

Once configured, you can run the Flask application:

```bash
flask run
```

The application will typically run on http://127.0.0.1:5000

###🤝 Contributing
We welcome contributions to EventEase! Please refer to our CONTRIBUTING.md guide for detailed instructions on how to set up your development environment, propose changes, and submit pull requests.

###📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

###✉️ Contact
For questions, feedback, or collaboration inquiries, please reach out to: mukeshkumar.cse24@gmail.com
Whatsapp grp: Mail to the above email id.
