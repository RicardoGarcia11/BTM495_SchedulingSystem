import os
import sys
from datetime import datetime, timedelta, time
from flask import Flask, request, redirect, url_for, render_template, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
from calendar import monthrange
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.db_models_4 import db, User, Account, Shift, Schedule, Request, Message, TimeOff, ClockRecord, Availability, Manager, ServiceStaff, schedule_shift

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "password"

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True) 
db_path = os.path.join(basedir, 'instance', 'scheduling_system.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
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
        user_type = request.form["user_type"].strip()

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for("signup"))

        if user_type not in ["Manager", "Service_Staff"]:
            flash("Invalid user type selected.", "danger")
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

            if user_type == "Manager":
                db.session.add(Manager(employee_id=new_user.employee_id))
                print("Manager entry added for:", new_user.employee_id)
            elif user_type == "Service_Staff":
                db.session.add(ServiceStaff(employee_id=new_user.employee_id))
                print("ServiceStaff entry added for:", new_user.employee_id)

            db.session.commit()

            session["logged_in"] = True
            session["user_type"] = user_type
            session["user_id"] = new_user.employee_id
            session["user_name"] = new_user.employee_name

            flash(f"Welcome, {new_user.employee_name}! Your account was created successfully.", "success")
            return redirect(url_for("manager_dashboard") if user_type == "Manager" else url_for("staff_dashboard"))

        except Exception as e:
            db.session.rollback()
            print("Registration error:", str(e))
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
            try:
                import json
                schedule_data = json.loads(request.form["schedule_data"])

                start_date = datetime.today().date()
                day_map = [start_date + timedelta(days=i) for i in range(7)]
                total_hours = len(schedule_data) * 8

                new_schedule = Schedule(
                    start_date=start_date,
                    end_date=start_date + timedelta(days=6),
                    total_hours=total_hours,
                    manager_id=session['user_id']
                )
                db.session.add(new_schedule)
                db.session.flush()

                for entry in schedule_data:
                    emp_id = int(entry["employee_id"])
                    shift_date = day_map[int(entry["day_index"])]

                    shift = Shift(
                        employee_id=emp_id,
                        shift_date=shift_date,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        total_hours=8
                    )
                    db.session.add(shift)
                    db.session.flush()

                    db.session.execute(schedule_shift.insert().values(
                        schedule_id=new_schedule.schedule_id,
                        shift_id=shift.shift_id
                    ))

                db.session.commit()
                return redirect(url_for("manager_createschedule", success="1"))

            except Exception as e:
                db.session.rollback()
                flash("Failed to create schedule. Try again.", "danger")
                return redirect(url_for("manager_createschedule"))

        staff_list = User.query.filter_by(user_type="Service_Staff").order_by(User.employee_id).all()

        if request.args.get("success") == "1":
            flash("Weekly schedule created successfully.", "success")
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
    if 'logged_in' not in session or session.get('user_type') != 'Manager':
        return redirect(url_for('login'))

    
    TargetShift = db.aliased(Shift)
    TargetUser = db.aliased(User)

    
    swap_requests = db.session.query(
        Request.request_id,
        Request.status,
        Request.request_date,
        User.employee_name.label("requester_name"),
        TargetUser.employee_name.label("swap_with_name")
    ).join(User, Request.employee_id == User.employee_id
    ).outerjoin(TargetShift, Request.target_shift_id == TargetShift.shift_id
    ).outerjoin(TargetUser, TargetShift.employee_id == TargetUser.employee_id
    ).filter(
        Request.request_type == 'Shift Swap',
        Request.status == 'Pending'
    ).all()

    
    time_off_requests = db.session.query(
        Request.request_id,
        Request.status,
        Request.request_date,
        User.employee_name.label("requester_name"),
        TimeOff.start_leave_date,
        TimeOff.end_leave_date,
        TimeOff.reason
    ).join(User, Request.employee_id == User.employee_id
    ).join(TimeOff, Request.time_off_id == TimeOff.time_off_id
    ).filter(
        Request.request_type == 'Time Off',
        Request.status == 'Pending'
    ).all()

    return render_template(
        'manager_requests.html',
        swap_requests=swap_requests,
        time_off_requests=time_off_requests
    )


@app.route("/staff_dashboard")
def staff_dashboard():
    if 'logged_in' not in session or session.get('user_type') != 'Service_Staff':
        return redirect(url_for('login'))

    employee_id = session.get("user_id")
    today = datetime.today()
    month_start = today.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)

    shifts = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.shift_date >= month_start,
        Shift.shift_date < next_month
    ).all()

    return render_template(
        "staff_dashboard.html",
        month_name=today.strftime("%B"),
        year=today.year,
        shifts=shifts,
        now=today,
        next_month=next_month,
        datetime=datetime
    )
   
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
    
@app.route("/staff_shiftswap", methods=["GET"])
def staff_shiftswap():
    if 'logged_in' not in session or session.get('user_type') != 'Service_Staff':
        return redirect(url_for('login'))

    employee_id = session.get("user_id")
    today = datetime.today()
    today_date = today.date()

    
    selected_month = int(request.args.get("month", today.month))
    selected_year = int(request.args.get("year", today.year))

    
    month_start = datetime(selected_year, selected_month, 1).date()
    num_days = monthrange(selected_year, selected_month)[1]
    next_month = (month_start + timedelta(days=num_days)).replace(day=1)
    first_weekday = month_start.weekday()


    shifts_in_month = Shift.query.filter(
        Shift.shift_date >= month_start,
        Shift.shift_date < next_month
    ).all()

    shift_map = {}
    my_shift_id = None

    for shift in shifts_in_month:
        user = User.query.get(shift.employee_id)
        if user:
            shift_map[shift.shift_date.day] = {
                "shift_id": shift.shift_id,
                "name": user.employee_name,
                "start_time": shift.start_time.strftime("%H:%M"),
                "end_time": shift.end_time.strftime("%H:%M"),
                "employee_id": user.employee_id
            }
        if shift.employee_id == employee_id and my_shift_id is None:
            my_shift_id = shift.shift_id

    
    prev_month = selected_month - 1 if selected_month > 1 else 12
    prev_year = selected_year if selected_month > 1 else selected_year - 1
    next_month_val = selected_month + 1 if selected_month < 12 else 1
    next_year = selected_year if selected_month < 12 else selected_year + 1

    return render_template(
        "staff_shiftswap.html",
        month_name=month_start.strftime("%B"),
        year=selected_year,
        today=today.day,
        num_days=num_days,
        first_weekday=first_weekday,
        shift_map=shift_map,
        current_user_id=employee_id,
        current_month=(selected_month == today.month and selected_year == today.year),
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month_val,
        next_year=next_year,
        my_shift_id=my_shift_id
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

            # Create TimeOff entry
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
            db.session.flush()  # So we can get time_off.time_off_id

            # Create linked Request entry
            request_entry = Request(
                employee_id=employee_id,
                request_type="Time Off",
                request_date=datetime.utcnow(),
                time_off_id=time_off.time_off_id,  # ✅ Link to TimeOff
                status="Pending"
            )

            db.session.add(request_entry)
            db.session.commit()

            flash("Time off request submitted successfully!", "success")
            return redirect(url_for("staff_timeoff"))

        except Exception as e:
            print("Error submitting request:", str(e))
            db.session.rollback()
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
    
@app.route("/request_swap", methods=["POST"])
def request_swap():
    data = request.get_json()
    print("Received data:", data)

    requested_shift_id = data.get("requested_shift_id")
    target_shift_id = data.get("target_shift_id")
    employee_id = session.get("user_id")

    if requested_shift_id is None or target_shift_id is None or employee_id is None:
        return jsonify({"message": "Missing shift or user information."}), 400

    existing_request = Request.query.filter_by(
        employee_id=employee_id,
        requested_shift_id=requested_shift_id,
        target_shift_id=target_shift_id,
        request_type="Shift Swap"
    ).first()

    if existing_request:
        return jsonify({"message": "You have already requested this shift swap."}), 400

    try:
        new_request = Request(
            employee_id=employee_id,
            request_type="Shift Swap",
            request_date=datetime.utcnow(),
            requested_shift_id=requested_shift_id,
            target_shift_id=target_shift_id,
            status="Pending"
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "message": "Swap request submitted successfully!"
        }), 200

    except Exception as e:
        print("Error processing swap request:", e)
        return jsonify({"message": "Internal server error."}), 500
    
@app.route("/update_request_status", methods=["POST"])
def update_request_status():
    data = request.get_json()
    request_id = data.get("request_id")
    new_status = data.get("status")

    req = Request.query.get(request_id)
    if not req:
        return jsonify({"message": "Request not found."}), 404

    req.status = new_status
    db.session.commit()

    return jsonify({"message": f"Request {request_id} marked as {new_status}."}), 200

    
def start_app():
    app.run(debug=True)

if __name__ == "__main__":
    start_app()
