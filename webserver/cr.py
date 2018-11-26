#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import psycopg2
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, make_response, url_for
# from DB import 
# from Web

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath("__file__")), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "yx2444"
DB_PASSWORD = "iz9e4m4l"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None


@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  context = dict()
  uid = request.cookies.get('uid')
  if uid:
    context = dict(uid = uid)
  

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)


def get_first(cursor):
  data = None
  for i in cursor:
    data = i
    break
  return data


SIGNUP_USER = '''INSERT INTO users (uid, school_name, contact_info)
                VALUES (%s, %s, %s);'''

GET_LAST_USER_ID_SQL = "SELECT MAX(uid) FROM users;"

@app.route('/sign_up', methods = ["POST", "GET"])
def signup():
   try:
    if request.method == "GET":
      return render_template("sign_up.html")
    else:
      uid = request.form["uid"]
      school_name = request.form["school_name"]
      contact_info = request.form["contact_info"]
      g.conn.execute(SIGNUP_USER, (uid, school_name, contact_info))
      cursor = g.conn.execute(GET_LAST_USER_ID_SQL)
      result = get_first_result(cursor)
      if cursor:
        resp = make_response(redirect("/"))
        delete_exsting_user_cookie(resp)
        resp.set_cookie('uid', str(result[0]))
        resp.set_cookie('school_name', request.form["school_name"])
        resp.set_cookies("contact_info", request.form["contact_info"])
        return resp
      else:
                # TODO(Chris): Handle the error format for signup,
                # ex. enter age with not numbers or some db callback
                print "Something happens in DB"
                return render_template("sign_up.html")
   except:
      return redirect("/")


LOGIN_USER = '''SELECT uid FROM users WHERE uid = %s'''

def delete_cookie(resp):
    resp.set_cookie('uid', '', expires = 0)
    resp.set_cookie('school_name', '', expires = 0)
    resp.set_cookie('contact_info', '', expires = 0)


@app.route('/login', methods = ["POST", "GET"])
def login():
  if request.method == "GET":
    return render_template("login.html")
  else:
    uid = request.form["uid"]
    cursor = g.conn.execute(LOGIN_USER, uid)
    result = get_first(cursor)
    if result: 
      resp = make_response(redirect("/"))
      delete_existing_user_cookie(resp)
      resp.set_cookie('uid', request.form["uid"])
      return resp  
    else:
      print "No User Found, please sign up!"
      return render_template("sign_up.html")


def all_item(item):
  if item:
    return [{'info': item[0],       \
    'location': item[1],            \
    'item_condition': item[2],      \
    'iid': item[3],                 \
    'uid': item[4],                 \
    'price': item[5]}               \
    for i in item]
  return item

FIND_ALL_ITEMS = ''' select * from item left join book on item.iid = book.iid
                       left join clothing on item.iid = clothing.iid
                       left join service on item.iid = service.iid'''

def get_all(cursor):
    return [result for result in cursor]

@app.route('/items')
def items():
    all_cursor = g.conn.execute(FIND_ALL_ITEMS)
    items = get_all(all_cursor)
    data = dict(items = all_item(items))
    #data = {'iid':56, 'name':"sjdhf",'price':123, 'item_comdition':"new"} 
    return render_template("items.html", **data)



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






  
  
  
  
  
  
 
    
  
      




















































