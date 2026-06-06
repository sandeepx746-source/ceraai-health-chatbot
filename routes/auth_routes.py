from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
from database.models import User
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()


@auth_bp.record_once
def on_load(state):
    oauth.init_app(state.app)

    oauth.register(
        name='google',
        client_id=state.app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=state.app.config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.chatbot'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        language_pref = request.form.get('language', 'en')

        if not username or not email or not password:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('auth.login'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            language_pref=language_pref
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('views.chatbot'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.chatbot'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('views.chatbot'))

        flash('Login unsuccessful. Please check email and password.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/google-login')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)

    return oauth.google.authorize_redirect(
        redirect_uri,
        prompt='select_account'
    )


@auth_bp.route('/google-callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        user_info = oauth.google.userinfo()

    email = user_info.get('email')

    if not email:
        flash('Google login failed. Email not found.', 'danger')
        return redirect(url_for('auth.login'))

    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('This Google account is not registered. Please register first.', 'danger')
        return redirect(url_for('auth.register'))

    login_user(user)
    return redirect(url_for('views.chatbot'))


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))