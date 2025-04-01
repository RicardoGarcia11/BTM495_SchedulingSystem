from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduling_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

schedule_shift = db.Table(
    'schedule_shift',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.schedule_id'), primary_key=True),
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.shift_id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.Enum('Manager', 'Service_Staff'), nullable=False)

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)

    def register(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def login(email, password):
        return Account.query.filter_by(email=email, password=password).first()

    def sendMessage(self, recipient_id, text_message):
        message = Message(
            sender_id=self.employee_id,
            recipient_id=recipient_id,
            latest_date=date.today(),
            latest_time=datetime.now(),
            message_text = text_message
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
    message_text = db.Column(db.Text, nullable=False)
  
    def loadChatHistory(self, other_user_id):
        messages = Message.query.filter(
        ((Message.sender_id == self.employee_id) & (Message.recipient_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.recipient_id == self.employee_id))
    ).order_by(Message.latest_time).all()
    
        return messages


class Account(db.Model):
    __tablename__ = 'account'
    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), unique=True)
    manager_code = db.Column(db.Integer)

    @property
    def user_type(self):
        user = User.query.get(self.employee_id)
        return user.user_type if user else None

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

    def assignShift(self, shift, schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if schedule:
            schedule.shifts.append(shift)
            db.session.commit()
        else:
            print(f"Error: Schedule with ID {schedule_id} not found.")

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
        swap_request = Request.query.get(swap_id)
        if not swap_request:
            return jsonify({"message": "Swap request not found."}), 404

        if swap_request.status != 'Pending':
            return jsonify({"message": f"Swap request is already {swap_request.status}."}), 400

        if swap_request.request_type != 'Shift Swap':
            return jsonify({"message": "This request is not a shift swap."}), 400
        
        requested_shift = Shift.query.get(swap_request.request_id)  
        target_shift = Shift.query.filter_by(employee_id=swap_request.employee_id).first()

        if not requested_shift or not target_shift:
            return jsonify({"message": "One or both shifts involved in the swap not found."}), 404

       
        temp_employee_id = requested_shift.employee_id
        requested_shift.employee_id = target_shift.employee_id
        target_shift.employee_id = temp_employee_id
        swap_request.status = 'Approved'
        db.session.commit()

        return jsonify({"message": f"Swap request {swap_id} approved and shifts swapped."}), 200
    
    def createSwapRequest(self, requested_shift_id, target_shift_id):
        requested_shift = Shift.query.get(requested_shift_id)
        target_shift = Shift.query.get(target_shift_id)

        if not requested_shift or not target_shift:
            return jsonify({"message": "One or both shifts not found."}), 404
        
        if requested_shift.employee_id != self.employee_id:
            return jsonify({"message": "You can only request a swap for your own shift."}), 400

        swap_request = Request.createRequest(
            employee_id=self.employee_id,
            request_type='Shift Swap',
            request_date=datetime.now()
        )
        swap_request.requested_shift_id = requested_shift_id
        swap_request.target_shift_id = target_shift_id

        db.session.commit()

        return jsonify({"message": f"Swap request {swap_request.request_id} created successfully."}), 201

    def getShift(self, shift_id):
        if Shift.checkShiftAvailability(shift_id):
            shift = Shift.query.get(shift_id)
            shift.employee_id = self.employee_id
            db.session.commit()
            return shift
        else:
            return None

    def logWorkHours(self, log):
        db.session.add(log)
        db.session.commit()

class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(10, 2), nullable=False)
    shifts = db.relationship('Shift', secondary=schedule_shift, backref=db.backref('schedules', lazy='dynamic'))

    @staticmethod
    def getSchedule(schedule_id, manager_id):
        return Schedule.query.filter_by(schedule_id=schedule_id, manager_id=manager_id).first()

    def updateSchedule(self, start_date, end_date, total_hours):
        self.start_date = start_date
        self.end_date = end_date
        self.total_hours = total_hours
        db.session.commit()

    def getShiftDB(self):
        return self.shifts
    
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
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'))

    @staticmethod
    def getAvailability(shift_date):
        return Shift.query.filter_by(shift_date=shift_date).all()

    @staticmethod
    def checkShiftAvailability(shift_id):
        shift = Shift.query.get(shift_id)

        if shift is None:
            return False
  
        return shift.employee_id is None

    @staticmethod
    def createShift(shift_date, start_time, end_time, total_hours, employee_id=None):
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
    status = db.Column(db.String(50), default='Pending')
    request_type = db.Column(db.String(50)) 

    @staticmethod
    def createRequest(employee_id, request_type, request_date):
        req = Request(employee_id=employee_id, request_type=request_type, request_date=request_date)
        db.session.add(req)
        db.session.commit()
        return req
    
    def cancelRequest(self):
        self.status = 'Cancelled'
        db.session.commit()
        return jsonify({"message": f"Request {self.request_id} has been cancelled."}), 200
    
    def getManagerApproval(self):
        if self.status == 'Cancelled':
            return jsonify({"message": f"Request {self.request_id} has been cancelled."}), 400
        if self.request_type == 'Time Off':
            if self.status == 'Approved':
                return jsonify({"message": f"Time-off request {self.request_id} has been approved."}), 200
            elif self.status == 'Pending':
                return jsonify({"message": f"Time-off request {self.request_id} is still pending."}), 400
            else:
                return jsonify({"message": f"Time-off request {self.request_id} has been rejected or is in an invalid state."}), 400
        else:
            return jsonify({"message": "This is not a time-off request."}), 400
    
    def getStaffApproval(self):
        if self.status == 'Cancelled':
            return jsonify({"message": f"Request {self.request_id} has been cancelled."}), 400
        if self.request_type == 'Shift Swap':
            if self.status == 'Approved':
                return jsonify({"message": f"Shift swap request {self.request_id} has been approved and processed."}), 200
            elif self.status == 'Pending':
                return jsonify({"message": f"Shift swap request {self.request_id} is still pending."}), 400
            else:
                return jsonify({"message": f"Shift swap request {self.request_id} has been rejected or is in an invalid state."}), 400
        else:
            return jsonify({"message": "This is not a shift swap request."}), 400
    
class TimeOff(db.Model):
    __tablename__ = 'time_off'
    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.Numeric(5, 2), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id'), nullable=False)  # ✅ Add this line

    @staticmethod
    def createTimeOff(start_leave_date, end_leave_date, total_leave_hours, employee_id):
        time_off = TimeOff(
            start_leave_date=start_leave_date,
            end_leave_date=end_leave_date,
            total_leave_hours=total_leave_hours,
            employee_id=employee_id
        )
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

