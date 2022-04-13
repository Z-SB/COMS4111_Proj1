import functools

from flask import Blueprint, request, g, session, redirect, url_for, flash, render_template
from sqlalchemy import *

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = g.conn.execute("select * from users where email_address = %s", email).fetchone()
        error = None
        if user is None:
            error = 'Incorrect Email address.'
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_email'] = user['email_address']
            session['owner_id'] = user['owner']
            session['user_name'] = user['name']
            session['participant'] = user['participant']
            session['hobby'] = user['hobby']
            # session['']
            return redirect(url_for('event.index'))

        flash(error)
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        hobby = request.form['hobby']
        error = None

        if not email:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        data = (email, username, password, hobby)
        if error is None:
            try:
                g.conn.execute(
                    "INSERT INTO users VALUES (%s, %s, %s, %s)",
                    data
                )

            except exc.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('register.html')


@bp.before_app_request
def load_logged_in_user():
    user_email = session.get('user_email')
    if user_email is None:
        g.user = None
    # else:
    #     user = g.conn.execute('select * from users where email_address = %s', user_email).fetchone()
    #     print(user)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view()