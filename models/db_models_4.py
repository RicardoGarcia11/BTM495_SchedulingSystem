from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduling_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== Models and Methods ==========

class User(db.Model):
    __tablename__ = 'user'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('Manager', 'Service_Staff'), nullable=False)

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)

    def register(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def login(email, password):
        return Account.query.filter_by(email=email, password=password).first()

    def sendMessage(self, recipient_id):
        message = Message(
            sender_id=self.employee_id,
            recipient_id=recipient_id,
            latest_date=date.today(),
            latest_time=datetime.now()
        )
        db.session.add(message)
        db.session.commit()

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    latest_date = db.Column(db.Date, nullable=False)
    latest_time = db.Column(db.DateTime, nullable=False)

class Account(db.Model):
    __tablename__ = 'account'
    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), unique=True)

    def getID(self):
        return self.employee_id

    def verifyLogin(self, password):
        return self.password == password

    def verifyUserType(self):
        user = User.query.get(self.employee_id)
        return user.user_type if user else None

class Manager(db.Model):
    __tablename__ = 'manager'
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), primary_key=True)

    def assignShift(self, shift):
        db.session.add(shift)
        db.session.commit()

    def createSchedule(self, start_date, end_date, total_hours):
        return Schedule.createSchedule(start_date, end_date, total_hours)

    def approveLeave(self, request_id):
        req = Request.query.get(request_id)
        if req:
            req.status = 'Approved'
            db.session.commit()

class ServiceStaff(db.Model):
    __tablename__ = 'service_staff'
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), primary_key=True)
    availability = db.Column(db.String(50), nullable=True)

    def createAvailability(self, availability):
        self.availability = availability
        db.session.commit()

    def submitAvailability(self):
        db.session.commit()

    def createLeaveRequest(self, start_date, end_date, hours):
        return TimeOff.createTimeOff(start_date, end_date, hours)

    def approveSwap(self, swap_id):
        pass  # Swap logic goes here

    def getShift(self):
        return Shift.query.filter_by(employee_id=self.employee_id).all()

    def logWorkHours(self, log):
        db.session.add(log)
        db.session.commit()

class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(10, 2), nullable=False)

    @staticmethod
    def getSchedule(schedule_id):
        return Schedule.query.get(schedule_id)

    def updateSchedule(self, start_date, end_date, total_hours):
        self.start_date = start_date
        self.end_date = end_date
        self.total_hours = total_hours
        db.session.commit()

    @staticmethod
    def createSchedule(start_date, end_date, total_hours):
        schedule = Schedule(start_date=start_date, end_date=end_date, total_hours=total_hours)
        db.session.add(schedule)
        db.session.commit()
        return schedule

class Shift(db.Model):
    __tablename__ = 'shift'
    shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shift_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_hours = db.Column(db.Numeric(5, 2), nullable=False)
    shift_database = db.Column(db.Text)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'))

    @staticmethod
    def getAvailability(shift_date):
        return Shift.query.filter_by(shift_date=shift_date).all()

    @staticmethod
    def checkShiftAvailability(shift_id):
        return Shift.query.get(shift_id) is not None

    @staticmethod
    def createShift(shift_date, start_time, end_time, total_hours, employee_id):
        shift = Shift(
            shift_date=shift_date,
            start_time=start_time,
            end_time=end_time,
            total_hours=total_hours,
            employee_id=employee_id
        )
        db.session.add(shift)
        db.session.commit()
        return shift

class Request(db.Model):
    __tablename__ = 'request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Pending')

    @staticmethod
    def createRequest(employee_id, request_type, request_date):
        req = Request(employee_id=employee_id, request_type=request_type, request_date=request_date)
        db.session.add(req)
        db.session.commit()
        return req

class TimeOff(db.Model):
    __tablename__ = 'time_off'
    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.Numeric(5, 2), nullable=False)

    @staticmethod
    def displayForm():
        return {'fields': ['start_leave_date', 'end_leave_date', 'total_leave_hours']}

    @staticmethod
    def createTimeOff(start_leave_date, end_leave_date, total_leave_hours):
        time_off = TimeOff(start_leave_date=start_leave_date, end_leave_date=end_leave_date, total_leave_hours=total_leave_hours)
        db.session.add(time_off)
        db.session.commit()
        return time_off

class ClockRecord(db.Model):
    __tablename__ = 'clock_record'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clockIN_time = db.Column(db.DateTime, nullable=False)
    clockOUT_time = db.Column(db.DateTime, nullable=False)
    total_staff_hours = db.Column(db.Numeric(5, 2), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)

    @staticmethod
    def validateID(log_id):
        return ClockRecord.query.get(log_id) is not None

    @staticmethod
    def collectTotalHours(employee_id):
        records = ClockRecord.query.filter_by(employee_id=employee_id).all()
        return sum(record.total_staff_hours for record in records)

    @staticmethod
    def createClockRecord(clockIN_time, clockOUT_time, total_staff_hours, employee_id):
        record = ClockRecord(clockIN_time=clockIN_time, clockOUT_time=clockOUT_time, total_staff_hours=total_staff_hours, employee_id=employee_id)
        db.session.add(record)
        db.session.commit()
        return record

# Many-to-many schedule/shift association table
schedule_shift = db.Table(
    'schedule_shift',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.schedule_id'), primary_key=True),
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)
)
