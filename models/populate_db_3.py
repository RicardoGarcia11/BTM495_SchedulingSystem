from datetime import datetime, date
from models.db_modelsV3 import db, User, Account, Message, Manager, ServiceStaff, Shift, Schedule, ShiftSwap, TimeOff, ClockRecord

# Initialize the database
db.create_all()

# Populate Users
user1 = User(employee_name='John Doe', email='john.doe@example.com', user_type='Manager')
user2 = User(employee_name='Jane Smith', email='jane.smith@example.com', user_type='Service_Staff')
user3 = User(employee_name='Alice Johnson', email='alice.johnson@example.com', user_type='Service_Staff')

db.session.add_all([user1, user2, user3])
db.session.commit()

# Populate Accounts
account1 = Account(email='john.doe@example.com', password='password123', employee_id=user1.employee_id)
account2 = Account(email='jane.smith@example.com', password='password123', employee_id=user2.employee_id)
account3 = Account(email='alice.johnson@example.com', password='password123', employee_id=user3.employee_id)

db.session.add_all([account1, account2, account3])
db.session.commit()

# Populate Managers
manager1 = Manager(employee_id=user1.employee_id)

db.session.add(manager1)
db.session.commit()

# Populate ServiceStaff
service_staff1 = ServiceStaff(employee_id=user2.employee_id, availability='Monday to Friday')
service_staff2 = ServiceStaff(employee_id=user3.employee_id, availability='Weekends')

db.session.add_all([service_staff1, service_staff2])
db.session.commit()

# Populate Shifts
shift1 = Shift(shift_date=date(2025, 3, 14), start_time=datetime(2025, 3, 14, 9, 0), end_time=datetime(2025, 3, 14, 17, 0), total_hours=8, shift_database='Shift 1', employee_id=user2.employee_id)
shift2 = Shift(shift_date=date(2025, 3, 15), start_time=datetime(2025, 3, 15, 9, 0), end_time=datetime(2025, 3, 15, 17, 0), total_hours=8, shift_database='Shift 2', employee_id=user3.employee_id)

db.session.add_all([shift1, shift2])
db.session.commit()

# Populate Schedules
schedule1 = Schedule(start_date=date(2025, 3, 14), end_date=date(2025, 3, 20), total_hours=40)

db.session.add(schedule1)
db.session.commit()

# Populate Messages
message1 = Message(sender_id=user1.employee_id, recipient_id=user2.employee_id, latest_date=date(2025, 3, 13), latest_time=datetime(2025, 3, 13, 10, 0))
message2 = Message(sender_id=user2.employee_id, recipient_id=user1.employee_id, latest_date=date(2025, 3, 13), latest_time=datetime(2025, 3, 13, 11, 0))

db.session.add_all([message1, message2])
db.session.commit()

# Populate ShiftSwaps
shift_swap1 = ShiftSwap(requesting_staff='Jane Smith', receiving_staff='Alice Johnson', original_shift='Shift 1', requested_shift=shift2.shift_id)

db.session.add(shift_swap1)
db.session.commit()

# Populate TimeOff
time_off1 = TimeOff(start_leave_date=date(2025, 3, 16), end_leave_date=date(2025, 3, 18), total_leave_hours=16)

db.session.add(time_off1)
db.session.commit()

# Populate ClockRecords
clock_record1 = ClockRecord(clockIN_time=datetime(2025, 3, 13, 9, 0), clockOUT_time=datetime(2025, 3, 13, 17, 0), total_staff_hours=8, employee_id=user2.employee_id)
clock_record2 = ClockRecord(clockIN_time=datetime(2025, 3, 14, 9, 0), clockOUT_time=datetime(2025, 3, 14, 17, 0), total_staff_hours=8, employee_id=user3.employee_id)

db.session.add_all([clock_record1, clock_record2])
db.session.commit()

print("Database populated successfully!")