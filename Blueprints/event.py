from flask import Blueprint, render_template, g, session, request, url_for, redirect, flash

bp = Blueprint('event', __name__, url_prefix='/')


@bp.route('/')
def index():
    g.conn.execute("""
    delete from recommendation
    """)
    return render_template('index.html')


@bp.route('/createNewEvent', methods=['GET', 'POST'])
def create_new_event():
    # history
    email = session['user_email']
    # fetch history depending on email
    history = g.conn.execute("""
        select name, count(*) as times from search_history
         group by email_address,name order by times desc limit 3
        """, email).fetchall()
    if not history:
        history = ['']
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
        is_recur = request.form['recur_sign']

        g.conn.execute("""
        insert into occur_time values (%s,%s)
        """, (is_recur, start_time))

        court_name = request.form['court_name']
        court_loc = request.form['court_loc']
        print(court_name, court_loc)
        # prevent repeat
        repeat = g.conn.execute("""
                select count(*) from courts 
                where label=%s 
                AND name=%s 
                AND location=%s
                """, (sport, court_name, court_loc)).fetchone()
        print(repeat)
        if repeat[0] == 0:
            g.conn.execute("""
                    insert into courts values (%s,%s,%s)
                    """, (sport, court_loc, court_name))

        g.conn.execute("""
        insert into search_history values (%s,%s)
        """, (email, court_name))

        # insert into located
        cid = g.conn.execute("select max(cid) from courts").fetchone()
        locate_data = (session['eid'], cid[0])

        g.conn.execute("""
        insert into located values (%s,%s)
        """, locate_data)
        # insert into occur
        tid = g.conn.execute("select max(tid) from occur_time").fetchone()
        occur_data = (session['eid'], tid[0])
        g.conn.execute("""
                insert into occur values (%s,%s)
                """, occur_data)
        return redirect(url_for('event.my_events'))

    return render_template('createEvent.html', history=history)


@bp.route('/comment', methods=['GET', "POST"])
def comment():
    if request.method == 'POST':
        content = request.form['comment']
        event_id = session['event_id']
        user_id = session['user_email']
        g.conn.execute("""
        insert into comment values (%s,%s,%s)
        """, (user_id, event_id, content))
        return redirect(url_for('event.my_events'))
    return render_template('comment.html')


@bp.route('/my_events')
def my_events():
    owner = session['owner_id']
    events = g.conn.execute("""
    select * from create_events
    where owner = %s
    """, owner).fetchall()
    event_list = []
    for event in events:
        event_list.append([event[1], event[2], event[3]])
    return render_template('my_events.html', event_list=event_list)


@bp.route('/event_details', methods=['GET', 'POST'])
def event_details():
    eid = request.args.get('type')
    print(eid)
    session['event_id'] = eid
    comments = g.conn.execute("""
    select * from comment
    where eid = %s
    """, eid).fetchall()
    print(comments)
    if not comments:
        comment_list = ['']
    else:
        comment_list = []
        for comment in comments:
            comment_list.append([comment[0], comment[1], comment[2], comment[3]])
    event = g.conn.execute("""
    select * from create_events
    where eid = %s
    """, eid).fetchone()
    print(event)
    user = g.conn.execute("""
        select name from users
        where owner = %s
        """, event[0]).fetchone()
    print(user)
    occur_time = g.conn.execute("""
    select t.start_time from create_events e,occur o,occur_time t
    where e.eid = %s
        and o.tid = t.tid
        and e.eid = o.eid
    """, eid).fetchone()
    print(occur_time)
    court = g.conn.execute("""
    select c.location,c.name from create_events e,located l,courts c
    where e.eid = %s
        and e.eid = l.eid
        and l.cid = c.cid
    """, eid).fetchone()
    print(court)
    return render_template('event_details.html', title='Event details', event=event, comments=comment_list,
                           event_time=occur_time[0], court=[court[0], court[1]], user_name=user[0])


@bp.route('/recommendation')
def recommendation():
    user = session['user_email']
    owner = session['owner_id']
    hobby = session['hobby']
    recommendation_list = g.conn.execute("""
    select title,eid from create_events E
    where E.type = %s
        and E.owner!= %s
    order by eid desc
    limit 3
    """, (hobby, owner)).fetchall()
    rid = []
    for recommendation in recommendation_list:
        g.conn.execute("""
        insert into recommendation values (%s,%s,%s)
        """, (recommendation[0], recommendation[1], user))
        id = g.conn.execute("select max(rid) from recommendation").fetchone()
        g.conn.execute("""
        insert into choose values (%s,%s)
        """, (id[0], recommendation[1]))
        rid.append(id[0])

    return render_template('recommendation.html', recommendation_list=recommendation_list, rid=rid)


@bp.route('/invite', methods=['GET', 'POST'])
def invite():
    if request.method == 'POST':
        error = None
        eid = session['eid']
        owner = session['owner_id']
        participant_email = request.form['participant']
        content = request.form['content']
        test = g.conn.execute("""
        select * from users
        where email_address = %s
        """, participant_email).fetchone()
        if test is None:
            error = 'no such user!'
        if error is None:
            participant = g.conn.execute("""
            select participant from users
            where email_address = %s
            """, participant_email).fetchone()
            g.conn.execute("""
            insert into invite values (%s,%s,%s,%s)
            """, (owner, participant[0], eid, content))
            return redirect(url_for('event.index'))
        flash(error)
    return render_template('invite.html')


@bp.route('/mailbox', methods=['GET', 'POST'])
def mailbox():
    participant = session['participant']
    mail_list = g.conn.execute("""
    select owner,eid,content from invite I
    where I.participant = %s
    """, participant).fetchall()
    sender = []
    for mail in mail_list:
        send = []
        send.append(g.conn.execute("""
        select name from users
        where owner = %s
        """, mail['owner']).fetchone()[0])
        send.append(g.conn.execute("""
        select email_address from users
        where owner = %s
        """, mail['owner']).fetchone()[0])
        send.append(g.conn.execute("""
        select title from create_events
        where eid = %s
        """, mail['eid']).fetchone()[0])
        send.append(mail['content'])
        send.append(mail['eid'])
        sender.append(send)
    return render_template('mailbox.html', mail_list=sender)
