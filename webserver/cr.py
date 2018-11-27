
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#

DB_USER = "yx2444"
DB_PASSWORD = "iz9e4m4l"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"



#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

from functools import wraps
def authorize(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs): #filter
        user = session.get('logged_in',None)#login sign
        if user:
            return fn(*args, **kwargs)#return login request
        else:
            return 'login is needed!'
    return wrapper



def get_first(cursor):
  data = None
  for i in cursor:
    data = i
    break
  return data

def delete_cookie(resp):
    resp.set_cookie('uid', '', expires = 0)
    resp.set_cookie('school_name', '', expires = 0)
    resp.set_cookie('contact_info', '', expires = 0)




@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
'''@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args'''

@app.route('/')
def index():
	context = dict()
	uid = request.cookies.get('uid')
	if uid:
		context = dict(uid = uid)
	return render_template("index.html", **context)

LOGIN_USER = '''SELECT uid FROM users WHERE uid = %s'''

@app.route('/login', methods = ['GET','POST'])
def login():
  if request.method == "GET":
    return render_template("login.html")
  else:
    uid = request.form["uid"]
    cursor = g.conn.execute(LOGIN_USER, uid)
    result = get_first(cursor)
    if result: 
      resp = make_response(redirect("/"))
      delete_cookie(resp)
      resp.set_cookie('uid', request.form["uid"])
      return resp  
    else:
      print "No User Found, please sign up!"
      return render_template("registe.html")


SIGNUP_USER = '''INSERT INTO users (uid, school_name, contact_info) VALUES (%s, %s, %s);'''

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
	if request.method == "GET":
		return render_template("sign_up.html")
	else:
		uid = request.form["uid"]
		school_name = request.form["school_name"]
		contact_info = request.form["contact_info"]
		g.conn.execute(SIGNUP_USER, (uid, school_name, contact_info))
		return render_template('user_page.html')
	
         

@app.route('/items')
def items():
    all_cursor = g.conn.execute(FIND_ALL_ITEMS)
    items = get_all(all_cursor)
    data = dict(items = all_item(items))
    #data = {'iid':56, 'name':"sjdhf",'price':123, 'item_comdition':"new"} 
    return render_template("items.html", **data)

@app.route('/login_page')
def login_page():
	return render_template('login.html')

@app.route('/registe_page')
def registe_page():
        return render_template('registe.html')

@app.route('/index_page')
def index_page():
        return render_template('index.html')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()




















   



  
 
 
  





















