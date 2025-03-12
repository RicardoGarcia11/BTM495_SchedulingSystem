

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# User Table 
class User(db.Model):
    __tablename__ = 'user'

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    user_type = db.Column(db.Enum('Manager', 'Service_Staff'), nullable=False)

    messages_sent = db.relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = db.relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    shifts = db.relationship("Shift", back_populates="employee")
    clock_records = db.relationship("ClockRecord", back_populates="employee")

    def register(self, password):
        """Registers a user by creating an associated account record."""
        new_account = Account(email=self.email, password=password, employee_id=self.employee_id)
        db.session.add(new_account)
        db.session.commit()

    @staticmethod
    def login(email, password):
        """Verifies user login credentials."""
        account = Account.query.filter_by(email=email, password=password).first()
        return account is not None

# Account Table 
class Account(db.Model):
    __tablename__ = 'account'

    email = db.Column(db.String(255), db.ForeignKey('user.email'), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), unique=True)

# Message Table (Stores communication between employees)
class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), nullable=False)
    latest_date = db.Column(db.Date, nullable=False)
    latest_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = db.relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")

    @staticmethod
    def create_chat(sender_id, recipient_id):
        """Creates a new message (chat) entry."""
        new_message = Message(sender_id=sender_id, recipient_id=recipient_id,
                              latest_date=datetime.today().date(), latest_time=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()

    @staticmethod
    def delete_chat(message_id):
        """Deletes a message."""
        Message.query.filter_by(message_id=message_id).delete()
        db.session.commit()

# Manager Table (Subclass of User)
class Manager(User):
    __tablename__ = 'manager'

    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), primary_key=True)

    def approve_leave(self, time_off_id):
        """Approves a leave request by removing it from the database."""
        time_off = TimeOff.query.get(time_off_id)
        if time_off:
            db.session.delete(time_off)
            db.session.commit()

    def assign_shift(self, shift_id, employee_id):
        """Assigns a shift to a service staff member."""
        shift = Shift.query.get(shift_id)
        if shift:
            shift.employee_id = employee_id
            db.session.commit()

# Service Staff Table (Subclass of User)
class ServiceStaff(User):
    __tablename__ = 'service_staff'

    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), primary_key=True)
    availability = db.Column(db.String(50), nullable=False)

    shifts = db.relationship("Shift", secondary="shift_servicestaff", back_populates="service_staff")
    shift_swaps = db.relationship("ShiftSwap", foreign_keys="ShiftSwap.requesting_staff")
    time_off_requests = db.relationship("TimeOff", back_populates="employee")

    def request_swap(self, receiving_staff_id, original_shift_id, requested_shift_id):
        """Requests a shift swap."""
        swap = ShiftSwap(requesting_staff=self.employee_id, receiving_staff=receiving_staff_id,
                         original_shift=original_shift_id, requested_shift=requested_shift_id)
        db.session.add(swap)
        db.session.commit()

    def request_leave(self, start_date, end_date, total_hours):
        """Requests time off."""
        leave = TimeOff(employee_id=self.employee_id, start_leave_date=start_date, end_leave_date=end_date,
                        total_leave_hours=total_hours)
        db.session.add(leave)
        db.session.commit()

# Shift Table (Represents shifts for employees)
class Shift(db.Model):
    __tablename__ = 'shift'

    shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shift_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_hours = db.Column(db.DECIMAL(5,2), nullable=False)
    shift_database = db.Column(db.Text)

    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="SET NULL"))
    employee = db.relationship("User", back_populates="shifts")

# Shift Swap Table
class ShiftSwap(db.Model):
    __tablename__ = 'shift_swap'

    swap_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requesting_staff = db.Column(db.Integer, db.ForeignKey('service_staff.employee_id', ondelete="CASCADE"), nullable=False)
    receiving_staff = db.Column(db.Integer, db.ForeignKey('service_staff.employee_id', ondelete="CASCADE"), nullable=False)
    original_shift = db.Column(db.Integer, db.ForeignKey('shift.shift_id', ondelete="CASCADE"), nullable=False)
    requested_shift = db.Column(db.Integer, db.ForeignKey('shift.shift_id', ondelete="CASCADE"), nullable=False)

# Time Off Table
class TimeOff(db.Model):
    __tablename__ = 'time_off'

    time_off_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_leave_date = db.Column(db.Date, nullable=False)
    end_leave_date = db.Column(db.Date, nullable=False)
    total_leave_hours = db.Column(db.DECIMAL(5,2), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('service_staff.employee_id', ondelete="CASCADE"), nullable=False)
    employee = db.relationship("ServiceStaff", back_populates="time_off_requests")

# Clock Record Table
class ClockRecord(db.Model):
    __tablename__ = 'clock_record'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clockIN_time = db.Column(db.DateTime, nullable=False)
    clockOUT_time = db.Column(db.DateTime, nullable=False)
    total_staff_hours = db.Column(db.DECIMAL(5,2), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.employee_id', ondelete="CASCADE"), nullable=False)
    employee = db.relationship("User", back_populates="clock_records")

    def clock_in(self, employee_id):
        """Registers a clock-in event."""
        new_record = ClockRecord(clockIN_time=datetime.utcnow(), clockOUT_time=None,
                                 total_staff_hours=0, employee_id=employee_id)
        db.session.add(new_record)
        db.session.commit()

    def clock_out(self, log_id):
        """Registers a clock-out event."""
        record = ClockRecord.query.get(log_id)
        if record:
            record.clockOUT_time = datetime.utcnow()
            record.total_staff_hours = (record.clockOUT_time - record.clockIN_time).total_seconds() / 3600
            db.session.commit()
