CREATE DATABASE restaurantdatabase;
USE  restaurantdatabase;
-- User table
CREATE TABLE user (
    employee_id INT PRIMARY KEY AUTO_INCREMENT, 
    employee_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL
    ); 
/*INSERT INTO user (employee_id, employee_name,email,user_type) VALUES
(001, "John Doe","johndoe@example.com","Manager"); */

-- Account table (linked to employee_id, using it as username for security)
CREATE TABLE account (
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    password VARCHAR(10) NOT NULL, 
    employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
);
/*INSERT INTO account (email, password) 
VALUES (12345, ''), (12346, '');*/

-- Message table
CREATE TABLE message (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    latest_date DATE NOT NULL,
    latest_time TIMESTAMP NOT NULL,
    recipient_id VARCHAR(150) NOT NULL,
    employee_name VARCHAR(150) NOT NULL,
    employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
);
/*INSERT INTO message (message_id,recipient_id, latest_date,latest_time,employee_name) VALUES
(0,"", CURRENT_DATE(),CURRENT_TIME,""); */

-- Service Staff table
CREATE TABLE service_staff (
	availability VARCHAR (50) NOT NULL,
    time_off_id INT,
    employee_id INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
);

-- Manager table 
CREATE TABLE manager (
	employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
	);

-- Shift table (represents a specific shift on a specific day)
CREATE TABLE shift (
    shift_id INT PRIMARY KEY AUTO_INCREMENT,
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,   
    total_hours DECIMAL NOT NULL, --Duration of the total hours of shift during the week
    employee_id INT,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
    );
/*INSERT INTO shift (shift_date, start_time, end_time, total_hours, employee_id) VALUES 
('2025-03-03','09:00:00', '13:00:00', 4,000);*/ -- Monday

-- Schedule table (Weekly Schedule)
CREATE TABLE schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    start_date DATE NOT NULL, --Start of the week
    end_date DATE NOT NULL,   -- End of the week
    total_hours DOUBLE NOT NULL, -- Total hours for the week across shifts
    shift_id INT,
    FOREIGN KEY (shift_id) REFERENCES shift (shift_id)
);
/*INSERT INTO schedule (start_date, end_date, total_hours) 
VALUES ('2025-03-03', '2025-03-09', 12);*/

-- Shift_ServiceStaff bridge table (many-to-many relationship between User and Shift)
CREATE TABLE shift_servicestaff (
    shift_id INT NOT NULL,
    employee_id INT NOT NULL,
    PRIMARY KEY (shift_id, employee_id), -- Composite Key
    FOREIGN KEY (shift_id) REFERENCES shift(shift_id),
    FOREIGN KEY (employee_id) REFERENCES user(employee_id)
);

-- Schedule_Shift junction table (many-to-many between Schedule and Shift)
CREATE TABLE schedule_shift (
    schedule_id INT NOT NULL,
    shift_id INT NOT NULL,
    PRIMARY KEY (schedule_id, shift_id), -- Composite Key
    FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id),
    FOREIGN KEY (shift_id) REFERENCES shift(shift_id)
);
/* Schedule_Shift junction table (many-to-many between Schedule and Shift) */

-- Shift swap table when service staff request to shift swaps
CREATE TABLE shift_swap (
    swap_id INT PRIMARY KEY AUTO_INCREMENT,
    requesting_servicestaff VARCHAR(255) NOT NULL,
    receiving_servicestaff VARCHAR(255) NOT NULL,
    original_shift INTEGER NOT NULL,
    requested_shift INTEGER NOT NULL,
    employee_id INT NOT NULL,
    shift_id INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES user(employee_id),
    FOREIGN KEY (shift_id) REFERENCES shift(shift_id)
);

-- Time off table when service staff request for time off
CREATE TABLE time_off (
    time_off_id INT PRIMARY KEY AUTO_INCREMENT,
    start_leave_date DATE NOT NULL,
    end_leave_date DATE NOT NULL,
    total_leave_hours INTEGER NOT NULL,
    approve_request BOOLEAN DEFAULT FALSE,
    decline_request BOOLEAN DEFAULT FALSE,
    employee_id INT NOT NULL,
	CONSTRAINT time_off_employee FOREIGN KEY (employee_id) REFERENCES user(employee_id)
);


CREATE TABLE clock_record (
	log_id INT PRIMARY KEY AUTO_INCREMENT,
    clockIN_time TIMESTAMP NOT NULL,
    clockOUT_time TIMESTAMP NOT NULL,
    total_staff_hours DOUBLE NOT NULL,
    employee_id INT NOT NULL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES user (employee_id)
    );
