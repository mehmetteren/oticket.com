
/*DROP TABLE Customer;
CREATE TABLE Customer (
	user_ptr_id	INT NOT NULL PRIMARY KEY,
	balance	    DECIMAL(15,2),
	phone		VARCHAR(20),
	birth_date	DATE,
	tck		    VARCHAR(11) NOT NULL UNIQUE,
    gender	    VARCHAR(15),
    FOREIGN KEY (user_ptr_id) REFERENCES User(user_id));
    
INSERT INTO User(name, email, password) VALUES ('eren', 'eren@sql.com', '123');

INSERT INTO Customer(user_ptr_id, balance, birth_date, tck, gender) VALUES (1, 1500.23, '1991/10/10', '12312312312', 'male');

CREATE TABLE Company_User (
    user_ptr_id	    INT NOT NULL PRIMARY KEY,
	role		    VARCHAR(50));

CREATE TABLE Schedule (
	code				VARCHAR(10) NOT NULL PRIMARY KEY,
	transport_type		VARCHAR(50),
    departure_datetime	DATETIME,
    arrival_datetime	DATETIME,
    male_female_seats	BOOLEAN);*/

/*
CREATE TABLE Seat (
    schedule_code VARCHAR(10) NOT NULL, 
    seat_no SMALLINT(4), 
    occupancy BOOLEAN, 
    category VARCHAR(30),
    fare NUMERIC(8,2),
    PRIMARY KEY (schedule_code, seat_no),
    FOREIGN KEY (schedule_code) REFERENCES Schedule(code));

CREATE TABLE Company (
	company_id		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	name			VARCHAR(100) UNIQUE,
	email			VARCHAR(100) NOT NULL,
	contact_number	VARCHAR(50) NOT NULL,
	rating			DOUBLE(4,1));

CREATE TABLE Vehicle_Model (
	model_name		VARCHAR(50) PRIMARY KEY,
	transport_type	VARCHAR(50),
	year			INT(4),
	max_range		INT(6),
	rating			DOUBLE(4,1));

CREATE TABLE Review (
	review_id		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    company_id      INT NOT NULL,
    model_name      VARCHAR(50),
	comment		    TEXT(500),
    rating			numeric(3,1),
    date			datetime,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (company_id) REFERENCES Company(company_id),
    FOREIGN KEY (model_name) REFERENCES 
        Vehicle_Model(model_name));

CREATE TABLE Journey (
    journey_id		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	journey_name	VARCHAR(50),
    all_booked		BOOLEAN, 
    customer_id     INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(user_ptr_id));

CREATE TABLE Ticket (
	ticket_id			INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id         INT NOT NULL,
    schedule_code       VARCHAR(10) NOT NULL,
    seat_no             SMALLINT(4) NOT NULL,
	purchase_datetime	DATETIME,
    reserved			BOOLEAN,
    FOREIGN KEY (customer_id) REFERENCES Customer(user_ptr_id),
    FOREIGN KEY (schedule_code, seat_no) REFERENCES 
            Seat(schedule_code, seat_no));

CREATE TABLE Vehicle (
	vehicle_code		VARCHAR(20) PRIMARY KEY,
	availability		BOOLEAN,
    capacity_firstclass	SMALLINT(3),
    capacity_economy	SMALLINT(3),
    capacity_business	SMALLINT(3),
    model_name          VARCHAR(50) NOT NULL,
    FOREIGN KEY (model_name) REFERENCES Vehicle_Model(model_name));

CREATE TABLE Route(
	route_id			INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	departure_location	VARCHAR(50),
    arrival_location	VARCHAR(50),
    distance			NUMERIC(8,3));

CREATE TABLE Schedule (
	code				VARCHAR(10) NOT NULL PRIMARY KEY,
	transport_type		VARCHAR(50),
    departure_datetime	DATETIME,
    arrival_datetime	DATETIME,
    male_female_seats	BOOLEAN,
    company_id          INT NOT NULL,
    vehicle_code        VARCHAR(20) NOT NULL,
    route_id            INT NOT NULL,
    transfer_code       VARCHAR(10) NOT NULL REFERENCES Schedule,
    FOREIGN KEY (company_id) REFERENCES Company(company_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_code) REFERENCES Vehicle(vehicle_code) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES Route(route_id) ON DELETE CASCADE);

CREATE TABLE Ticket (
    schedule_code       VARCHAR(10) NOT NULL, 
    seat_no             SMALLINT(4) NOT NULL, 
    customer_id         INT NOT NULL,
    occupancy           BOOLEAN NOT NULL,
    purchase_datetime	DATETIME,
    reserved			BOOLEAN NOT NULL, 
    category            VARCHAR(30),
    fare                NUMERIC(8,2),
    PRIMARY KEY (schedule_code, seat_no),
    FOREIGN KEY (customer_id) REFERENCES Customer(user_ptr_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_code) REFERENCES Schedule(code) ON DELETE CASCADE);


CREATE TABLE Leg (
	journey_id	    INT,
	schedule_code	VARCHAR(10),		
    PRIMARY KEY (journey_id, schedule_code),
    FOREIGN KEY (journey_id) REFERENCES Journey(journey_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_code) REFERENCES Schedule(code) ON DELETE CASCADE);*/

-->>> ENTER REVIEW
SELECT comp.name
 FROM Ticket t, Schedule s, Company comp
 WHERE t.customer_id = $userid AND t.schedule_code = s.code AND 
        s.company_id = comp.company_id;

SELECT model_name
 FROM Ticket t, Schedule s, Vehicle v
 WHERE t.customer_id = $ AND t.schedule_code = s.code AND 
        s.vehicle_code = v.vehicle_code;

INSERT INTO Review(user_id, company_id, model_name, comment, rating, date) VALUES (
    $userid, (SELECT company_id FROM Company WHERE name = $compname),
    (SELECT model_name FROM Vehicle_Model WHERE model_name = $modelname AND year = $year LIMIT 1),
    $comment, $rating, $currentdate);

 -->>>>COMP REVIEW
 -- RETRIEVE COMPANY INFORMATION
SELECT name, rating
 FROM Company
 WHERE company_id = $compid;

-- RETRIEVE REVIEW COUNT
SELECT COUNT(*) as rev_count
 FROM Review
 WHERE company_id = $compid;

-- RETRIEVE REVIEWS
SELECT r.model_name, r.comment, r.rating, r.date, u.name
 FROM Review r, User u
 WHERE r.company_id = $compid AND r.customer_id = u.user_id
 ORDER BY r.date ASC;

SELECT r.model_name, r.comment, r.rating, r.date, u.name
 FROM Review r, User u
 WHERE r.company_id = $compid AND r.customer_id = u.user_id
 ORDER BY r.date DESC;

SELECT r.model_name, r.comment, r.rating, r.date, u.name
 FROM Review r, User u
 WHERE r.company_id = $compid AND r.customer_id = u.user_id
 ORDER BY r.rating ASC;

SELECT r.model_name, r.comment, r.rating, r.date, u.name
 FROM Review r, User u
 WHERE r.company_id = $compid AND r.customer_id = u.user_id
 ORDER BY r.rating DESC;

-->>>>>>> VEHICLE REVIEW
-- RETRIEVE THE VEHICLE INFORMATION
SELECT model_name, year, rating
 FROM Vehicle_Model
 WHERE model_name = $modelname AND year = $year;

-- RETRIEVE REVIEW COUNT
SELECT COUNT(*) as rev_count
 FROM Review
 WHERE model_name = $modelname AND year = $year;

-- RETRIEVE REVIEWS
SELECT r.comment, r.rating, r.date, u.name, c.name
 FROM Review r, User u, Company c
 WHERE r.model_name = $modelname AND r.model_year = $year AND r.customer_id = u.user_id AND
        r.company_id = c.company_id
 ORDER BY r.date ASC;

SELECT r.comment, r.rating, r.date, u.name, c.name
 FROM Review r, User u, Company c
 WHERE r.model_name = $modelname AND r.model_year = $year AND r.customer_id = u.user_id AND
        r.company_id = c.company_id
 ORDER BY r.date DESC;
 
 SELECT r.comment, r.rating, r.date, u.name, c.name
 FROM Review r, User u, Company c
 WHERE r.model_name = $modelname AND r.model_year = $year AND r.customer_id = u.user_id AND
        r.company_id = c.company_id
 ORDER BY r.ratinh ASC;

 SELECT r.comment, r.rating, r.date, u.name, c.name
 FROM Review r, User u, Company c
 WHERE r.model_name = $modelname AND r.model_year = $year AND r.customer_id = u.user_id AND
        r.company_id = c.company_id
 ORDER BY r.rating DESC;


-- The search query will be done once in the real application, 
-- we have included it inside a WITH statement in other queries just for readability

-- RETRIEVING PRICES FOR SEARCH RESULTS
 WITH search_result(schedule_code) as
    (SELECT schedule_code
    FROM Schedule s, Route r
    WHERE s.route_id = r.route_id AND r.departure_location = $deploc AND 
        r.arrival_location = $arrloc AND DATE(s.departure_datetime) = $datet AND
        s.transfer_code $isnull AND s.transport_type = $ttype) 
 SELECT DISTINCT  sr.schedule_code, MIN(t.price) as price_to_show
 FROM Ticket t, search_result sr
 WHERE t.schedule_code = sr.schedule_code
 GROUP BY sr.schedule_code;

-- RETRIEVING AVAILABILITY INFORMATION FOR SEARCH RESULTS
 WITH search_result(schedule_code) as
    (SELECT schedule_code
    FROM Schedule s, Route r
    WHERE s.route_id = r.route_id AND r.departure_location = $deploc AND 
        r.arrival_location = $arrloc AND DATE(s.departure_datetime) = $datet AND
        s.transfer_code $isnull AND s.transport_type = $ttype) 
 SELECT sr.schedule_code, CASE
        WHEN (SELECT seat_no FROM Ticket WHERE schedule_code = sr.schedule_code AND status = 'Available' ) EXISTS 
            THEN 'Available' 
        ELSE 'Full'
                END
 FROM search_result sr;

-- RETRIEVING REMAINING ATTRIBUTES FOR SEARCH RESULTS
WITH search_result(schedule_code, departure_datetime, arrival_datetime, company_id, vehicle_code) as
    (SELECT s.schedule_code, s.departure_datetime, s.arrival_datetime, s.company_id, s.vehicle_code
    FROM Schedule s, Route r
    WHERE s.route_id = r.route_id AND r.departure_location = $deploc AND 
        r.arrival_location = $arrloc AND DATE(s.departure_datetime) = $datet AND
        s.transfer_code $isnull AND s.transport_type = $ttype) 
 SELECT sr.schedule_code, c.name, sr.departure_datetime, sr.arrival_datetime, v.model_name
 FROM search_result sr, Company c, Vehicle v
 WHERE sr.company_id = c.company_id AND sr.vehicle_code = v.vehicle_code;

-- RETRIEVE THE TICKET
SELECT *
FROM Ticket
WHERE schedule_code = $sscode AND seat_no = $seatno;

 -- CHECKS
NOT EXISTS (
 WITH selected_schedule(departure_datetime, arrival_datetime) as 
    (SELECT departure_datetime, arrival_datetime
    FROM Schedule
    WHERE schedule_code = $sccode)
 SELECT
 FROM Ticket t, Schedule s, selected_schedule selected
 WHERE t.customer_id = $userid AND t.schedule_code = s.code AND 
        UNIX_TIMESTAMP(s.departure_datetime) <= UNIX_TIMESTAMP(selected.arrival_datetime) AND 
        UNIX_TIMESTAMP(selected.departure_datetime) <= UNIX_TIMESTAMP(s.arrival_datetime));


SELECT DATEDIFF(CURDATE(), birth_date) / 365 AS age
FROM Customer
WHERE user_ptr_id = $userid;


-- PAYMENT
SELECT balance
FROM Customer
WHERE user_ptr_id = $userid;

WITH selected_ticket(price) as 
    (SELECT *
    FROM Ticket
    WHERE schedule_code = $sscode AND seat_no = $seatno)
UPDATE Customer c, selected_ticket t
SET c.balance = c.balance - t.price
WHERE c.user_ptr_id = $userid;


UPDATE Ticket t
SET t.customer_id = $userid, t.status = $status, purchase_datetime = NOW()
WHERE t.schedule_code = $sccode AND t.seat_no = $seatno;





-- TRIGGERS

CREATE TRIGGER delete_owner_trigger
AFTER DELETE ON User
FOR EACH ROW
BEGIN
    UPDATE Ticket
    SET status = 'Available', customer_id = NULL, purchase_datetime = NULL
    WHERE owner_id = OLD.id;
END;


CREATE TRIGGER update_average_rating_trigger
AFTER INSERT ON Review
FOR EACH ROW
BEGIN
    UPDATE Company
    SET rating = (
        SELECT AVG(rating)
        FROM Review
        WHERE company_id = NEW.company_id
    )
    WHERE id = NEW.company_id;
END;

-- EVENT
CREATE EVENT update_ticket_status_event
ON SCHEDULE EVERY 1 HOUR
DO
BEGIN
    UPDATE Ticket
    SET status = 'Available'
    WHERE status = 'Reserved' AND TIMEDIFF(departure_time, NOW()) < '02:00:00';
END;

-- Find the most popular transport types in a month based on people’s preferences:
SELECT s.transport_type, COUNT(*) as total_tickets_sold
FROM Schedule s, Ticket t
WHERE MONTH(s.departure_time) = MONTH(NOW()) AND YEAR(s.departure_time) = YEAR(NOW()) AND
        t.schedule_code = s.code AND t.customer_id is not null
GROUP BY s.transport_type
ORDER BY total_tickets_sold DESC
LIMIT 5;

-- Find the busiest days for ticket purchases in the last week:
SELECT DATE(purchase_time) as date, COUNT(*) as total_tickets_sold
FROM Ticket
WHERE purchase_datetime BETWEEN DATE_SUB(NOW(), INTERVAL 1 WEEK) AND NOW()
GROUP BY DATE(purchase_datetime)
ORDER BY total_tickets_sold DESC
LIMIT 7;

 -- Find the average price of tickets sold in each transport category in the last month:
SELECT s.transport_type, AVG(price) as avg_price
FROM Schedule s, Ticket t
WHERE t.purchase_datetime BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW() AND
        t.schedule_code = s.code AND t.customer_id is not null
GROUP BY s.transport_type;

INSERT INTO User (name, email, password, 'Customer') VALUES (% s, % s, % s)
INSERT INTO Customer (phone, tck, birth_date, gender) VALUES (% s, % s, % s)

INSERT INTO User (name, email, password, 'Company_User') VALUES (% s, % s, % s)
INSERT INTO Company_User (role, company_id) VALUES (% s, % s, % s)