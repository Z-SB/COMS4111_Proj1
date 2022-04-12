from flask import Blueprint, request, g, session, redirect, url_for, flash, render_template
from sqlalchemy import exc


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        user = g.conn.execute("select * from users where email_address = %s",email).fetchone()
        print(user)
        error = None
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
