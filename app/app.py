
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import re
import os
import hashlib
from datetime import timedelta, datetime
import time

from search import search_bp
from db_util import generate_tickets

app = Flask(__name__)

app.secret_key = 'secccret'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pass'
app.config['MYSQL_DB'] = 'db'
  
mysql = MySQL(app)
app.extensions['mysql'] = mysql

app.register_blueprint(search_bp)



# TODO: cursor.close() mysql.connection.close()


@app.route('/')
def test():
    return redirect(url_for('search.search_ticket', type='ALL'))
    


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
                session['balance'] = customer['balance']
                session['phone'] = customer['phone']
                session['birth_date'] = customer['birth_date']
                session['tck'] = customer['tck']
                session['gender'] = customer['gender']

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
@app.route('/change-type', methods =['POST'])
def change_type():
    session['transportation_type'] = request.args.get('transportation_type')



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



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
