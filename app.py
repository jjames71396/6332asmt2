import math
import pandas as pd
import os, uuid
from sqlalchemy import create_engine
import pymysql
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)


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
    arg = request.form.get('name')
    args = arg.split(',')
    
    r = float(args[2])
    f = float(args[0])
    l = float(args[1])
    ns = r/111        # North-south distance in degrees (69 for miles, 111 for km)
    ew = ns / math.cos(f) # East-west distance in degrees
    sf = f-ns
    nf = f+ns
    wl = l-ew
    el = l+ew
    
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
    
    if sf < nf and el < wl:
        result = pd.read_sql_query(query.format(sf,nf,el,wl, typ), engine)
    elif sf < nf and wl < el:
        result = pd.read_sql_query(query.format(sf,nf,wl,el, typ), engine)
    elif nf < sf and wl < el:
        result = pd.read_sql_query(query.format(nf,sf,wl,el, typ), engine)
    elif nf < sf and el < wl:
        result = pd.read_sql_query(query.format(nf,sf,el,wl, typ), engine)          
        
        
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/range', methods=['POST'])
def range():
    arg = request.form.get('name')
    args = arg.split(',')
    
    query = '''SELECT *
    FROM earthquakes
    WHERE time BETWEEN {} AND {}
    AND mag BETWEEN {} AND {}
    AND type = {}
    '''
    result = None
    dfinish = "'2023-05-10T23:20:14.660Z'" # Enter your desired start date/time in the string
    dstart = "'2023-05-10T20:20:14.660Z'"
    
    result = pd.read_sql_query(query.format(args[0], args[1], float(args[2]), float(args[3]), typ), engine)
    
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


@app.route('/count', methods=['POST'])
def count():
    query = '''SELECT *
    FROM earthquakes
    WHERE type = {}
    AND
    mag > {}
    '''
    result = None
    arg = request.form.get('name')
    result = pd.read_sql_query(query.format(typ, float(arg)), engine)
    if result is not None:
       return render_template('count.html', name = len(result), tables=[result.to_html(classes='data', header="true")])
    else:
       print('Request for count page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
