# Contributing to EventEase

We welcome and appreciate your contributions to EventEase! By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🚀 Get Started

Before you start, make sure you have followed the setup instructions in the [README.md](README.md) to get the app running locally.

## 🤔 How to Contribute

We encourage you to contribute in various ways, including:

* **Reporting Bugs:** If you find a bug, please open an issue.
* **Suggesting Features:** Have an idea for a new feature? Let us know by opening an issue.
* **Submitting Code Changes:** Fix bugs, implement new features, or improve existing ones.

---

## 🐛 Reporting Bugs

If you encounter a bug, please help us by:

1.  **Checking Existing Issues:** Search our [issues](https://github.com/mukesh-dev-git/eventease/issues) to see if the bug has already been reported.
2.  **Opening a New Issue:** If not, please open a new issue using the "Bug report" template.
3.  **Provide Details:**
    * **Steps to reproduce:** Clear, detailed steps to recreate the bug.
    * **Expected behavior:** What you expected to happen.
    * **Actual behavior:** What actually happened.
    * **Screenshots/Logs:** Attach any relevant screenshots or error logs.
    * **Environment:** Your operating system, browser, Python version, etc.

---

## ✨ Suggesting Features

We love new ideas! To suggest a feature:

1.  **Check Existing Issues:** Search our [issues](https://github.com/mukesh-dev-git/eventease/issues) to see if the feature has already been suggested.
2.  **Open a New Issue:** If not, open a new issue using the "Feature request" template.
3.  **Describe Your Idea:**
    * **Problem:** Explain the problem this feature would solve.
    * **Proposed Solution:** Describe your idea for the feature.
    * **Why it's important:** Explain the benefits or value this feature would bring.

---

## 💻 Submitting Code Changes (Pull Request Workflow)

We use the standard GitHub "Fork & Pull Request" workflow.

1.  **Fork the Repository:**
    Go to the main [EventEase repository](https://github.com/your-username/eventease) and click the "Fork" button in the top right corner. This creates a copy of the repository under your GitHub account.

2.  **Clone Your Fork Locally:**
    ```bash
    git clone [https://github.com/mukesh-dev-git/eventease.git](https://github.com/mukesh-dev-git/eventease.git)
    cd eventease
    ```

3.  **Add the Upstream Remote:**
    Set up a remote to the original EventEase repository to pull updates.
    ```bash
    git remote add upstream [https://github.com/mukesh-dev-git/eventease.git](https://github.com/mukesh-dev-git/eventease.git)
    ```

4.  **Sync with the Upstream (Recommended before starting work):**
    Always pull the latest changes from the original `develop` or `main` branch before creating your feature branch.
    ```bash
    git checkout develop # Or 'main', depending on the active development branch
    git pull upstream develop
    ```

5.  **Create a New Branch:**
    For each new feature or bug fix, create a new branch.
    ```bash
    git checkout -b feature/your-feature-name # For new features
    # OR
    git checkout -b bugfix/issue-number # For bug fixes, referencing the issue number
    ```

6.  **Make Your Changes & Commit:**
    * Write your code and make your changes.
    * Ensure your code adheres to our [Coding Style Guidelines](#-coding-style-guidelines).
    * Commit your changes with clear, descriptive commit messages.
        ```bash
        git add .
        git commit -m "feat: Briefly describe your feature"
        # OR
        git commit -m "fix: Briefly describe your bug fix for #issue-number"
        ```

7.  **Test Your Changes Locally:**
    **Crucially, before pushing, run the app locally (`flask run`) and thoroughly test your changes** to ensure they work as expected and haven't introduced new bugs.

8.  **Push to Your Fork:**
    ```bash
    git push origin your-branch-name
    ```

9.  **Open a Pull Request (PR):**
    * Go to your forked repository on GitHub.
    * GitHub will usually prompt you to create a Pull Request from your new branch to the `develop` (or `main`) branch of the original EventEase repository.
    * Fill out the Pull Request template with a clear summary of your changes, how to test them, and reference any related issues (e.g., `Closes #123`).

---


## ✅ Testing

If you've implemented new features or fixed bugs, please ensure that relevant functionality works as expected after your changes. If you write new tests, ensure they pass.

To run the Flask application locally for testing:
```bash
flask run
