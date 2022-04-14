from flask import Blueprint, render_template, g, session, request, url_for, redirect

bp = Blueprint('event', __name__, url_prefix='/')


@bp.route('/')
def index():
    # print(session['user_email'])
    if session.get('user_email'):
        user_events = g.conn.execute("""
        select U.email_address,U.name,E.owner,E.title,E.type
        from users U join create_events E on U.owner = E.owner
        where U.email_address = %s
        """, session.get('user_email')).fetchall()
        return render_template('index.html', event=user_events)
    return render_template('index.html')


@bp.route('/createNewEvent', methods=['GET', 'POST'])
def create_new_event():
    # history
    email = session['user_email']
    # fetch history depending on email
    history = g.conn.execute("""
    select name from search_history where email_address = %s
    """, email).fetchone()
    item_list = ["", "", ""]
    for i in range(len(history)):
        item_list[i] = history[i]
    item_0 = item_list[0]
    item_1 = item_list[1]
    item_2 = item_list[2]
    print(item_0)
    if request.method == 'POST':
        owner_id = session['owner_id']
        print('something')
        title = request.form['title']
        sport = request.form['sport']
        g.conn.execute("""
        insert into create_events values (%s,%s,%s)
        """, (owner_id, title, sport))
        print(owner_id, title, sport)

        eid = g.conn.execute("select max(eid) from create_events").fetchone()

        session['eid'] = eid[0]

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

        g.conn.execute("""
        insert into search_history values (%s,%s)
        """, (email, court_name))

        return render_template(url_for('event.event_details'))

    return render_template('createEvent.html', history=history)


@bp.route('/comment', methods=["POST"])
def comment():
    content = request.form['content']
    event_id = session['event_id']
    user_id = session['user_email']
    g.conn.execute("""
    insert into comment values (%s,%s,%s)
    """, (user_id, event_id, content))
    return redirect(url_for('event.event_details'))


@bp.route('/event_details')
def event_details():
    owner = session['owner_id']
    event_list = g.conn.execute("""
    select * from create_events
    where owner = %s
    """, owner).fetchall()
    return render_template('event_details.html', event_list=event_list)


@bp.route('/recommendation')
def recommendation():
    # user = session['user_email']
    owner = session['owner_id']
    hobby = session['hobby']
    recommendation_list = g.conn.execute("""
    select title,eid from create_events E
    where E.type = %s
        and E.owner!= %s
    """, (hobby, owner)).fetchall()
    return render_template('recommendation.html', recommendation_list=recommendation_list)
