from flask import Flask, Blueprint, current_app, url_for, redirect
from flask import render_template
from flask import request
from flask_mysqldb import MySQL
import MySQLdb.cursors


company_bp = Blueprint('company', __name__, template_folder='templates')

@company_bp.route('/my-schedules', methods=['GET'])
def schedules():
    pass

@company_bp.route('/add-schedule', methods=['GET', 'POST'])
def add_schedule():
    pass
