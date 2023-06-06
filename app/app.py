
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import re
import os
import hashlib
from datetime import timedelta, datetime
import time

from search import search_bp
from my_tickets import my_tickets_bp
from company import company_bp
from my_journeys import my_journeys_bp
from db_util import generate_tickets, is_duplicate_route

app = Flask(__name__)

app.secret_key = 'secccret'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pass'
app.config['MYSQL_DB'] = 'db'
  
mysql = MySQL(app)
app.extensions['mysql'] = mysql

app.register_blueprint(search_bp)
app.register_blueprint(my_tickets_bp)   
app.register_blueprint(company_bp)
app.register_blueprint(my_journeys_bp)



# TODO: cursor.close() mysql.connection.close()

@app.route('/')
def test():
    session['type'] = 'Bus'
    #print(is_duplicate_route('Ankara ASTI', 'ESENLER', 5, mysql.connection.cursor(MySQLdb.cursors.DictCursor)))
    #generate_tickets(mysql, 'S004', 1000, 2300, 2000)
    #generate_tickets(mysql, 'S002', 800, 1000, 900)
    #generate_tickets(mysql, 'S003', 1200, 2500, 1900)


    return redirect(url_for('search.search_ticket', type=session['type']))
    


@app.route('/login', methods =['GET', 'POST'])
def login():
    message = request.args.get('message')
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['user_type'] = user['user_type']
            message = 'Logged in successfully!'

            if user['user_type'] == 'Customer':
                cursor.execute(f"SELECT * FROM Customer WHERE user_ptr_id = '{user['user_id']}'")
                customer = cursor.fetchone()
                session['phone'] = customer['phone']
                session['birth_date'] = customer['birth_date']
                session['tck'] = customer['tck']
                session['gender'] = customer['gender']
                session['balance'] = customer['balance']

            elif user['user_type'] == 'Company_User':
                cursor.execute(f"SELECT * FROM Company_User WHERE user_ptr_id = '{user['user_id']}'")
                company_user = cursor.fetchone()
                session['role'] = company_user['role']

                cursor.execute(f"SELECT * FROM Company WHERE company_id = '{company_user['company_id']}'")
                company = cursor.fetchone()
                session['company'] = company


            return redirect(url_for('search.search_ticket', type='ALL'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login_v2.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = request.args.get('message')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name') + " " + request.form.get('lastname')
        tck = request.form.get('tck')
        phone = request.form.get('phone')
        gender = request.form.get('radiogroup1')
        birth_date = request.form.get('birth-date')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM User u, Customer c \
                       WHERE (tck = %s OR u.email = %s) \
                            AND u.user_id = c.user_ptr_id", (tck, email))
        account = cursor.fetchone()
        if account:
            message = 'A user with this TCK number and e-mail already exists!'
            return redirect(url_for('register', message = message))
  
        elif not name or not password or not email or not tck or not phone or not gender or not birth_date:
            message = 'Please fill out all the fields!'
            return redirect(url_for('register', message = message))
        else:
            cursor.execute(f'''INSERT INTO User (email, name, password, user_type) VALUES 
            ('{email}', '{name}', '{password}', 'Customer');''')
            mysql.connection.commit()

            cursor.execute('''SELECT LAST_INSERT_ID() as id;''')
            id = cursor.fetchone().get('id')

            cursor.execute(f'''INSERT INTO Customer (user_ptr_id, balance, tck, phone, gender, birth_date) VALUES
            ({id}, 0, '{tck}', '{phone}', '{gender}', '{birth_date}');''')
            
            mysql.connection.commit()
            message = 'User successfully created!'

            return redirect(url_for('login'))

    else:
        return render_template('register_v2.html', message = message)


# TODO: not finished, logic is not correct
@app.route('/change-type', methods =['POST', 'GET'])
def change_type():
    session['type'] = request.args.get('type')
    return redirect(url_for('search.search_ticket', type=session['type']))



# app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/logout', methods=['POST'])
def logout():
    if session.get('loggedin', None):
        session['loggedin'] = False
        session['user_id'] = None
        session['name'] = None
        session['email'] = None
        session['user_type'] = None
        
        keys = ['balance', 'phone', 'birth_date', 'tck', 'gender', 'role', 'company']
        session.update({key: None for key in keys})

        session.permanent = False  # Remove session permanency

        return redirect(url_for('search.search_ticket', type='ALL'))
    
    else:
        redirect(url_for('login', message="not logged in!"))

@app.route('/reports', methods=['GET', 'POST'])
def reports():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(f'''
SELECT DATE(purchase_datetime) as date, COUNT(*) as total_tickets_sold
FROM Ticket
WHERE purchase_datetime BETWEEN DATE_SUB(NOW(), INTERVAL 1 WEEK) AND NOW()
GROUP BY DATE(purchase_datetime)
LIMIT 7;''')
    results1 = cursor.fetchall()

    cursor.execute('''
    SELECT r.transport_type, AVG(fare) as avg_price
FROM Schedule s, Ticket t, Route r
WHERE t.purchase_datetime BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW() AND
t.schedule_code = s.code AND t.customer_id is not null AND r.route_id = s.route_id 
GROUP BY r.transport_type;
    ''')

    results2 = cursor.fetchall()

    return f"<h2> -- the busiest days for ticket purchases in the last week: {results1} </h2><h2> average price of tickets for each category: {results2} </h2>"


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
