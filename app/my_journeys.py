from flask import Flask, Blueprint, current_app, url_for, redirect, jsonify, session
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
import MySQLdb.cursors

from db_util import get_all, ticket_checks
from search import trips_dict

my_journeys_bp = Blueprint('my_journeys', __name__, template_folder='templates')

@my_journeys_bp.route('/my-journeys', methods=['GET'])
def my_journeys():

    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer to see your journeys!'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    SELECT journey_id, journey_name, all_booked
    FROM Journey
    WHERE customer_id = {session['user_id']};
    ''')
    journeys = cursor.fetchall()

    return render_template('my_journeys.html', journeys=journeys, message=request.args.get('message'))


@my_journeys_bp.route('/journey-info', methods=['GET'])
def journey_info():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer to see your journeys!'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    journey_id = request.args.get('journey_id')

    cursor.execute(f'''
    SELECT s.code as schedule_code, c.name as company_name, s.departure_datetime, s.arrival_datetime, 
        r.departure_location, r.arrival_location, p.price_to_show 
    FROM Schedule s, Leg l, Journey j, Company c, Route r, (    
        SELECT DISTINCT  sr.schedule_code, MIN(t.fare) as price_to_show
        FROM search_result sr, Ticket t
        WHERE t.schedule_code = sr.schedule_code
        GROUP BY sr.schedule_code) as p
    WHERE j.journey_id = {journey_id} AND j.customer_id = {session['user_id']}
            AND	s.company_id = c.company_id 
            AND r.route_id = s.route_id
            AND s.code = l.schedule_code 
            AND j.journey_id = l.journey_id 
            AND p.schedule_code = s.code;
    ''')

    trips = cursor.fetchall()

    response = {
        'trips': trips,
    }
    return jsonify(response)


@my_journeys_bp.route('/create-journey', methods=['POST'])
def create_journey():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer to create a journey!'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    journey_name = request.form.get('journey_name')

    cursor.execute(f'''
    INSERT INTO Journey (customer_id, journey_name, all_booked) VALUES
    ({session['user_id']}, '{journey_name}', FALSE)
    ''')
    mysql.connection.commit()

    return redirect(url_for('my_journeys.my_journeys', message='Journey created successfully!'))

@my_journeys_bp.route('/delete-journey', methods=['POST'])
def delete_journey():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer to delete a journey!'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    journey_id = request.args.get('journey_id')

    cursor.execute(f'''
    DELETE
    FROM Journey
    WHERE journey_id = {journey_id} AND customer_id = {session['user_id']}
    ''')

    mysql.connection.commit()

    cursor.execute(f'''
    DELETE              
    FROM Leg
    WHERE journey_id = {journey_id}
    ''')

    mysql.connection.commit()

    return redirect(url_for('my_journeys.my_journeys', message='Journey deleted successfully!'))


@my_journeys_bp.route('/add-to-journey', methods=['POST'])
def add_to_journey():
    journey_id = request.form.get('journey') # this is the journey_id
    schedule_code = request.args.get('schedule_code')

    if journey_id and schedule_code and session['loggedin']:
        mysql = current_app.extensions['mysql']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # security check
        cursor.execute(f'''
        SELECT journey_id
        FROM Journey
        WHERE journey_id = {journey_id} AND customer_id = {session['user_id']}
        ''')

        if not cursor.fetchone():
            return "<h2>WTF ARE YOU DOING</h2>"
        #redirect(url_for('my_journeys.my_journeys', message='You do not have permission to add to this journey!'))
        try:
            cursor.execute(f'''
            INSERT INTO Leg (journey_id, schedule_code) VALUES
            ({journey_id}, '{schedule_code}')
            ''')
            mysql.connection.commit()

            return render_template('trips.html', trips=trips_dict['search_results'] , departure_location=trips_dict['departure_location'], 
                            arrival_location=trips_dict['arrival_location'], locations=trips_dict['locations'],  message='Added to journey successfully!',
                            journeys=trips_dict['journeys'])
        
        except MySQLdb.IntegrityError:
            return render_template('trips.html', trips=trips_dict['search_results'] , departure_location=trips_dict['departure_location'], 
                            arrival_location=trips_dict['arrival_location'], locations=trips_dict['locations'],  message='Trip already in journey!',
                            journeys=trips_dict['journeys'])

    else:
        return redirect(url_for('login', message='You must be logged in as a customer!'))
    


@my_journeys_bp.route('/remove-from-journey', methods=['POST'])
def remove_from_journey():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    journey_id = request.args.get('journey_id')
    schedule_code = request.args.get('schedule_code')

    cursor.execute(f'''
    SELECT journey_id
    FROM Journey
    WHERE journey_id = {journey_id} AND customer_id = {session['user_id']}
    ''')

    if not cursor.fetchone():
        return "<h2>WTF ARE YOU DOING</h2>"
    #redirect(url_for('my_journeys.my_journeys', message='You do not have permission to add to this journey!'))

    cursor.execute(f'''
    DELETE FROM Leg
    WHERE journey_id = {journey_id} AND schedule_code = '{schedule_code}'
    ''')

    mysql.connection.commit()
    
    return redirect(url_for('my_journeys.my_journeys', message='Removed from journey successfully!'))

@my_journeys_bp.route('/book-tickets', methods=['POST'])
def book_tickets():
    pass