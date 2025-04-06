from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from frontend.app import app, db

from models.db_models_4 import User, Account, Manager, ServiceStaff, Shift, TimeOff, Message, ClockRecord

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database dropped and recreated.")

    manager1 = User(employee_name="Alice Manager", user_type="Manager")
    manager2 = User(employee_name="Bob Manager", user_type="Manager")
    staff1 = User(employee_name="Charlie Staff", user_type="Service_Staff")
    staff2 = User(employee_name="Diana Staff", user_type="Service_Staff")
    staff3 = User(employee_name="Ethan Staff", user_type="Service_Staff")

    db.session.add_all([manager1, manager2, staff1, staff2, staff3])
    db.session.flush()

    accounts = [
    Account(email="alice@company.com", password=generate_password_hash("pass123", method='pbkdf2:sha256'), employee_id=manager1.employee_id),
    Account(email="bob@company.com", password=generate_password_hash("pass123", method='pbkdf2:sha256'), employee_id=manager2.employee_id),
    Account(email="charlie@company.com", password=generate_password_hash("pass123", method='pbkdf2:sha256'), employee_id=staff1.employee_id),
    Account(email="diana@company.com", password=generate_password_hash("pass123", method='pbkdf2:sha256'), employee_id=staff2.employee_id),
    Account(email="ethan@company.com", password=generate_password_hash("pass123", method='pbkdf2:sha256'), employee_id=staff3.employee_id),
]

    db.session.add_all(accounts)

    db.session.add_all([
        Manager(employee_id=manager1.employee_id),
        Manager(employee_id=manager2.employee_id),
        ServiceStaff(employee_id=staff1.employee_id),
        ServiceStaff(employee_id=staff2.employee_id),
        ServiceStaff(employee_id=staff3.employee_id),
    ])

    now = datetime.now()
    today = now.date()

    shift1 = Shift.createShift(
        shift_date=today,
        start_time=now,
        end_time=now + timedelta(hours=4),
        total_hours=4.0,
        employee_id=staff1.employee_id
    )

    shift2 = Shift.createShift(
        shift_date=today + timedelta(days=1),
        start_time=now,
        end_time=now + timedelta(hours=6),
        total_hours=6.0,
        employee_id=staff2.employee_id
    )

    time_off = TimeOff.createTimeOff(
        start_leave_date=today + timedelta(days=2),
        end_leave_date=today + timedelta(days=4),
        total_leave_hours=16.0,
        employee_id=staff3.employee_id
    )

    msg1 = Message(
        sender_id=staff1.employee_id,
        recipient_id=manager1.employee_id,
        message_text="Requesting time off",
        latest_date=today,
        latest_time=now
    )

    msg2 = Message(
        sender_id=manager1.employee_id,
        recipient_id=staff1.employee_id,
        message_text="Time off approved",
        latest_date=today,
        latest_time=now
    )

    db.session.add_all([msg1, msg2])

    log = ClockRecord(
        clockIN_time=now - timedelta(hours=4),
        clockOUT_time=now,
        total_staff_hours=4.0,
        employee_id=staff1.employee_id
    )
    shift3 = Shift.createShift(
        shift_date=today + timedelta(days=2),
        start_time=now.replace(hour=10, minute=0),
        end_time=now.replace(hour=18, minute=0),
        total_hours=8.0,
        employee_id=None
    )

    shift4 = Shift.createShift(
        shift_date=today + timedelta(days=3),
        start_time=now.replace(hour=14, minute=0),
        end_time=now.replace(hour=22, minute=0),
        total_hours=8.0,
        employee_id=None
    )

    db.session.add(log)
    db.session.commit()

    print("Database populated successfully.")
