#Programming Assignment 2
#Jordan James 1001879608
#CSE 6332-002

import math
import pandas as pd
import os, uuid
from sqlalchemy import create_engine
import pymysql
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

# Setting up initial parameters
typ = "'earthquake'"
r = 5000
f = 40
l = 1
ns = r/111        # North-south distance in degrees (69 for miles, 111 for km)
ew = ns / math.cos(f) # East-west distance in degrees
sf = f-ns
nf = f+ns
wl = l-ew
el = l+ew

# Setting up database connection parameters
server = 'q2server.mysql.database.azure.com'
database = 'testdb'
username = 'servadmin'
password = '#hackme123'
port = '3306'

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}",
    connect_args={"ssl": {"ssl_ca": "DigiCertGlobalRootCA.crt.pem"}},
)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/location', methods=['POST'])
def location():
    # Retrieving data from the request form
    arg = request.form.get('name')
    args = arg.split(',')
    
    # Calculating latitude and longitude boundaries
    r = float(args[2])
    f = float(args[0])
    l = float(args[1])
    ns = r/111        # North-south distance in degrees (69 for miles, 111 for km)
    ew = ns / math.cos(f) # East-west distance in degrees
    sf = f-ns
    nf = f+ns
    wl = l-ew
    el = l+ew
    
    # SQL query to retrieve earthquakes within the specified boundaries
    query = '''SELECT *
    FROM earthquakes
    WHERE latitude BETWEEN {} AND {}
    AND
    longitude BETWEEN {} AND {}
    AND
    type = {}
    '''
    result = None
    dfinish = "'2023-05-10T23:20:14.660Z'" # Enter your desired start date/time in the string
    dstart = "'2023-05-10T20:20:14.660Z'"
    
    # Executing the SQL query based on different boundary scenarios
    if sf < nf and el < wl:
        result = pd.read_sql_query(query.format(sf,nf,el,wl, typ), engine)
    elif sf < nf and wl < el:
        result = pd.read_sql_query(query.format(sf,nf,wl,el, typ), engine)
    elif nf < sf and wl < el:
        result = pd.read_sql_query(query.format(nf,sf,wl,el, typ), engine)
    elif nf < sf and el < wl:
        result = pd.read_sql_query(query.format(nf,sf,el,wl, typ), engine)          
        
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/range', methods=['POST'])
def range():
    # Retrieving data from the request form
    arg = request.form.get('name')
    args = arg.split(',')
    
    # SQL query to retrieve earthquakes within the specified time and magnitude range
    query = '''SELECT *
    FROM earthquakes
    WHERE time BETWEEN {} AND {}
    AND mag BETWEEN {} AND {}
    AND type = {}
    '''
    result = None
    dfinish = "'2023-05-10T23:20:14.660Z'" # Enter your desired start date/time in the string
    dstart = "'2023-05-10T20:20:14.660Z'"
    
    # Executing the SQL query
    result = pd.read_sql_query(query.format(args[0], args[1], float(args[2]), float(args[3]), typ), engine)
    
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/count', methods=['POST'])
def count():
    # SQL query to retrieve earthquakes of a specific type and magnitude greater than a threshold
    query = '''SELECT *
    FROM earthquakes
    WHERE type = {}
    AND
    mag > {}
    '''
    result = None
    arg = request.form.get('name')
    result = pd.read_sql_query(query.format(typ, float(arg)), engine)
    
    # Rendering the template with the query result
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()
