import os
import sys
from flask import Flask, request, redirect, url_for, render_template, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db_models_4 import db, User, Account, Shift, Schedule, Request, Message, TimeOff, ClockRecord


app = Flask(__name__, instance_relative_config=True)
app.secret_key = "password"

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'scheduling_system.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():
    db.create_all()
    print("Database initialized!")

@app.route("/")
def home():
    return render_template("home_page.html")

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
    return render_template("login_page.html")

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

@app.route("/request_time_off", methods=["POST"])
def request_time_off():
    data = request.get_json()
    try:
        time_off = TimeOff.createTimeOff(
            start_leave_date=data["start_leave_date"],
            end_leave_date=data["end_leave_date"],
            total_leave_hours=data["total_leave_hours"],
            employee_id=data["employee_id"]
        )
        return jsonify({"message": "Time off requested", "time_off_id": time_off.time_off_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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

@app.route("/signup")
def signup():
    return render_template("signup_page.html")

@app.route("/managerportal_page")
def manager_portal():
    return render_template("managerportal_page.html")

@app.route("/manager_login", methods=["GET", "POST"])
def manager_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        account = Account.query.filter_by(email=email).first()

        if account and check_password_hash(account.password, password):
            user = User.query.get(account.employee_id)
            if user and user.user_type == "Manager":
                session['logged_in'] = True
                session['user_type'] = 'Manager'
                session['user_id'] = user.employee_id
                session['user_name'] = user.employee_name
                return redirect(url_for("manager_dashboard"))
            else:
                return jsonify({"error": "Access denied: Not a manager"}), 403
        else:
            return jsonify({"error": "Invalid login credentials"}), 401
    return render_template("manager_login.html")

@app.route("/manager_dashboard")
def manager_dashboard():
    if 'logged_in' in session and session.get('user_type') == 'Manager':
        return render_template("manager_dashboard.html")
    else:
        return redirect(url_for('manager_login'))


def start_app():
    app.run(debug=True)

if __name__ == "__main__":
    start_app()

