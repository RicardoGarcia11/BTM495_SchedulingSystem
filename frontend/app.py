import os
import sys
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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
            user = User.query.get(account.employee_id)
            session['logged_in'] = True
            session['user_type'] = user.user_type
            session['user_id'] = user.employee_id
            session['user_name'] = user.employee_name

            if user.user_type == "Manager":
                return redirect(url_for("manager_dashboard"))
            else:
                return redirect(url_for("staff_dashboard"))

        return render_template("login_page.html", error="Invalid email or password.")
    
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
                error = "Access denied: This portal is for managers only."
                return render_template("manager_login.html", error=error)
        else:
            error = "Invalid login credentials."
            return render_template("manager_login.html", error=error)
    
    return render_template("manager_login.html")

@app.route("/manager_dashboard")
def manager_dashboard():
    if 'logged_in' in session and session.get('user_type') == 'Manager':
        return render_template("manager_dashboard.html")
    else:
        return redirect(url_for("manager_dashboard", success="Schedule created successfully!"))

@app.route("/create_schedule", methods=["GET", "POST"])
def create_schedule():
    if 'logged_in' in session and session.get('user_type') == 'Manager':
        if request.method == "POST":
            print(" FORM SUBMITTED")

            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
            shift_ids = request.form.getlist("shifts")
            total_hours = 0
            for shift_id in shift_ids:
                shift = Shift.query.get(int(shift_id))
                if shift:
                    total_hours += float(shift.total_hours)

            print(f"Start: {start_date}, End: {end_date}, Total Hours: {total_hours}, Shifts: {shift_ids}")

            
            schedule = Schedule.createSchedule(start_date, end_date, total_hours, session['user_id'])

            for shift_id in shift_ids:
                shift = Shift.query.get(int(shift_id))
                if shift:
                    schedule.shifts.append(shift)

            db.session.commit()
            return redirect(url_for("manager_dashboard"))

        
        shifts = Shift.query.filter(Shift.shift_date >= datetime.today().date()).all()
        return render_template("create_schedule.html", shifts=shifts)

    return redirect(url_for("manager_login"))

@app.route("/staff_dashboard")
def staff_dashboard():
    if 'logged_in' in session and session.get('user_type') == 'Service_Staff':
        return render_template("staff_dashboard.html")
    else:
        return redirect(url_for('login'))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/staff_loghours", methods=["GET", "POST"])
def staff_log_hours():
    if 'logged_in' not in session or session.get('user_type') != 'Service_Staff':
        if request.method == "GET":
            return redirect(url_for('login'))
        else:
            return jsonify({"error": "Unauthorized"}), 401

    employee_id = session.get("user_id")
    today = datetime.today().date()
    shift = Shift.query.filter_by(shift_date=today, employee_id=employee_id).first()

    if request.method == "GET":
        return render_template("staff_loghours.html", shift=shift)

   
    if not shift:
        return jsonify({"error": "You have no shift assigned today."}), 400

    try:
        data = request.get_json()
        action = data.get("action")
        now = datetime.now()

        if action == "clock_in":
            session["clock_in_time"] = now.isoformat()
            return jsonify({"message": f"Clocked in at {now.strftime('%I:%M %p')}"})

        elif action == "clock_out":
            clock_in_str = session.pop("clock_in_time", None)
            if not clock_in_str:
                return jsonify({"error": "You need to clock in first."}), 400

            clock_in_time = datetime.fromisoformat(clock_in_str)
            total_hours = round((now - clock_in_time).total_seconds() / 3600, 2)

            new_log = ClockRecord(
                clockIN_time=clock_in_time,
                clockOUT_time=now,
                total_staff_hours=total_hours,
                employee_id=employee_id
            )
            db.session.add(new_log)
            db.session.commit()

            return jsonify({
                "message": f"Clocked out at {now.strftime('%I:%M %p')}. Total hours: {total_hours:.2f}"
            })

        return jsonify({"error": "Invalid action"}), 400

    except Exception as e:
        print("Logging error:", str(e))
        return jsonify({"error": "Logging hours failed"}), 500
    
@app.route("/staff_shiftswap", methods=["GET", "POST"])
def staff_shiftswap():
    if 'logged_in' not in session or session.get('user_type') != 'Service_Staff':
        return redirect(url_for('login'))

    employee_id = session.get("user_id")
    today = datetime.today().date()

    my_shift = Shift.query.filter_by(shift_date=today, employee_id=employee_id).first()

    other_shifts = Shift.query.filter(
        Shift.shift_date == today,
        Shift.employee_id != employee_id,
        Shift.employee_id.isnot(None)
    ).all()

    other_users = []
    for shift in other_shifts:
        user = User.query.get(shift.employee_id)
        if user:
            other_users.append({
                "name": user.employee_name,
                "shift_id": shift.shift_id
            })

    return render_template(
        "staff_shiftswap.html",
        my_shift_id=my_shift.shift_id if my_shift else None,
        other_users=other_users
    )

@app.route("/staff_timeoff", methods=["GET", "POST"])
def staff_timeoff():
    if "logged_in" not in session or session.get("user_type") != "Service_Staff":
        flash("You must be logged in as Service Staff to access this page.", "warning")
        return redirect(url_for("login"))

    employee_id = session.get("user_id")

    if request.method == "POST":
        try:
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            reason = request.form.get("reason")
            file = request.files.get("upload")

            if not start_date or not end_date or not reason:
                flash("All required fields must be filled.", "danger")
                return redirect(url_for("staff_timeoff"))

            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            
            filename = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            time_off = TimeOff(
                start_leave_date=start_date,
                end_leave_date=end_date,
                total_leave_hours=0, 
                employee_id=employee_id,
                reason=reason,
                status="Pending",
                notes=None,
                file_name=filename
            )

            db.session.add(time_off)
            db.session.commit()

            flash("Time off request submitted successfully!", "success")
            return redirect(url_for("staff_timeoff"))

        except Exception as e:
            print("Error submitting request:", str(e))
            flash("There was a problem submitting your request. Try again.", "danger")
            return redirect(url_for("staff_timeoff"))

    
    previous_requests = TimeOff.query.filter_by(employee_id=employee_id).order_by(TimeOff.start_leave_date.desc()).all()

    return render_template("staff_timeoff.html", requests=previous_requests)

@app.route("/staff_messages", methods=["GET"])
def staff_messages():
    if 'logged_in' not in session or session.get('user_type') != 'Service_Staff':
        return redirect(url_for('login'))

    return render_template("staff_messages.html")

@app.route("/staff_createavailability", methods=["GET", "POST"])
def staff_availability():
    if "logged_in" not in session or session.get("user_type") != "Service_Staff":
        flash("You must be logged in as Service Staff to access this page.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received."}), 400
            print("Received availability data:", data)

            return jsonify({"message": "Availability submitted successfully!"}), 200

        except Exception as e:
            print("Error handling POST request:", e)
            return jsonify({"error": "Something went wrong."}), 500
    return render_template("staff_createavailability.html")





def start_app():
    app.run(debug=True)

if __name__ == "__main__":
    start_app()


