-- INSERT STATEMENTS
-- Inserting data into the "Company" table
INSERT INTO Company (name, email, contact_number, rating, logo)
VALUES
  ('OZ ERCIS SEYAHAT', 'abc@example.com', '1234567890', 0, NULL),
  ('LUKS ADANA', 'xyz@example.com', '9876543210', 0, NULL),
  ('Kamil Koc', 'pqr@example.com', '5555555555', 0, NULL),
  ('Turkish Airlines', 'thy@thy.com', '02121110111', 0, NULL),
  ('TCDD', 'iletisim@tcdd.com', '123123', 0, NULL);

-- Inserting data into the "User" table
INSERT INTO User (name, email, password, user_type)
VALUES
  ('John Doe', 'john@example.com', 'password123', 'Customer'),
  ('Jane Smith', 'jane@example.com', 'securepass', 'Company_User'),
  ('Admin User', 'admin@example.com', 'adminpass', 'Admin'),
  ('Turna Balasario', 'turna@example.com', 'pass', 'Customer'),
  ('Elon Musk', 'elon@example.com', 'twitter', 'Company_User');


-- Inserting data into the "Customer" table
INSERT INTO Customer (user_ptr_id, balance, phone, birth_date, tck, gender)
VALUES
  (1, 1000.00, '1234567890', '1990-05-20', '12345678901', 'Male'),
  (4, 500.00, '9876543210', '1995-10-15', '98765432109', 'Female');
  

-- Inserting data into the "Company_User" table
INSERT INTO Company_User (user_ptr_id, company_id, role)
VALUES
  (5, 1, 'Manager'),
  (2, 1, 'Employee');


-- Inserting data into the "Journey" table
INSERT INTO Journey (journey_name, all_booked, customer_id)
VALUES
  ('Summer Vacation', FALSE, 1),
  ('Business Trip', FALSE, 4);


-- Inserting data into the "Vehicle_Model" table
INSERT INTO Vehicle_Model (model_name, transport_type, year, max_range, rating, seating_plan)
VALUES
  ('Boeing 747', 'Plane', 2015, 10000, 0, NULL),
  ('Neoplan Starliner', 'Bus', 2017, 800, 0, NULL),
  ('Mercedes-Benz Travego', 'Bus', 2019, 860, 0, NULL),
  ('Siemens Valero (YHT)', 'Train', 2016, NULL, 0, NULL);



-- Inserting data into the "Vehicle" table
INSERT INTO Vehicle (vehicle_code, availability, capacity_firstclass, capacity_economy, capacity_business, model_name, year, company_id)
VALUES
  ('TK78119', TRUE, 30, 150, 40, 'Boeing 747', 2015, 4),
  ('01AC2334', TRUE, 0, 60, 0, 'Neoplan Starliner', 2017, 1),
  ('34T1111', TRUE, 0, 60, 0, 'Neoplan Starliner', 2017, 1),
  ('34T7324', TRUE, 10, 30, 20, 'Mercedes-Benz Travego', 2019, 3),
  ('YHT-123', TRUE, 0, 300, 50, 'Siemens Valero (YHT)', 2016, 5);



INSERT INTO Route (departure_location, arrival_location, distance)
VALUES
  ('Ankara ASTI', 'Istanbul Esenler', 450.123),
  ('Ercis Otogar', 'Adana Otogar', 1000.678),
  ('Istanbul Sabiha Gokcen', 'New York JFK', 8216.789),
  ('Ankara Gar', 'Istanbul Sogutlucesme YHT', 390.123),
  ('Istanbul Sogutlucesme YHT', 'Ankara Gar', 390.123),
  ('Istanbul Esenler', 'Ankara ASTI', 450.123),
  ('Adana Otogar', 'Ercis Otogar', 1000.678),
  ('New York JFK', 'Istanbul Sabiha Gokcen', 8216.789);


-- Inserting data into the "Review" table
INSERT INTO Review (user_id, company_id, model_name, model_year, comment, rating, date)
VALUES
  (1, 1, NULL, NULL, 'Had a smooth ride!', 4.5, '2022-02-15 10:30:00'),
  (2, 3, 'Mercedes-Benz Travego', 2019, 'The bus was comfortable and clean.', 4.0, '2022-03-10 16:45:00');

-- Inserting data into the "Schedule" table
INSERT INTO Schedule (code, transport_type, departure_datetime, arrival_datetime, 
                        male_female_seats, company_id, vehicle_code, route_id, transfer_code)
VALUES
  ('S001', 'Plane', '2022-06-15 08:00:00', '2022-06-15 16:00:00', TRUE, 4, 'TK78119', 3, NULL),
  ('S002', 'Bus', '2022-06-20 10:00:00', '2022-06-20 17:00:00', FALSE, 3, '34T7324', 1, NULL),
  ('S003', 'Bus', '2022-06-20 12:00:00', '2022-06-20 19:00:00', FALSE, 3, '34T1111', 1, NULL);

