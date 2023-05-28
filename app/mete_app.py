# beginning of a flask mysql app

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import hashlib
import datetime
import time


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/login")
def login():
    return "<h3>hello login</h3>"

@app.route("/signup")
def signup():
    return  render_template("signup.html")

@app.route("/stats")
def stats():
    tickets_sold = 1650
    male_customers = 650
    female_customers = 1000
    bus_tickets = 1000
    train_tickets = 250
    flight_tickets = 400
    return render_template('company_stats.html', 
                           tickets_sold=tickets_sold, 
                           male_customers=male_customers,
                           female_customers = female_customers,
                           bus_tickets = bus_tickets,
                           train_tickets = train_tickets,
                           flight_tickets = flight_tickets)
    
##### MODIFIED PART
schedules = []
schedule_id_counter = 0
    
@app.route("/schedules")
def schedule():
    return  render_template("company_schedules.html", schedules=schedules)

schedules = []
schedule_id_counter = 0

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    global schedule_id_counter

    start_place = request.form['start_place']
    end_place = request.form['end_place']
    departure_time = request.form['departure_time']
    date = request.form['date']
    transportation_type = request.form['transportation_type']
    price = request.form['price']

    schedule = {
        'schedule_id': schedule_id_counter,
        'start_place': start_place,
        'end_place': end_place,
        'departure_time': departure_time,
        'date': date,
        'transportation_type': transportation_type,
        'price': price
    }

    schedules.append(schedule)
    schedule_id_counter += 1

    return redirect('/schedules') 

@app.route('/delete/<int:schedule_id>', methods=['GET'])
def delete_schedule(schedule_id):
    global schedules

    schedules = [schedule for schedule in schedules if schedule['schedule_id'] != schedule_id]

    return redirect('/schedules')

#######
    
if(__name__) == "__main__":
    #app.debug = True
    app.run()
