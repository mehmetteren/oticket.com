from flask import Flask, Blueprint, current_app, url_for, redirect, jsonify, session
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
import MySQLdb.cursors

from db_util import get_all, ticket_checks

my_tickets_bp = Blueprint('my_tickets', __name__, template_folder='templates')

trips_dict = {}

@my_tickets_bp.route('/my-tickets', methods=['GET'])
def my_tickets():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer to see your tickets!'))

    message=request.args.get('message')
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'''
    SELECT t.schedule_code, t.seat_no, t.status, t.category, t.fare, r.departure_location, 
        r.arrival_location, s.departure_datetime, s.arrival_datetime, c.name as company_name
    FROM Ticket t, Schedule s, Route r, Company c
    WHERE s.route_id = r.route_id AND t.schedule_code = s.code 
        AND t.customer_id = {session['user_id']} AND s.company_id = c.company_id
    ''')
    trips_dict['tickets'] = cursor.fetchall()
    return render_template('my_tickets.html', trips=trips_dict['tickets'], message=message)



@my_tickets_bp.route('/pay', methods=['POST'])
def pay():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer'))
    
    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    SELECT *
    FROM Ticket
    WHERE schedule_code = '{request.args.get('schedule_code')}' AND seat_no = {request.args.get('seat_no')}
        AND customer_id = {session['user_id']} AND status = 'Reserved'
    ''')
    ticket = cursor.fetchone()

    result = ticket_checks(session['user_id'], request.args.get('schedule_code'), 
                  ticket['category'], cursor, conflicting_schedules_check=False)
    
    if result['message'] == 'OK':

        cursor.execute(f'''
        UPDATE Customer
        SET balance = balance - {ticket['fare']}
        ''')
        mysql.connection.commit()

        cursor.execute(f'''
        UPDATE Ticket 
        SET status = 'Sold', customer_id = '{session['user_id']}'
        WHERE schedule_code = '{request.args.get('schedule_code')}' AND seat_no = {request.args.get('seat_no')}
        ''')
        mysql.connection.commit()

        cursor.execute(f"SELECT balance FROM Customer WHERE user_ptr_id = '{session['user_id']}'")
        session['balance'] = cursor.fetchone()['balance']

        return redirect(url_for('my_tickets.my_tickets', message='Ticket purchased successfully!'))
    else:
        return redirect(url_for('my_tickets.my_tickets',  message=result['message']))


@my_tickets_bp.route('/cancel', methods=['POST'])
def cancel():
    if not session['loggedin'] or not session['user_type'] == 'Customer':
        return redirect(url_for('login', message='You must be logged in as a customer'))

    mysql = current_app.extensions['mysql']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
    SELECT status, fare
    FROM Ticket
    WHERE schedule_code = '{request.args.get('schedule_code')}' AND seat_no = {request.args.get('seat_no')}
        AND customer_id = {session['user_id']}
    ''')
    ticket = cursor.fetchone()
    status = ticket['status']
    fare = ticket['fare']

    if status == 'Sold':
        cursor.execute(f'''
        UPDATE Customer
        SET balance = balance + {fare}
        WHERE user_ptr_id = {session['user_id']}
        ''')
        mysql.connection.commit()
        session['balance'] += fare
    
    cursor.execute(f'''
    UPDATE Ticket
    SET status = 'Available', customer_id = NULL, purchase_datetime = NULL
    WHERE schedule_code = '{request.args.get('schedule_code')}' AND seat_no = {request.args.get('seat_no')}
        AND customer_id = {session['user_id']} AND (status = 'Reserved' OR status = 'Sold')
    ''')
    mysql.connection.commit()

    return redirect(url_for('my_tickets.my_tickets', message='Ticket cancelled successfully!'))