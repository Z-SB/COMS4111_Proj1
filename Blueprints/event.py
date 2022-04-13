from flask import Blueprint, render_template, g, session,request

bp = Blueprint('event', __name__, url_prefix='/')

@bp.route('/')
def index():
    if session.get('user_email'):
        user_events = g.conn.execute("""
        select U.email_address,U.name,E.owner,E.title,E.type
        from users U join create_events E on U.owner = E.owner
        where U.email_address = %s
        """,session.get('user_email')).fetchall()
        return render_template('index.html',event = user_events)
    return render_template('index.html')


@bp.route('/createNewEvent', methods=['GET', 'POST'])
def create_new_event():
    if request.method == 'POST':
        time = request.form['time']
        title = request.form['title']
        sport = request.form['sport']
        g.conn.execute("""
        insert into create_events values (%s,%s,%s)
        """, (1, title, sport))
        return render_template('selectCourt.html')

    return render_template('createEvent.html')