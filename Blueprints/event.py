from flask import Blueprint, render_template, g, session

bp = Blueprint('event', __name__, url_prefix='/')

@bp.route('/')
def index():
    if session.get('user_email'):
        user_events = g.conn.execute("""
        select U.email_address,U.name,E.owner,E.title,E.type
        from users U join create_events E on U.owner = E.owner
        where U.email_address = %s
        """,session.get('user_email')).fetchall()
        print(user_events)
    return render_template('index.html')


