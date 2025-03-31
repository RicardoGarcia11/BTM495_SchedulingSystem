import os
import sys
from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Adjust the path to your project structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your existing models and database
from models.db_models_4 import db, User, Account, Shift, Schedule, Request, Message, TimeOff, ClockRecord

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup (matches your db_models_4.py)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///scheduling_system.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create the database tables automatically
with app.app_context():
    db.create_all()
    print("Database initialized!")

# Home page route
@app.route("/")
def home():
    return render_template("home_page.html")

# Login route (basic example)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        account = Account.query.filter_by(email=email).first()
        
        if account and check_password_hash(account.password, password):
            return redirect(url_for("home"))
        else:
            return jsonify({"error": "Invalid login credentials"}), 401
    else:
        return render_template("login.html")

# API route example: Create Shift
@app.route("/create_shift", methods=["POST"])
def create_shift():
    data = request.get_json()
    try:
        shift = Shift.createShift(
            shift_date=data["shift_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            total_hours=data["total_hours"],
            employee_id=data.get("employee_id")
        )
        return jsonify({"message": "Shift created", "shift_id": shift.shift_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API route example: Request Time Off
@app.route("/request_time_off", methods=["POST"])
def request_time_off():
    data = request.get_json()
    try:
        time_off = TimeOff.createTimeOff(
            start_leave_date=data["start_leave_date"],
            end_leave_date=data["end_leave_date"],
            total_leave_hours=data["total_leave_hours"]
        )
        return jsonify({"message": "Time off requested", "time_off_id": time_off.time_off_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API route example: Send Message
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    sender = User.query.get(data["sender_id"])
    if not sender:
        return jsonify({"error": "Sender not found"}), 404

    try:
        sender.sendMessage(recipient_id=data["recipient_id"], text_message=data["message_text"])
        return jsonify({"message": "Message sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Additional routes and APIs can be added here similarly...

# Run Flask application
if __name__ == "__main__":
    app.run(debug=True)
