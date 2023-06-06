CREATE DATABASE IF NOT EXISTS db;

USE db;

CREATE TABLE Company (
  company_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  email VARCHAR(100) NOT NULL,
  contact_number VARCHAR(50) NOT NULL,
  rating DOUBLE(4, 1),
  logo MEDIUMBLOB
);

CREATE TABLE User (
  user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(50) NOT NULL,
  user_type ENUM('Customer', 'Company_User', 'Admin')
);

CREATE TABLE Customer (
  user_ptr_id INT NOT NULL PRIMARY KEY,
  balance DECIMAL(15, 2),
  phone VARCHAR(20),
  birth_date DATE,
  tck VARCHAR(11) NOT NULL UNIQUE,
  gender ENUM('Male', 'Female'),
  FOREIGN KEY (user_ptr_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Company_User (
  user_ptr_id INT NOT NULL PRIMARY KEY,
  company_id INT NOT NULL,
  role VARCHAR(50),
  FOREIGN KEY (user_ptr_id) REFERENCES User(user_id) ON DELETE CASCADE,
  FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE
);

CREATE TABLE Journey (
  journey_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  journey_name VARCHAR(50),
  all_booked BOOLEAN,
  customer_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES Customer(user_ptr_id) ON DELETE CASCADE
);

CREATE TABLE Vehicle_Model (
  model_name VARCHAR(50) NOT NULL,
  transport_type VARCHAR(50),
  year INT(4) NOT NULL,
  max_range INT(6),
  rating DOUBLE(4, 1),
  seating_plan MEDIUMBLOB,
  PRIMARY KEY (model_name, year)
);

CREATE TABLE Vehicle (
  vehicle_code VARCHAR(20) PRIMARY KEY,
  availability BOOLEAN NOT NULL,
  capacity_firstclass SMALLINT(3),
  capacity_economy SMALLINT(3),
  capacity_business SMALLINT(3),
  model_name VARCHAR(50) NOT NULL,
  year INT(4) NOT NULL,
  company_id INT NOT NULL,
  FOREIGN KEY (model_name, year) REFERENCES Vehicle_Model(model_name, year) ON DELETE CASCADE,
  FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE
);

CREATE TABLE Route(
  route_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  departure_location VARCHAR(50),
  arrival_location VARCHAR(50),
  transport_type ENUM('Flight', 'Bus', 'Train') NOT NULL,
  distance NUMERIC(8, 3)
);

CREATE TABLE Review (
  review_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  company_id INT NOT NULL,
  model_name VARCHAR(50),
  model_year INT(4),
  comment TEXT(500),
  rating numeric(3, 1),
  date datetime,
  FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
  FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE,
  FOREIGN KEY (model_name, model_year) REFERENCES Vehicle_Model(model_name, year) ON DELETE CASCADE
);

CREATE TABLE Schedule (
  code VARCHAR(10) NOT NULL PRIMARY KEY,
  departure_datetime DATETIME,
  arrival_datetime DATETIME,
  male_female_seats BOOLEAN,
  company_id INT NOT NULL,
  vehicle_code VARCHAR(20) NOT NULL,
  route_id INT NOT NULL,
  transfer_code VARCHAR(10) REFERENCES Schedule,
  FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE,
  FOREIGN KEY (vehicle_code) REFERENCES Vehicle(vehicle_code) ON DELETE CASCADE,
  FOREIGN KEY (route_id) REFERENCES Route(route_id) ON DELETE CASCADE
);

CREATE TABLE Ticket (
  schedule_code VARCHAR(10) NOT NULL,
  seat_no SMALLINT NOT NULL,
  customer_id INT,
  status ENUM('Reserved', 'Sold', 'Available') NOT NULL, 
  purchase_datetime DATETIME,
  category ENUM('Economy', 'Business', 'First Class') NOT NULL,
  fare NUMERIC(8, 2),
  PRIMARY KEY (schedule_code, seat_no),
  FOREIGN KEY (customer_id) REFERENCES Customer(user_ptr_id) ON DELETE SET NULL,
  FOREIGN KEY (schedule_code) REFERENCES Schedule(code) ON DELETE CASCADE
);

CREATE TABLE Leg (
  journey_id INT,
  schedule_code VARCHAR(10),
  PRIMARY KEY (journey_id, schedule_code),
  FOREIGN KEY (journey_id) REFERENCES Journey(journey_id) ON DELETE CASCADE,
  FOREIGN KEY (schedule_code) REFERENCES Schedule(code) ON DELETE CASCADE
);