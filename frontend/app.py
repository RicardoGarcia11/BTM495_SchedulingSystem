import os
import sys
from datetime import datetime, timedelta, time
from flask import Flask, request, redirect, url_for, render_template, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db_models_4 import db, User, Account, Shift, Schedule, Request, Message, TimeOff, ClockRecord, Availability

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "password"

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True) 
db_path = os.path.join(basedir, 'instance', 'scheduling_system.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database initialized!")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        account = Account.query.filter_by(email=email).first()

    
        if account and account.check_password(password):
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        employee_name = request.form["employee_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        user_type = request.form["user_type"]

        
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for("signup"))

        
        existing_account = Account.query.filter_by(email=email).first()
        if existing_account:
            flash("Email already registered. Please use a different email.", "danger")
            return redirect(url_for("signup"))

        try:
            
            new_user = User(employee_name=employee_name, user_type=user_type)
            db.session.add(new_user)
            db.session.flush() 
           


            new_account = Account(email=email, employee_id=new_user.employee_id)
            new_account.set_password(password)
            db.session.add(new_account)

            print(f"Creating account for: {email}, {employee_name}, type: {user_type}")
            db.session.commit()
            print(" Registration saved to database.")


            session['logged_in'] = True
            session['user_type'] = user_type
            session['user_id'] = new_user.employee_id
            session['user_name'] = new_user.employee_name

            flash(f"Welcome, {new_user.employee_name}! Your account was created successfully.", "success")

            
            if user_type == "Manager":
                return redirect(url_for("manager_dashboard"))
            else:
                return redirect(url_for("staff_dashboard"))

        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {str(e)}")
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for("signup"))

    return redirect(url_for("signup"))





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

@app.route("/manager_createschedule", methods=["GET", "POST"])
def manager_createschedule():
    if 'logged_in' in session and session.get('user_type') == 'Manager':
        if request.method == "POST":
            import json

            schedule_data = json.loads(request.form["schedule_data"])
            print("Schedule Submitted:", schedule_data)

            start_date = datetime.today().date()
            day_map = [start_date + timedelta(days=i) for i in range(7)]

            total_hours = len(schedule_data) * 8  
            schedule = Schedule.createSchedule(
                start_date=start_date,
                end_date=start_date + timedelta(days=6),
                total_hours=total_hours,
                manager_id=session['user_id']
            )
            db.session.add(schedule)

            for item in schedule_data:
                emp_id = int(item["employee_id"])
                shift_date = day_map[int(item["day_index"])]

                shift = Shift(
                    employee_id=emp_id,
                    shift_date=shift_date,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    total_hours=8
                )

                db.session.add(shift)
                schedule.shifts.append(shift)

            db.session.commit()

        
            return redirect(url_for("manager_createschedule", success="1"))

    
        staff_list = User.query.filter_by(user_type="Service_Staff").order_by(User.employee_id).all()

        
        if request.args.get("success") == "1":
            flash("Weekly schedule created successfully!", "success")
            return render_template("manager_createschedule.html", staff_list=staff_list, success_redirect=True)

        return render_template("manager_createschedule.html", staff_list=staff_list)

    return redirect(url_for("manager_login"))



@app.route("/manager_messages", methods=["GET"])
def manager_messages():
    if 'logged_in' not in session or session.get('user_type') != 'Manager':
        return redirect(url_for('login'))

    return render_template("manager_messages.html")

@app.route('/manager_reports')
def manager_reports():
    return render_template('manager_reports.html')

@app.route('/manager_requests')
def manager_requests():
    return render_template('manager_requests.html')


@app.route("/staff_dashboard")
def staff_dashboard():
    if 'logged_in' in session and session.get('user_type') == 'Service_Staff':
        return render_template("staff_dashboard.html")
    else:
        return redirect(url_for('login'))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home_page.html")

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
def staff_createavailability():
    if "logged_in" not in session or session.get("user_type") != "Service_Staff":
        flash("You must be logged in as Service Staff to access this page.", "warning")
        return redirect(url_for("login"))

    employee_id = session.get("user_id")

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received."}), 400

            print("Received staff_createavailability data:", data)

            Availability.query.filter_by(employee_id=employee_id).delete()

            for day_index, details in data.items():
                for shift in details["shifts"]:
                    availability = Availability(
                        employee_id=employee_id,
                        day_index=int(day_index),
                        shift_type=shift
                    )
                    db.session.add(availability)

            db.session.commit()
            return jsonify({"message": "Availability submitted successfully!"}), 200

        except Exception as e:
            print("Error handling POST request:", e)
            db.session.rollback()
            return jsonify({"error": "Something went wrong."}), 500

    existing_availability = Availability.query.filter_by(employee_id=employee_id).order_by(Availability.day_index).all()
    
    return render_template("staff_createavailability.html", availability=existing_availability)


@app.route("/manager_report_detail")
def manager_report_detail():
    section = request.args.get("section", "Unknown Section")
    label = request.args.get("label", "Unknown Report")
    return render_template("manager_report_detail.html", section=section, label=label)

@app.route("/manager_viewstaffavailability")
def manager_viewstaffavailability():
    if 'logged_in' not in session or session.get('user_type') != 'Manager':
        return redirect(url_for("login"))

    availability_records = db.session.query(
        Availability.employee_id,
        User.employee_name,
        Availability.day_index,
        Availability.shift_type
    ).join(User, Availability.employee_id == User.employee_id).order_by(Availability.employee_id, Availability.day_index).all()

    return render_template("manager_viewstaffavailability.html", records=availability_records)


@app.route("/clear_availability", methods=["POST"])
def clear_availability():
    if "logged_in" not in session or session.get("user_type") != "Service_Staff":
        return jsonify({"error": "Unauthorized"}), 401

    employee_id = session.get("user_id")
    try:
        Availability.query.filter_by(employee_id=employee_id).delete()
        db.session.commit()
        return jsonify({"message": "Availability cleared successfully."}), 200
    except Exception as e:
        print("Error clearing availability:", e)
        db.session.rollback()
        return jsonify({"error": "Failed to clear availability."}), 500

def start_app():
    app.run(debug=True)

if __name__ == "__main__":
    start_app()
