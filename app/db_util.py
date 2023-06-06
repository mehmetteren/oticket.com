import MySQLdb.cursors
import string
from typing import Tuple
import Levenshtein

def get_all(table, attribute='*', cursor=None, where='TRUE'):
    if cursor:       
        cursor.execute(f"SELECT {attribute} FROM {table} WHERE {where}")
        return cursor.fetchall()
    else:
        print("Error: No cursor provided")
        return None
    

def get_some(table, attribute='*', cursor=None, where='TRUE', limit=0):
    if cursor:       
        cursor.execute(f"SELECT {attribute} FROM {table} WHERE {where} LIMIT {limit}")
        return cursor.fetchall()
    else:
        print("Error: No cursor provided")
        return None
    

# TODO: maybe change how the seat_no s are generated
# TODO: maybe provide more price options and something
def generate_tickets(mysql, schedule_code, economy_price:float, first_price:float, business_price:float):

    if schedule_code and mysql: 

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'''
        SELECT capacity_firstclass, capacity_business, capacity_economy 
        FROM Vehicle v, Schedule s 
        WHERE v.vehicle_code = s.vehicle_code AND s.code = '{schedule_code}'
        ''')
        capacities = cursor.fetchone()
        eco_count = capacities['capacity_economy']
        first_count = capacities['capacity_firstclass']
        bus_count = capacities['capacity_business']

        for i in range(1, first_count + 1):
            cursor.execute(f'''INSERT INTO Ticket (schedule_code, seat_no, status, category, fare) VALUES 
                           ('{schedule_code}', {i}, 'Available', 'First Class', {first_price})''')
        mysql.connection.commit() 

        for x in range(first_count + 1, first_count + bus_count + 1):
            cursor.execute(f'''INSERT INTO Ticket (schedule_code, seat_no, status, category, fare) VALUES 
                           ('{schedule_code}', {x}, 'Available', 'Business', {business_price})''')
        mysql.connection.commit() 

        for y in range(bus_count + first_count + 1, eco_count + first_count + bus_count + 1):
            cursor.execute(f'''INSERT INTO Ticket (schedule_code, seat_no, status, category, fare) VALUES 
                           ('{schedule_code}', {y}, 'Available', 'Economy', {economy_price})''')
        mysql.connection.commit()   

    else:
        print("Error: None value provided for schedule_code or mysql connection")
    

def ticket_checks(user_id, schedule_code, category,  cursor, conflicting_schedules_check=True) -> dict:
    cursor.execute(f'''
    SELECT balance
    FROM Customer
    WHERE user_ptr_id = {user_id};''')
    balance = cursor.fetchone()['balance']

    # Check if ticket is available
    cursor.execute(f'''
    SELECT *
    FROM Ticket
    WHERE category = '{category}' AND status = 'Available' AND schedule_code = '{schedule_code}'
    LIMIT 1
    ''')
    ticket = cursor.fetchone()

    cursor.execute(f'''
    SELECT DATEDIFF(CURDATE(), birth_date) / 365 AS age
    FROM Customer
    WHERE user_ptr_id = {user_id};''')
    age = cursor.fetchone()['age']

    if not ticket:
        return {'message':"Ticket is not available!", 'seat_no': None}

    # Check if user has enough balance
    if ticket['fare'] > balance:
        return {'message':"Not enough balance!", 'ticket': ticket}

    # Check if user is old enough
    if age < 18:
        return {'message':"You are not old enough!", 'seat_no': None}

    if conflicting_schedules_check:
        # Check conflicting schedules
        cursor.execute(f'''
        SELECT t.schedule_code as code, s1.departure_datetime as dep, s1.arrival_datetime as arr
        FROM Ticket t, Schedule s1,     
        (SELECT s2.departure_datetime, s2.arrival_datetime
            FROM Schedule s2
            WHERE s2.code = '{schedule_code}') selected
        WHERE t.customer_id = {user_id} AND t.schedule_code = s1.code 
            AND (UNIX_TIMESTAMP(s1.departure_datetime) <= UNIX_TIMESTAMP(selected.arrival_datetime) AND 
            UNIX_TIMESTAMP(selected.departure_datetime) <= UNIX_TIMESTAMP(s1.arrival_datetime));
        ''')
        conflicting_schedules = cursor.fetchall()

        if conflicting_schedules:
            # {sch['dep']} - {sch['arr']}
            return {'message':"You have conflicting schedules! Schedule code(s): " + 
                    ' | '.join(f"{sch['code']}" for sch in conflicting_schedules), 
                    'seat_no': None}
    
    return {'message':"OK", 'ticket': ticket}


def is_duplicate_route(departure, arrival, threshold, cursor):
    # Retrieve existing routes from the Route table
    
    existing_routes = get_all('Route', attribute='departure_location, arrival_location', cursor=cursor)

    # Check similarity between user input and existing routes
    for route in existing_routes:
        existing_departure = route['departure_location'].lower()
        existing_arrival = (route['arrival_location']).lower()
        departure_distance = Levenshtein.distance(departure.lower(), existing_departure)
        arrival_distance = Levenshtein.distance(arrival.lower(), existing_arrival)

        if departure_distance <= threshold and arrival_distance <= threshold:
            return True  # Similar route already exists

    return False  # No similar route found