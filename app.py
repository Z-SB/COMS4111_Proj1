from flask import Flask, g
from sqlalchemy import *

import config

from Blueprints.auth import bp as auth_bp
from Blueprints.event import bp as event_bp

app = Flask(__name__)
app.config.from_object(config)
app.config.from_mapping(SECRET_KEY='qwerty')

app.register_blueprint(auth_bp)
app.register_blueprint(event_bp)
DB_USER = "js5940"
DB_PASSWORD = "3093"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/proj1part2"

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
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


if __name__ == '__main__':
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=host, port=PORT, debug=true, threaded=threaded)
    run()
