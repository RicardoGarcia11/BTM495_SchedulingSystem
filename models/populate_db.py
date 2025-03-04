
from models.db_models import db, Employee, Account, Shift, Schedule, ScheduleShift, ShiftEmployee

#this function populates the datbase - based off of sample_data.sql
def populate_db():
    
     
        employee1 = Employee(employee_id=12345, first_name='Alex', last_name='Johnson', address='123 Main St',
                             email='alex@example.com', phone_number=5551234567, hourly_rate=20.50, role='Service Staff')
        employee2 = Employee(employee_id=12346, first_name='Sarah', last_name='Miller', address='456 Oak Ave',
                             email='sarah@example.com', phone_number=5559876543, hourly_rate=22.00, role='Manager')
        

        account1 = Account(employee_id=12345, password='hashed_password')
        account2 = Account(employee_id=12346, password='hashed_password')
        

        shift1 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-03')
        shift2 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-04')
        shift3 = Shift(start_time='09:00:00', end_time='13:00:00', total_hours=4, date='2025-03-07')
        

        schedule1 = Schedule(start_date='2025-03-03', end_date='2025-03-09', total_hours=12)

        schedule_shift1 = ScheduleShift(schedule_id=1, shift_id=1)
        schedule_shift2 = ScheduleShift(schedule_id=1, shift_id=2)
        schedule_shift3 = ScheduleShift(schedule_id=1, shift_id=3)
   
        shift_employee1 = ShiftEmployee(shift_id=1, employee_id=12345)
        shift_employee2 = ShiftEmployee(shift_id=1, employee_id=12346)
        shift_employee3 = ShiftEmployee(shift_id=2, employee_id=12345)
        shift_employee4 = ShiftEmployee(shift_id=2, employee_id=12346)
        shift_employee5 = ShiftEmployee(shift_id=3, employee_id=12345)
        shift_employee6 = ShiftEmployee(shift_id=3, employee_id=12346)
        

        db.session.add_all([employee1, employee2, account1, account2, shift1, shift2, shift3, schedule1,
                            schedule_shift1, schedule_shift2, schedule_shift3, shift_employee1, shift_employee2,
                            shift_employee3, shift_employee4, shift_employee5, shift_employee6])
        
        #add to db
        db.session.commit()
        