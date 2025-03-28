from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

# Request model
class Request(db.Model):
    __tablename__ = 'request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Pending')

    @staticmethod
    def createRequest(employee_id, request_type, request_date):
        new_request = Request(
            employee_id=employee_id,
            request_type=request_type,
            request_date=request_date
        )
        db.session.add(new_request)
        db.session.commit()
        return new_request

    @staticmethod
    def getRequest(request_id):
        return Request.query.get(request_id)

# Association table for Schedule and Shift
schedule_shift = db.Table(
    'schedule_shift',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.schedule_id'), primary_key=True),
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)
)

# Schedule model
class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(10, 2), nullable=False)

    @staticmethod
    def getSchedule(schedule_id):
        return Schedule.query.get(schedule_id)

    def getShiftDB(self):
        shifts = Shift.query.join(schedule_shift).filter(schedule_shift.c.schedule_id == self.schedule_id).all()
        return shifts

    def updateSchedule(self, start_date, end_date, total_hours):
        self.start_date = start_date
        self.end_date = end_date
        self.total_hours = total_hours
        db.session.commit()

    @staticmethod
    def createSchedule(start_date, end_date, total_hours):
        new_schedule = Schedule(
            start_date=start_date,
            end_date=end_date,
            total_hours=total_hours
        )
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule

# Shift model
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
        shift = Shift.query.get(shift_id)
        return shift is not None

    @staticmethod
    def createShift(shift_date, start_time, end_time, total_hours, employee_id):
        new_shift = Shift(
            shift_date=shift_date,
            start_time=start_time,
            end_time=end_time,
            total_hours=total_hours,
            employee_id=employee_id
        )
        db.session.add(new_shift)
        db.session.commit()
        return new_shift

# TimeOff model
class TimeOff(db.Model):
    __tablename__ = 'time_off'
    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.Numeric(5, 2), nullable=False)

    @staticmethod
    def displayForm():
        return {
            'fields': ['start_leave_date', 'end_leave_date', 'total_leave_hours']
        }

    @staticmethod
    def createTimeOff(start_leave_date, end_leave_date, total_leave_hours):
        new_time_off = TimeOff(
            start_leave_date=start_leave_date,
            end_leave_date=end_leave_date,
            total_leave_hours=total_leave_hours
        )
        db.session.add(new_time_off)
        db.session.commit()
        return new_time_off

# ClockRecord model
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
        new_record = ClockRecord(
            clockIN_time=clockIN_time,
            clockOUT_time=clockOUT_time,
            total_staff_hours=total_staff_hours,
            employee_id=employee_id
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record