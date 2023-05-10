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

