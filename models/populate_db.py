from models import db, Employee, Account, Shift, Schedule, ScheduleShift, ShiftEmployee
from flask import Flask

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost/your_database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Function to populate the database
def populate_db():
    with app.app_context():
        # Create sample employees
        employee1 = Employee(employee_id=12345, first_name='Alex', last_name='Johnson', address='123 Main St',
                             email='alex@example.com', phone_number=5551234567, hourly_rate=20.50, role='Service Staff')
        employee2 = Employee(employee_id=12346, first_name='Sarah', last_name='Miller', address='456 Oak Ave',
                             email='sarah@example.com', phone_number=5559876543, hourly_rate=22.00, role='Manager')
        
        # Create sample accounts
        account1 = Account(employee_id=12345, password='hashed_password')
        account2 = Account(employee_id=12346, password='hashed_password')
        
        # Create sample shifts
        shift1 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-03')
        shift2 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-04')
        shift3 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-07')
        
        # Create sample schedule
        schedule1 = Schedule(start_date='2025-03-03', end_date='2025-03-09', total_hours=12)
        
        # Create schedule-shift relationships
        schedule_shift1 = ScheduleShift(schedule_id=1, shift_id=1)
        schedule_shift2 = ScheduleShift(schedule_id=1, shift_id=2)
        schedule_shift3 = ScheduleShift(schedule_id=1, shift_id=3)
        
        # Create shift-employee relationships
        shift_employee1 = ShiftEmployee(shift_id=1, employee_id=12345)
        shift_employee2 = ShiftEmployee(shift_id=1, employee_id=12346)
        shift_employee3 = ShiftEmployee(shift_id=2, employee_id=12345)
        shift_employee4 = ShiftEmployee(shift_id=2, employee_id=12346)
        shift_employee5 = ShiftEmployee(shift_id=3, employee_id=12345)
        shift_employee6 = ShiftEmployee(shift_id=3, employee_id=12346)
        
        # Add to session
        db.session.add_all([employee1, employee2, account1, account2, shift1, shift2, shift3, schedule1,
                            schedule_shift1, schedule_shift2, schedule_shift3, shift_employee1, shift_employee2,
                            shift_employee3, shift_employee4, shift_employee5, shift_employee6])
        
        # Commit to database
        db.session.commit()
        print("Database populated successfully!")

if __name__ == "__main__":
    populate_db()