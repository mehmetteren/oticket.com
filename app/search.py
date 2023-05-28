from flask import Flask, Blueprint, current_app, url_for, redirect
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
import MySQLdb.cursors

from db_util import get_all

search_bp = Blueprint('search', __name__, template_folder='templates')

# TODO: add types to routes
# TODO: order the locations
# TODO: drop the view
# TODO: exceptions, no date etc., empty search result
@search_bp.route('/search-ticket/<type>', methods=['GET', 'POST'])
def search_ticket(type):
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'GET':

        locations_dict = get_all(table='Route', attribute='departure_location', cursor=cursor)
        locations = len(locations_dict)*['']

        for i in range(len(locations_dict)):
            locations[i] = locations_dict[i]['departure_location']


        return render_template('search.html', locations=locations)
    
    if request.method == 'POST':
        return redirect(url_for('search.search_results', type=type,
                       departure_location=request.form.get('departure_loc'), arrival_location=request.form.get('arrival_loc'), 
                       date=request.form.get('date'), direct=request.form.get('direct', 0)))
    
@search_bp.route('/search-results', methods=['GET'])
def search_results():
    type=request.args.get('type')
    departure_location=request.args.get('departure_location')
    arrival_location=request.args.get('arrival_location')
    date=request.args.get('date')
    direct=request.args.get('direct')

    print(type, departure_location, arrival_location, date, direct)
    
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if direct:
        isnull = 'NULL'
    else:
        isnull = 'NOT NULL'

    cursor.execute(f"DROP VIEW IF EXISTS search_result;")
    mysql.connection.commit()

    cursor.execute(f'''
    CREATE VIEW search_result AS 
        SELECT s.code as schedule_code, s.departure_datetime, s.arrival_datetime, s.company_id, s.vehicle_code
        FROM Schedule s, Route r
        WHERE s.route_id = r.route_id AND r.departure_location = '{departure_location}' AND 
            r.arrival_location = '{arrival_location}' AND DATE(s.departure_datetime) = '{date}' AND
            s.transfer_code IS {isnull} AND s.transport_type = '{type}'; ''')

    mysql.connection.commit()

    price_sql = f'''
    SELECT DISTINCT  sr.schedule_code, MIN(t.fare) as price_to_show
    FROM search_result sr, Ticket t
    WHERE t.schedule_code = sr.schedule_code
    GROUP BY sr.schedule_code
    '''

    availability_sql = f'''
    SELECT sr.schedule_code, 
        CASE
            WHEN EXISTS (SELECT seat_no 
                        FROM Ticket t 
                        WHERE t.schedule_code = sr.schedule_code AND t.status = 'Available') THEN 'Available'
            ELSE 'Full'
        END as status
    FROM search_result sr'''

    vehicle_sql = f'''
    SELECT sr.schedule_code, vem.year, vem.model_name
    FROM search_result sr, Vehicle vv, Vehicle_Model vem
    WHERE sr.vehicle_code = vv.vehicle_code AND vv.year = vem.year 
        AND vv.model_name = vem.model_name'''

    cursor.execute(f''' 
    SELECT s.schedule_code, c.name as company_name, TIME(s.departure_datetime) as departure_time, 
        TIME(s.arrival_datetime) as arrival_time, veh.year, veh.model_name, av.status, pr.price_to_show 
    FROM search_result s, Company c, ({vehicle_sql}) as veh, ({availability_sql}) as av, ({price_sql}) as pr
    WHERE s.company_id = c.company_id AND s.schedule_code = veh.schedule_code AND s.schedule_code = av.schedule_code
        AND s.schedule_code = pr.schedule_code
    ''')

    results = cursor.fetchall()

    locations_dict = get_all(table='Route', attribute='departure_location', cursor=cursor)
    locations = len(locations_dict)*['']

    for i in range(len(locations_dict)):
        locations[i] = locations_dict[i]['departure_location']


    return render_template('trips.html', trips=results, departure_location=departure_location, 
                           arrival_location=arrival_location, locations=locations)

    # return f"<h3>{type, departure_location, arrival_location, date, direct}</h3><h3>{e}</h3>"


