from flask import Blueprint, render_template, g, session, request, url_for, redirect

bp = Blueprint('event', __name__, url_prefix='/')


@bp.route('/')
def index():

    return render_template('index.html')


@bp.route('/createNewEvent', methods=['GET', 'POST'])
def create_new_event():

    # history
    email = session['user_email']
    # fetch history depending on email
    history = g.conn.execute("""
    select name from search_history where email_address = %s
    """, email).fetchone()

    if request.method == 'POST':
        owner_id = session['owner_id']
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

        return redirect(url_for('event.event_details'))

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


@bp.route('/invite',methods = ['GET','POST'])
def invite():
    if request.method == 'POST':
        owner = session['owner_id']
        participant_email = request.form['participant']
        content = request.form['content']
        participant = g.conn.execute("""
        select participant from users
        where email_address = %s
        """,participant_email).fetchone()
        g.conn.execute("""
        insert into invite values (%s,%s,%s)
        """,(owner,participant[0],content))
        return redirect(url_for('event.index'))
    return render_template('invite.html')


@bp.route('/mailbox', methods=['GET', 'POST'])
def mailbox():
    participant = session['participant']
    mail_list = g.conn.execute("""
    select owner,content from invite I
    where I.participant = %s
    """, participant).fetchall()
    sender = []
    for mail in mail_list:
        send = []
        send.append(g.conn.execute("""
        select name from users
        where owner = %s
        """, mail['owner']).fetchone())
        send.append(g.conn.execute("""
        select email_address from users
        where owner = %s
        """, mail['owner']).fetchone())
        send.append(mail['content'])
        sender.append(send)
    return render_template('mailbox.html', mail_list=sender)
