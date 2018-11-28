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

  

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")



def set_cookie_redirct(cookie_key, cookie_val, redirct_url):
    resp = make_response(redirect(redirct_url))
    resp.set_cookie(cookie_key, cookie_val)
    return resp

def delete_cookie(resp):
    resp.set_cookie('uid', '', expires = 0)
    
def xstr(s):
    if s is None:
        return ''
    else:
        return str(s)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == "GET":
    return render_template("login.html")
  else:
      uid = request.form["uid"]
      temp = [uid]
      print(temp)

      cursor = g.conn.execute('select uid from users where uid =\'' + uid + '\'')
      result = [r for r in cursor]
      print(result)
      if  len(result) != 0:
        resp = make_response(render_template('user_page.html'))
        delete_cookie(resp)
        resp.set_cookie('uid', uid)
        return resp
      else :
            return render_template('not_found.html')
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "GET":
        return render_template("sign_up.html")
    else:
        uid = request.form['uid']
        school_name = request.form['school_name']
        contact_info = request.form['contact_info']
        r = g.conn.execute('select uid from users where uid = \''+ uid+'\'')
        # if username already exists
        res = [re for re in r]
        if(len(res) != 0):
            return render_template('userid_error.html')
        else:
            g.conn.execute('insert into users (uid, school_name, contact_info) values(\''+ str(uid) +'\',\'' + str(school_name) +'\',\'' + str(contact_info)+'\')')
            return render_template('login.html')    
@app.route('/all_items')
def all_items():
  cursor = g.conn.execute('select * from item')
  info = []
  uid = request.cookies.get('uid')
  
  for r in cursor:
    tmp = {}
    tmp['Item Information'] = str(r[0])
    tmp['Location'] = str(r[1])
    tmp['Item Condition'] = str(r[2])
    tmp['Item ID'] = str(r[3])
    tmp['Owner ID'] = str(r[4])
    tmp['Price'] = str(r[5])
    info.append(tmp)
  cursor.close()
  return render_template('all_items.html',data=info)

@app.route('/myitem')
def myitem():
	uid = request.cookies.get('uid')
        cursor = g.conn.execute('select * from item where uid =\'' + uid + '\' ')
        info = []
        for r in cursor:
		tmp = {}
    		tmp['Item Information'] = str(r[0])
    		tmp['Location'] = str(r[1])
  		tmp['Item Condition'] = str(r[2])
    		tmp['Item ID'] = str(r[3])
    		tmp['Owner ID'] = str(r[4])
 		tmp['Price'] = str(r[5])
   		info.append(tmp)
   		 # can also be accessed using result[0]
        cursor.close()
        return render_template('myitem.html',data=info)

@app.route('/user_reviews')
def user_reviews():
  uid = request.cookies.get('uid')
  cursor = g.conn.execute('select * from review where receiverid = \''+ uid +'\'')
  info = []
  for r in cursor:
    tmp = {}
    tmp['Rating'] = str(r[0])
    tmp['Review Content'] = str(r[1])
    tmp['Review ID'] = str(r[2])
    tmp['Writer ID'] = str(r[4])
    info.append(tmp)
  cursor.close()
  return render_template('user_reviews.html',data=info)

	
	
@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == "GET":
        return render_template("post.html")
    else:
        uid = request.cookies.get('uid')
        info = request.form['info']
        location = request.form['location']
	item_condition = request.form['item_condition']
	#iid= request.form['iid']
	price = request.form['price']
        g.conn.execute('insert into item (uid,info,location,item_condition,price) values(\''+ str(uid) +'\',\'' + str(info) +'\',\''+ str(location) +'\',\''+ str(item_condition) +'\',\''+ str(price) +'\')')
        return render_template('post.html')         

@app.route('/clothing', methods=['GET', 'POST'])
def clothing():
    if request.method == "GET":
        return render_template("clothing.html")
    else:
        uid = request.cookies.get('uid')
        brand = request.form['brand']
        size = request.form['size']
	res = g.conn.execute('select count(iid) from item')
	iid = res.fetchall()[0][0]
        g.conn.execute('insert into clothing (ownerid, brand, size,iid) values(\''+ str(uid) +'\',\'' + str(brand) +'\',\''+ str(size) +'\',\''+str(iid)+'\')')
        return render_template('clothing.html')         

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == "GET":
        return render_template("book.html")
    else:
        uid = request.cookies.get('uid')
        version = request.form['version']
        subject = request.form['subject']
	res = g.conn.execute('select count(iid) from item')
	iid = res.fetchall()[0][0]
        g.conn.execute('insert into book (ownerid, version, subject,iid) values(\''+ str(uid) +'\',\'' + str(version) +'\',\''+ str(subject) +'\',\''+str(iid)+'\')')
        return render_template('book.html')         

@app.route('/service', methods=['GET', 'POST'])
def service():
    if request.method == "GET":
        return render_template("service.html")
    else:
        uid = request.cookies.get('uid')
        duration = request.form['duration']
	res = g.conn.execute('select count(iid) from item')
	iid = res.fetchall()[0][0]
        g.conn.execute('insert into clothing (ownerid, duration,iid) values(\''+ str(uid) +'\',\'' + str(duration) +'\',\''+str(iid)+'\')')
        return render_template('service.html')     


@app.route('/all_clothing')
def all_clothing():
  cursor = g.conn.execute('select i.info, i.location, i.item_condition, i.iid, i.uid, i.price, c.brand, c.size from clothing c left join item i on c.iid = i.iid')
  info = []
  
  for r in cursor:
    tmp = {}
    tmp['info'] = r[0]
    tmp['location'] = r[1]
    tmp['item_condition'] = r[2]
    tmp['iid'] = r[3]
    tmp['uid'] = r[4]
    tmp['price'] = r[5]
    tmp['brand'] = r[6]
    tmp['size'] = r[7]
    info.append(tmp)
  cursor.close()
  return render_template('all_clothing.html',data=info)


@app.route('/all_book')
def all_book():
  cursor = g.conn.execute('select i.info, i.location, i.item_condition, i.iid, i.uid, i.price, b.version, b.subject from book b left join item i on b.iid = i.iid')
  info = []
  
  for r in cursor:
    tmp = {}
    tmp['info'] = r[0]
    tmp['location'] = r[1]
    tmp['item_condition'] = r[2]
    tmp['iid'] = r[3]
    tmp['uid'] = r[4]
    tmp['price'] = r[5]
    tmp['version'] = r[6]
    tmp['subject'] = r[7]
    info.append(tmp)
  cursor.close()
  return render_template('all_book.html',data=info)



@app.route('/all_service')
def all_service():
  cursor = g.conn.execute('select i.info, i.location, i.item_condition, i.iid, i.uid, i.price, s.duration from service s left join item i on s.iid = i.iid')
  info = []
  
  for r in cursor:
    tmp = {}
    tmp['info'] = r[0]
    tmp['location'] = r[1]
    tmp['item_condition'] = r[2]
    tmp['iid'] = r[3]
    tmp['uid'] = r[4]
    tmp['price'] = r[5]
    tmp['service'] = r[6]
    info.append(tmp)
  cursor.close()
  return render_template('all_service.html',data=info)

    
    
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
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
