from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
# Update the connection string to use SQLite.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== Database Models ====================

class User(db.Model):
    __tablename__ = 'user'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('Manager', 'Service_Staff'), nullable=False)
    
    account = db.relationship('Account', back_populates='user', uselist=False)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient')

class Account(db.Model):
    __tablename__ = 'account'
    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), unique=True)
    
    user = db.relationship('User', back_populates='account')

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    latest_date = db.Column(db.Date, nullable=False)
    latest_time = db.Column(db.DateTime, nullable=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='messages_received')

class Manager(db.Model):
    __tablename__ = 'manager'
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), primary_key=True)

class ServiceStaff(db.Model):
    __tablename__ = 'service_staff'
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), primary_key=True)
    availability = db.Column(db.String(50), nullable=False)

class Shift(db.Model):
    __tablename__ = 'shift'
    shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shift_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_hours = db.Column(db.Numeric(5,2), nullable=False)
    shift_database = db.Column(db.Text)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'))

class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(10,2), nullable=False)

# Many-to-many relationship between Shift and ServiceStaff.
shift_servicestaff = db.Table('shift_servicestaff',
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('user.employee_id'), primary_key=True)
)

# Many-to-many relationship between Schedule and Shift.
schedule_shift = db.Table('schedule_shift',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.schedule_id'), primary_key=True),
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)
)

class ShiftSwap(db.Model):
    __tablename__ = 'shift_swap'
    swap_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requesting_staff = db.Column(db.String(255), nullable=False)
    receiving_staff = db.Column(db.String(255), nullable=False)
    original_shift = db.Column(db.String(255), nullable=False)
    requested_shift = db.Column(db.Integer, nullable=False)

class TimeOff(db.Model):
    __tablename__ = 'time_off'
    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.Numeric(5,2), nullable=False)

class ClockRecord(db.Model):
    __tablename__ = 'clock_record'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clockIN_time = db.Column(db.DateTime, nullable=False)
    clockOUT_time = db.Column(db.DateTime, nullable=False)
    total_staff_hours = db.Column(db.Numeric(5,2), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)

# ==================== Flask Endpoints ====================

@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    employee_name = data.get('employee_name')
    email = data.get('email')
    user_type = data.get('user_type')
    password = data.get('password')
    
    # Create a new user record.
    user = User(employee_name=employee_name, email=email, user_type=user_type)
    db.session.add(user)
    db.session.commit()
    
    # Create an account record.
    account = Account(email=email, password=password, employee_id=user.employee_id)
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': f'Account created for {employee_name}',
        'employee_id': user.employee_id
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    account = Account.query.filter_by(email=email, password=password).first()
    if account:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Login failed'}), 401

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    now = datetime.now()
    message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        latest_date=now.date(),
        latest_time=now
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message sent'})

@app.route('/assign_shift', methods=['POST'])
def assign_shift():
    data = request.get_json()
    shift_date = datetime.strptime(data.get('shift_date'), '%Y-%m-%d').date()
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%d %H:%M:%S')
    total_hours = data.get('total_hours')
    shift_database = data.get('shift_database')
    employee_id = data.get('employee_id')
    
    shift = Shift(
        shift_date=shift_date,
        start_time=start_time,
        end_time=end_time,
        total_hours=total_hours,
        shift_database=shift_database,
        employee_id=employee_id
    )
    db.session.add(shift)
    db.session.commit()
    return jsonify({
        'message': 'Shift assigned',
        'shift_id': shift.shift_id
    })

@app.route('/request_shift_swap', methods=['POST'])
def request_shift_swap():
    data = request.get_json()
    requesting_staff = data.get('requesting_staff')
    receiving_staff = data.get('receiving_staff')
    original_shift = data.get('original_shift')
    requested_shift = data.get('requested_shift')
    
    swap = ShiftSwap(
        requesting_staff=requesting_staff,
        receiving_staff=receiving_staff,
        original_shift=original_shift,
        requested_shift=requested_shift
    )
    db.session.add(swap)
    db.session.commit()
    return jsonify({
        'message': 'Shift swap requested',
        'swap_id': swap.swap_id
    })

@app.route('/create_schedule', methods=['POST'])
def create_schedule():
    data = request.get_json()
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    total_hours = data.get('total_hours')
    
    schedule = Schedule(
        start_date=start_date,
        end_date=end_date,
        total_hours=total_hours
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({
        'message': 'Schedule created',
        'schedule_id': schedule.schedule_id
    })

@app.route('/clock_in', methods=['POST'])
def clock_in():
    data = request.get_json()
    employee_id = data.get('employee_id')
    now = datetime.now()
    # Initially, set clockOUT_time equal to clockIN_time; will update at clock-out.
    clock_record = ClockRecord(
        clockIN_time=now,
        clockOUT_time=now,
        total_staff_hours=0,
        employee_id=employee_id
    )
    db.session.add(clock_record)
    db.session.commit()
    return jsonify({
        'message': f'Employee {employee_id} clocked in',
        'log_id': clock_record.log_id
    })

@app.route('/clock_out', methods=['POST'])
def clock_out():
    data = request.get_json()
    log_id = data.get('log_id')
    clock_record = ClockRecord.query.get(log_id)
    if clock_record:
        now = datetime.now()
        clock_record.clockOUT_time = now
        delta = now - clock_record.clockIN_time
        hours = delta.total_seconds() / 3600
        clock_record.total_staff_hours = hours
        db.session.commit()
        return jsonify({
            'message': f'Employee {clock_record.employee_id} clocked out',
            'total_hours': float(hours)
        })
    else:
        return jsonify({'message': 'Clock record not found'}), 404

@app.route('/request_time_off', methods=['POST'])
def request_time_off():
    data = request.get_json()
    employee_id = data.get('employee_id')
    start_leave_date = datetime.strptime(data.get('start_leave_date'), '%Y-%m-%d').date()
    end_leave_date = datetime.strptime(data.get('end_leave_date'), '%Y-%m-%d').date()
    total_leave_hours = data.get('total_leave_hours')
    
    time_off = TimeOff(
        start_leave_date=start_leave_date,
        end_leave_date=end_leave_date,
        total_leave_hours=total_leave_hours
    )
    db.session.add(time_off)
    db.session.commit()
    return jsonify({
        'message': f'Time off requested for employee {employee_id}',
        'time_off_id': time_off.time_off_id
    })


