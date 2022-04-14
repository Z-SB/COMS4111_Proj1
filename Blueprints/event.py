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

        owner_id = 1
        title = request.form['title']
        sport = request.form['sport']
        g.conn.execute("""
        insert into create_events values (%s,%s,%s)
        """, (owner_id, title, sport))
        print(owner_id, title, sport)

        eid = g.conn.execute("select max(eid) from create_events").fetchone()

        session['eid'] = eid[0]
        print(session)
        start_time = request.form['time']
        # end_time = request.form['end_time']
        is_recur = False

        g.conn.execute("""
        insert into occur_time values (%s,%s,%s)
        """, (is_recur, start_time, start_time))

        court_name = request.form['court_name']
        court_loc = request.form['court_loc']
        print(court_name, court_loc)
        g.conn.execute("""
        insert into courts values (%s,%s,%s)
        """, (sport, court_name, court_loc))



    return render_template('createEvent.html')