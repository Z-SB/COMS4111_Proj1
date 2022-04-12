import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for, flash, \
    get_flashed_messages
import config

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../Downloads/DatabaseProject/templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_object(config)
app.config.from_mapping(SECRET_KEY='qwerty')

DB_USER = "js5940"
DB_PASSWORD = "3093"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/proj1part2"

engine = create_engine(DATABASEURI)


# engine.execute("""drop table if exists test""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


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
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
    try:
        g.conn.close()
    except exception as e:
        pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/another')
def another():
    return render_template('anotherfile.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     else:
#         email = request.form['email']
#         password = request.form['password']
#         emails = g.conn.execute("SELECT email_address FROM Users where email_address = %s", email).fetchone()
#         if emails is None:
#             return redirect('/noSuchUser')
#         else:
#             confirm_password = g.conn.execute('SELECT name FROM Users where email_address = %s', email).fetchone()
#             if password == list(confirm_password)[0]:
#                 return redirect('/loginSuccess')
#             else:
#                 return redirect('/loginFail')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = g.conn.execute("select * from users where email_address = %s", email).fetchone()
        if user is None:
            error = 'Incorrect Email address.'
        elif user['name'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_name'] = user['name']
            return redirect(url_for('index'))

        flash(error)
        # messages = get_flashed_messages()
    return render_template('login.html')




@app.route('/userInfo', methods=['GET', 'POST'])
def userInfo():
    print(email)
    return render_template('userInfo.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # validators 用于验证
    # email = request.form['email']
    # name = request.form['name']
    # password = request.form['password']
    # confirmed_password = request.form['confirmed_password']
    # if password == confirmed_password:
    return render_template('register.html')
    # else:
    #     return 'password not match'


@app.route('/createEvent')
def createEvent():
    return render_template('createEvent.html')


@app.route('/invite')
def invite():
    return redirect('/userInfo')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/comment')
def comment():
    pass


@app.route('/recommendation')
def recommendation():
    pass


if __name__ == '__main__':
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
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=host, port=PORT, debug=debug, threaded=threaded)


    run()
