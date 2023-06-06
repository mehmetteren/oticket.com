from flask import Flask, Blueprint, current_app, url_for, redirect, session
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
from db_util import is_duplicate_route, generate_tickets, get_all
import MySQLdb.cursors


company_bp = Blueprint('company', __name__, template_folder='templates')

@company_bp.route('/schedules', methods=['GET'])
def schedules():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to see schedules page!'))

    message=request.args.get('message')
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    SELECT *
    FROM Vehicle v
    WHERE v.company_id = {session['company']['company_id']} 
    ''')

    vehicles = cursor.fetchall()


    cursor.execute(f'''
    SELECT s.code as schedule_code, s.departure_datetime, s.arrival_datetime,
        r.departure_location, r.arrival_location, r.transport_type as transportation_type, s.vehicle_code
    FROM Schedule s, Route r
    WHERE s.route_id = r.route_id AND s.company_id = {session['company']['company_id']}
    ''')

    schedules = cursor.fetchall()

    cursor.execute(f'''
    SELECT t.schedule_code, t.fare, t.category
    FROM Ticket t, Schedule s
    WHERE t.schedule_code = s.code AND s.company_id = {session['company']['company_id']}
    GROUP BY t.schedule_code, t.fare, t.category
    ''')

    query_result = cursor.fetchall()

    prices_dict = {}
    for row in query_result:
        prices_dict[row['schedule_code']] = {}
 
    for row in query_result:
        prices_dict[row['schedule_code']][row['category']] = row['fare']

    locations_dict = get_all(table='Route', attribute='departure_location', cursor=cursor)
    locations = len(locations_dict)*['']

    for i in range(len(locations_dict)):
        locations[i] = locations_dict[i]['departure_location']

    return render_template('company_schedules.html', schedules=schedules, prices=prices_dict, 
                            message=message, vehicles=vehicles, locations=locations)


@company_bp.route('/add-schedule', methods=['GET', 'POST'])
def add_schedule():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to see schedules page!'))

    if request.method == 'POST':
        mysql = current_app.extensions['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(f'''
        SELECT name
        FROM Company
        WHERE company_id = {session['company']['company_id']}
        ''')
        res1 = cursor.fetchone()

        cursor.execute(f'''
        SELECT s1.code as schedule_code, s1.departure_datetime as dep, s1.arrival_datetime as arr
        FROM Vehicle v, Schedule s1     
        WHERE v.vehicle_code = '{request.form.get('vehicle_code')}' AND v.vehicle_code = s1.vehicle_code 
            AND (UNIX_TIMESTAMP(s1.departure_datetime) <= UNIX_TIMESTAMP('{request.form.get('arrival_datetime')}') AND 
            UNIX_TIMESTAMP('{request.form.get('departure_datetime')}') <= UNIX_TIMESTAMP(s1.arrival_datetime));
        ''')
        conflicting_schedules = cursor.fetchall()

        if conflicting_schedules:
            return redirect(url_for(f"company.schedules', message=f'Vehicle is not available for that time interval! \
                                    Conflicting schedule code(s):  {[c['schedule_code'] for c in conflicting_schedules]}"))


        if res1:
            try:
                #if not is_duplicate_route
                cursor.execute(f'''
                SELECT route_id FROM Route
                WHERE departure_location = '{request.form.get('departure_location')}' AND
                arrival_location = '{request.form.get('arrival_location')}';
                ''')

                route_id = cursor.fetchone().get('route_id')

                cursor.execute(f'''
                INSERT INTO Schedule (code, departure_datetime, arrival_datetime, route_id, company_id, vehicle_code) VALUES
                ('{request.form.get('schedule_code')}', '{request.form.get('departure_datetime')}', 
                '{request.form.get('arrival_datetime')}', {route_id}, {session['company']['company_id']},
                '{request.form.get('vehicle_code')}'); 
                ''')
                mysql.connection.commit()

                generate_tickets(mysql, request.form.get('schedule_code'), request.form.get('economy_price'),
                                    request.form.get('firstclass_price'), request.form.get('business_price'))
                
                return redirect(url_for('company.schedules', message='Schedule added successfully!'))
            except Exception as e:
                return redirect(url_for('company.schedules', message=e.args))
        else:
            return redirect(url_for('company.schedules', message='error2!'))
        



@company_bp.route('/delete-schedule', methods=['GET', 'POST'])
def delete_schedule():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to see schedules page!'))
    

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    schedule_code = request.args.get('schedule_code')

    cursor.execute(f'''
    DELETE FROM Schedule
    WHERE code='{request.args.get('schedule_code')}' AND company_id = {session['company']['company_id']}
    ''')
    mysql.connection.commit()

    return redirect(url_for('company.schedules', message='Schedule deleted successfully!'))


@company_bp.route('/my-vehicles', methods=['GET'])
def vehicles():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to see your tickets!'))

    message=request.args.get('message')
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    SELECT *
    FROM Vehicle v, Vehicle_Model vm
    WHERE v.model_name = vm.model_name AND v.year = vm.year AND
                   v.company_id = {session['company']['company_id']} 
    ''')

    result = cursor.fetchall()

    return render_template('company_vehicles.html', vehicles=result, message=message)

@company_bp.route('/add-vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to add a vehicle!'))
    
    if request.method == 'POST':
        
        mysql = current_app.extensions['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute(f'''
            INSERT INTO Vehicle_Model (model_name, year, transport_type) VALUES
            ('{request.form.get('vehicle-model-name')}', {request.form.get('vehicle-model-year')}, '{request.form.get('transportation-type')}');
            ''')
            mysql.connection.commit()

        except MySQLdb._exceptions.IntegrityError:
            pass

        cursor.execute(f'''
        INSERT INTO Vehicle (vehicle_code, availability, capacity_firstclass, capacity_economy, capacity_business, model_name, year, company_id)
        VALUES
        ('{request.form.get('vehicle-code')}', TRUE, {request.form.get('first-class-capacity')}, 
        {request.form.get('economy-capacity')}, {request.form.get('business-capacity')}, 
        '{request.form.get('vehicle-model-name')}', {request.form.get('vehicle-model-year')}, {session['company']['company_id']});
        ''')

        mysql.connection.commit()

        return redirect(url_for('company.vehicles', message='Vehicle added successfully!'))

                      

@company_bp.route('/delete-vehicle', methods=['GET', 'POST'])
def delete_vehicle():
    if not session['loggedin'] or not session['user_type'] == 'Company_User':
        return redirect(url_for('login', message='You must be logged in as a company user to delete vehicles!'))
    

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    DELETE FROM Vehicle
    WHERE vehicle_code='{request.args.get('vehicle_code')}' AND company_id = {session['company']['company_id']}
    ''')
    mysql.connection.commit()

    return redirect(url_for('company.vehicles', message='Vehicle deleted successfully!'))
