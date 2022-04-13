from flask import Blueprint, render_template, g, session, request, url_for,redirect

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
        # time = request.form['time']
        title = request.form['title']
        sport = request.form['sport']
        g.conn.execute("""
        insert into create_events values (%s,%s,%s)
        """, (1, title, sport))
        return render_template('selectCourt.html')

    return render_template('createEvent.html')

@bp.route('/comment',methods = ["POST"])
def comment():
    content = request.form['content']
    event_id = session['event_id']
    user_id = session['user_email']
    g.conn.execute("""
    insert into comment values (%s,%s,%s)
    """,(user_id,event_id,content))
    return redirect(url_for('event.event_details'))


@bp.route('/event_details')
def event_details():
    owner = session['owner_id']
    event_list = g.conn.execute("""
    select * from create_events
    where owner = %s
    """,owner).fetchall()
    return render_template('event_details.html',event_list = event_list)


@bp.route('/recommendation')
def recommendation():
    # user = session['user_email']
    owner = session['owner_id']
    hobby = session['hobby']
    recommendation_list = g.conn.execute("""
    select title,eid from create_events E
    where E.type = %s
        and E.owner!= %s
    """,(hobby,owner)).fetchall()
    return render_template('recommendation.html',recommendation_list = recommendation_list)


