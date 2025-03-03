-- Employee Table
CREATE TABLE public.employee (
    employee_id INTEGER PRIMARY KEY, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    address VARCHAR(200),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number INTEGER,
    hourly_rate DOUBLE PRECISION,
    role VARCHAR(50) NOT NULL 
);

-- Account table (linked to employee_id, using it as username for security)
CREATE TABLE public.account (
    employee_id INTEGER PRIMARY KEY, -- Use employee_id as the unique identifier
    password VARCHAR(255) NOT NULL, 
    CONSTRAINT fk_account_employee FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id)
);

-- Shift table (represents a specific shift on a specific day)
CREATE TABLE public.shift (
    shift_id SERIAL PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,   
    total_hours INTEGER NOT NULL, -- Duration in hours
    date DATE NOT NULL,       -- Date of the shift 
    CONSTRAINT check_hours CHECK (total_hours = EXTRACT(EPOCH FROM (end_time - start_time)) / 3600) -- Ensure total_hours matches time duration
);

-- Schedule table (Weekly Schedule)
CREATE TABLE public.schedule (
    schedule_id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL, -- Start of the week
    end_date DATE NOT NULL,   -- End of the week
    total_hours INTEGER NOT NULL, -- Total hours for the week across all shifts
    CONSTRAINT check_weekly_dates CHECK (end_date = start_date + INTERVAL '6 days') -- Ensure 7-day week
);

-- Shift_Employee bridge table (many-to-many relationship between Employee and Shift)
CREATE TABLE public.shift_employee (
    shift_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    PRIMARY KEY (shift_id, employee_id), -- Composite Key
    CONSTRAINT fk_shift_employee_shift FOREIGN KEY (shift_id) REFERENCES public.shift(shift_id),
    CONSTRAINT fk_shift_employee_employee FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id)
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
    CONSTRAINT fk_sender FOREIGN KEY (sender_id) REFERENCES public.employee(employee_id),
    CONSTRAINT fk_recipient FOREIGN KEY (recipient_id) REFERENCES public.employee(employee_id)
);

-- Shift Swap table
CREATE TABLE public.shift_swap (
    swap_id SERIAL PRIMARY KEY,
    requesting_emp INTEGER NOT NULL,
    receiving_emp INTEGER NOT NULL,
    original_shift INTEGER NOT NULL,
    requested_shift INTEGER NOT NULL,
    CONSTRAINT fk_requesting_swap_employee FOREIGN KEY (requesting_emp) REFERENCES public.employee(employee_id),
    CONSTRAINT fk_receiving_swap_employee FOREIGN KEY (receiving_emp) REFERENCES public.employee(employee_id),
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
    CONSTRAINT fk_time_off_employee FOREIGN KEY (employee_id) REFERENCES public.employee(employee_id)
);