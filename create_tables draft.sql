-- User Table
CREATE TABLE public.user (
    employee_id INTEGER PRIMARY KEY, 
    employee_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    user_type VARCHAR(50) NOT NULL,
);

-- Account table (linked to employee_id, using it as username for security)
CREATE TABLE public.account (
    email INTEGER PRIMARY KEY, -- Use employee_id as the unique identifier
    password VARCHAR(255) NOT NULL, 
    CONSTRAINT fk_account_employee FOREIGN KEY (employee_id) REFERENCES public.user(employee_id)
);

-- Shift table (represents a specific shift on a specific day)
CREATE TABLE public.shift (
    shift_id SERIAL PRIMARY KEY,
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,   
    total_hours DECIMAL NOT NULL, -- Duration in hours
    shift_database LIST NOT NULL, -- IS THIS ATTRIBUTE VALID?
    CONSTRAINT check_hours CHECK (total_hours = EXTRACT(EPOCH FROM (end_time - start_time)) / 3600) -- Ensure total_hours matches time duration
);

-- Schedule table (Weekly Schedule)
CREATE TABLE public.schedule (
    schedule_id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL, -- Start of the week
    end_date DATE NOT NULL,   -- End of the week
    total_hours DECIMAL NOT NULL, -- Total hours for the week across all shifts
    CONSTRAINT check_weekly_dates CHECK (end_date = start_date + INTERVAL '6 days') -- Ensure 7-day week
);

-- Shift_ServiceStaff bridge table (many-to-many relationship between User and Shift)
CREATE TABLE public.Shift_servicestaff (
    shift_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    PRIMARY KEY (shift_id, employee_id), -- Composite Key
    CONSTRAINT fk_shift_employee_shift FOREIGN KEY (shift_id) REFERENCES public.shift(shift_id),
    CONSTRAINT fk_shift_employee_employee FOREIGN KEY (employee_id) REFERENCES public.user(employee_id)
);

-- Schedule_Shift junction table (many-to-many between Schedule and Shift)
CREATE TABLE public.schedule_shift (
    schedule_id INTEGER NOT NULL,
    shift_id INTEGER NOT NULL,
    PRIMARY KEY (schedule_id, shift_id), -- Composite Key
    CONSTRAINT fk_schedule_shift_schedule FOREIGN KEY (schedule_id) REFERENCES public.schedule(schedule_id),
    CONSTRAINT fk_schedule_shift_shift FOREIGN KEY (shift_id) REFERENCES public.shift(shift_id)
);

-- Message table
CREATE TABLE public.message (
    message_id SERIAL PRIMARY KEY,
    latest_date DATE NOT NULL,
    latest_time TIMESTAMP NOT NULL,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    CONSTRAINT fk_sender FOREIGN KEY (sender_id) REFERENCES public.user(employee_id),
    CONSTRAINT fk_recipient FOREIGN KEY (recipient_id) REFERENCES public.user(employee_id)
);

-- Shift Swap table
CREATE TABLE public.shift_swap (
    swap_id SERIAL PRIMARY KEY,
    requesting_servicestaff INTEGER NOT NULL,
    receiving_servicestaff INTEGER NOT NULL,
    original_shift INTEGER NOT NULL, --IS THIS AN INTEGER OR CLASS OF SHIFT?
    requested_shift INTEGER NOT NULL,
    CONSTRAINT fk_requesting_swap_employee FOREIGN KEY (requesting_emp) REFERENCES public.user(employee_id),
    CONSTRAINT fk_receiving_swap_employee FOREIGN KEY (receiving_emp) REFERENCES public.user(employee_id),
    CONSTRAINT fk_original_shift FOREIGN KEY (original_shift) REFERENCES public.shift(shift_id),
    CONSTRAINT fk_requested_shift FOREIGN KEY (requested_shift) REFERENCES public.shift(shift_id)
);

-- Time Off table
CREATE TABLE public.time_off (
    time_off_id SERIAL PRIMARY KEY,
    start_leave_date DATE NOT NULL,
    end_leave_date DATE NOT NULL,
    total_leave_hours INTEGER NOT NULL,
    approve_request BOOLEAN DEFAULT FALSE,
    decline_request BOOLEAN DEFAULT FALSE,
    employee_id INTEGER NOT NULL,
    CONSTRAINT fk_time_off_employee FOREIGN KEY (employee_id) REFERENCES public.user(employee_id)
);