INSERT INTO public.employee (employee_id, first_name, last_name, address, email, phone_number, hourly_rate, role) 
VALUES 
(12345, 'Alex', 'Johnson', '123 Main St', 'alex@example.com', '555-123-4567', 20.50, 'Service Staff'),
(12346, 'Sarah', 'Miller', '456 Oak Ave', 'sarah@example.com', '555-987-6543', 22.00, 'Manager');

INSERT INTO public.account (employee_id, password) 
VALUES (12345, 'hashed_password'), (12346, 'hashed_password');

INSERT INTO public.shift (start_time, end_time, total_hours, date) 
VALUES 
('09:00:00', '13:00:00', 4, '2025-03-03'), -- Monday
('09:00:00', '13:00:00', 4, '2025-03-04'), -- Tuesday
('09:00:00', '13:00:00', 4, '2025-03-07'); -- Friday

INSERT INTO public.schedule (start_date, end_date, total_hours) 
VALUES ('2025-03-03', '2025-03-09', 12);

INSERT INTO public.schedule_shift (schedule_id, shift_id) 
VALUES (1, 1), (1, 2), (1, 3);

INSERT INTO public.shift_employee (shift_id, employee_id) 
VALUES 
(1, 12345), (1, 12346),
(2, 12345), (2, 12346),
(3, 12345), (3, 12346); 