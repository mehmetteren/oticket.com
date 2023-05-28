import MySQLdb.cursors
from typing import Tuple
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
    