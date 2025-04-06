from datetime import datetime, date

# Class Definitions
class User:
    USER_TYPES = ['Manager', 'Service Staff']

    def __init__(self, employee_id: int, employee_name: str, email: str, user_type: str):
        if user_type not in self.USER_TYPES:
            raise ValueError(f"user_type must be one of {self.USER_TYPES}")
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.email = email
        self.user_type = user_type
        self.account = None
        self.messages_sent = []
        self.messages_received = []

class Account:
    def __init__(self, email: str, password: str, employee_id: int):
        self.email = email
        self.password = password
        self.employee_id = f'{employee_id:03d}'  # Ensure employee_id is 3 digits
        self.user = None

class Message:
    def __init__(self, message_id: int, sender_id: int, recipient_id: int, latest_date: date, latest_time: datetime):
        self.message_id = message_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.latest_date = latest_date
        self.latest_time = latest_time
        self.sender = None
        self.recipient = None

class Manager(User):
    def __init__(self, employee_id: int, employee_name: str, email: str):
        super().__init__(employee_id, employee_name, email, 'Manager')

class ServiceStaff(User):
    def __init__(self, employee_id: int, employee_name: str, email: str, availability: str):
        super().__init__(employee_id, employee_name, email, 'Service Staff')
        self.availability = availability

class Shift:
    def __init__(self, shift_id: int, shift_date: date, start_time: datetime, end_time: datetime, total_hours: float, shift_database: str, employee_id: int):
        self.shift_id = shift_id
        self.shift_date = shift_date
        self.start_time = start_time
        self.end_time = end_time
        self.total_hours = total_hours
        self.shift_database = shift_database
        self.employee_id = employee_id

class Schedule:
    def __init__(self, schedule_id: int, start_date: date, end_date: date, total_hours: float):
        self.schedule_id = schedule_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_hours = total_hours

class ShiftSwap:
    def __init__(self, swap_id: int, requesting_staff: str, receiving_staff: str, original_shift: str, requested_shift: int):
        self.swap_id = swap_id
        self.requesting_staff = requesting_staff
        self.receiving_staff = receiving_staff
        self.original_shift = original_shift
        self.requested_shift = requested_shift

class TimeOff:
    def __init__(self, time_off_id: int, start_leave_date: date, end_leave_date: date, total_leave_hours: float):
        self.time_off_id = time_off_id
        self.start_leave_date = start_leave_date
        self.end_leave_date = end_leave_date
        self.total_leave_hours = total_leave_hours

class ClockRecord:
    def __init__(self, log_id: int, clockIN_time: datetime, clockOUT_time: datetime, total_staff_hours: float, employee_id: int):
        self.log_id = log_id
        self.clockIN_time = clockIN_time
        self.clockOUT_time = clockOUT_time
        self.total_staff_hours = total_staff_hours
        self.employee_id = employee_id

# Method Definitions
def create_account(employee_name: str, email: str, user_type: str, password: str, employee_id: int):
    if user_type == 'Manager':
        user = Manager(employee_id=employee_id, employee_name=employee_name, email=email)
    elif user_type == 'Service Staff':
        user = ServiceStaff(employee_id=employee_id, employee_name=employee_name, email=email, availability='')
    else:
        raise ValueError(f"user_type must be one of {User.USER_TYPES}")
    
    account = Account(email=email, password=password, employee_id=user.employee_id)
    user.account = account
    return {
        'message': f'Account created for {employee_name}',
        'employee_id': user.employee_id
    }

def login(email: str, password: str, accounts: list):
    for account in accounts:
        if account.email == email and account.password == password:
            return {'message': 'Login successful'}
    return {'message': 'Login failed'}

def send_message(sender_id: int, recipient_id: int, messages: list):
    now = datetime.now()
    message = Message(message_id=None, sender_id=sender_id, recipient_id=recipient_id, latest_date=now.date(), latest_time=now)
    messages.append(message)
    return {'message': 'Message sent'}

def assign_shift(shift_date: date, start_time: datetime, end_time: datetime, total_hours: float, shift_database: str, employee_id: int, shifts: list):
    shift = Shift(shift_id=None, shift_date=shift_date, start_time=start_time, end_time=end_time, total_hours=total_hours, shift_database=shift_database, employee_id=employee_id)
    shifts.append(shift)
    return {
        'message': 'Shift assigned',
        'shift_id': shift.shift_id
    }

def request_shift_swap(requesting_staff: str, receiving_staff: str, original_shift: str, requested_shift: int, shift_swaps: list):
    swap = ShiftSwap(swap_id=None, requesting_staff=requesting_staff, receiving_staff=receiving_staff, original_shift=original_shift, requested_shift=requested_shift)
    shift_swaps.append(swap)
    return {
        'message': 'Shift swap requested',
        'swap_id': swap.swap_id
    }

def create_schedule(start_date: date, end_date: date, total_hours: float, schedules: list):
    schedule = Schedule(schedule_id=None, start_date=start_date, end_date=end_date, total_hours=total_hours)
    schedules.append(schedule)
    return {
        'message': 'Schedule created',
        'schedule_id': schedule.schedule_id
    }

def clock_in(employee_id: int, clock_records: list):
    now = datetime.now()
    clock_record = ClockRecord(log_id=None, clockIN_time=now, clockOUT_time=None, total_staff_hours=0, employee_id=employee_id)
    clock_records.append(clock_record)
    return {
        'message': f'Employee {employee_id} clocked in',
        'log_id': clock_record.log_id
    }

def clock_out(log_id: int, clock_records: list):
    for clock_record in clock_records:
        if clock_record.log_id == log_id:
            now = datetime.now()
            clock_record.clockOUT_time = now
            delta = now - clock_record.clockIN_time
            hours = delta.total_seconds() / 3600
            clock_record.total_staff_hours = hours
            return {
                'message': f'Employee {clock_record.employee_id} clocked out',
                'total_hours': float(hours)
            }
    return {'message': 'Clock record not found'}

def request_time_off(employee_id: int, start_leave_date: date, end_leave_date: date, total_leave_hours: float, time_off_requests: list):
    time_off = TimeOff(time_off_id=None, start_leave_date=start_leave_date, end_leave_date=end_leave_date, total_leave_hours=total_leave_hours)
    time_off_requests.append(time_off)
    return {
        'message': f'Time off requested for employee {employee_id}',
        'time_off_id': time_off.time_off_id
    }