import os
import sys
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import db from models/db_models.py
from models.db_models import db  


# Initialize Flask app
app = Flask(__name__)
app.secret_key = "hello"

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///scheduling.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)
 

# Define home page
@app.route("/")
def home():
    return render_template("home_page.html")

# Example: Redirect to home after login
@app.route("/login")
def user_login():
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        # Only create tables if they don’t exist
        db.create_all()
        print("Database initialized!")
    app.run(debug=True)