"""This file defines the SQLAlchemy models for the Flask application.
It maps database tables to Python classes, enabling ORM-based interactions
instead of raw SQL queries.

Each class represents a table in the PostgreSQL database, and relationships
between tables are managed using SQLAlchemy's ORM features.

Tables Implemented:
- Employee: Stores employee details.
- Account: Links employee accounts with login credentials.
- Shift: Represents work shifts.
- Schedule: Defines weekly schedules.
- ShiftEmployee: Many-to-many relationship between employees and shifts.
- ScheduleShift: Many-to-many relationship between schedules and shifts.
- Message: Stores messages exchanged between employees.
- ShiftSwap: Tracks requests for swapping shifts between employees.
- TimeOff: Manages employee time-off requests.

Usage:
- This file should be imported into the main Flask app.
- The database connection should be initialized in `app.py` using `db.init_app(app)`.
- Run `db.create_all()` to generate tables in the database.

"""


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employee'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float)
    role = db.Column(db.String(50), nullable=False)
    
    account = db.relationship('Account', back_populates='employee', uselist=False)
    shifts = db.relationship('ShiftEmployee', back_populates='employee')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient')
    shift_swaps_requested = db.relationship('ShiftSwap', foreign_keys='ShiftSwap.requesting_emp', back_populates='requesting_employee')
    shift_swaps_received = db.relationship('ShiftSwap', foreign_keys='ShiftSwap.receiving_emp', back_populates='receiving_employee')
    time_off_requests = db.relationship('TimeOff', back_populates='employee')

class Account(db.Model):
    __tablename__ = 'account'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    
    employee = db.relationship('Employee', back_populates='account')

class Shift(db.Model):
    __tablename__ = 'shift'
    
    shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    total_hours = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Integer, nullable=False)

class ShiftEmployee(db.Model):
    __tablename__ = 'shift_employee'
    
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), primary_key=True)
    
    shift = db.relationship('Shift', back_populates='employees')
    employee = db.relationship('Employee', back_populates='shifts')

class ScheduleShift(db.Model):
    __tablename__ = 'schedule_shift'
    
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)

class Message(db.Model):
    __tablename__ = 'message'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latest_date = db.Column(db.Date, nullable=False)
    latest_time = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    
    sender = db.relationship('Employee', foreign_keys=[sender_id], back_populates='messages_sent')
    recipient = db.relationship('Employee', foreign_keys=[recipient_id], back_populates='messages_received')

class ShiftSwap(db.Model):
    __tablename__ = 'shift_swap'
    
    swap_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requesting_emp = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    receiving_emp = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    original_shift = db.Column(db.Integer, db.ForeignKey('shift.shift_id'), nullable=False)
    requested_shift = db.Column(db.Integer, db.ForeignKey('shift.shift_id'), nullable=False)
    
    requesting_employee = db.relationship('Employee', foreign_keys=[requesting_emp], back_populates='shift_swaps_requested')
    receiving_employee = db.relationship('Employee', foreign_keys=[receiving_emp], back_populates='shift_swaps_received')

class TimeOff(db.Model):
    __tablename__ = 'time_off'
    
    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.Integer, nullable=False)
    approve_request = db.Column(db.Boolean, default=False)
    decline_request = db.Column(db.Boolean, default=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    
    employee = db.relationship('Employee', back_populates='time_off_requests')