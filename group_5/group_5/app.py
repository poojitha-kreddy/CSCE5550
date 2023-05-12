# app.py
import re
from flask import render_template, request, redirect, url_for, flash, session
from models import Product, User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import RegistrationForm, LoginForm
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter

from config import app, db
from flask_migrate import Migrate

db.init_app(app)
migrate = Migrate(app, db)

csrf = CSRFProtect()
csrf.init_app(app)





# Configure logging
log_file = 'app.log'
logging.basicConfig(filename=log_file, level=logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
logging.getLogger().addHandler(handler)

# Dummy blocklist for demonstration purposes
BLOCKLIST = {'192.168.1.2'}

# Configure rate limiting
limiter = Limiter(app=app, key_func=lambda: session.get('user_id'), default_limits=["1000 per day", "100 per hour"])

def require_role(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('You need to log in to access this page.')
                return redirect(url_for('login'))
            user = User.query.get(user_id)
            if user.role != role:
                flash('You do not have the required permissions to access this page.')
                return redirect(url_for('homepage'))
            return func(*args, **kwargs)
        return decorated_function
    return decorator

@app.before_request
def blocklist_ip():
    if request.remote_addr in BLOCKLIST:
        logging.warning(f"Blocked IP address: {request.remote_addr}")
        return render_template('403.html'), 403

@app.route('/')
def homepage():
    products = Product.query.all()
    return render_template('homepage.html', products=products)

@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_page.html', product=product)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    csrf_token = form.csrf_token._value()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Hash and salt the password
        hashed_password = generate_password_hash(password)

        # Add the new user to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form,csrf_token=csrf_token)

# Add log entries for user activities and potential security issues
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            logging.info(f"User '{username}' logged in.")
            return redirect(url_for('homepage'))
        else:
            logging.warning(f"Failed login attempt for user '{username}'.")
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('homepage'))

@app.route('/admin/dashboard')
@require_role('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/search')
def search():
    query = request.args.get('query', '')

    # Check for SQL injection payloads
    # pattern = r'''(?:'|\")?[-\s&^*]|(?:'|\")?\sor\s(?:''|\"\")?[-\s&^*]|or\s(?:true--|1=1(?:--|#|\/\*)?)|admin(?:'|\\"|\\)|\))?(?:\s--|\s#|\s\/\*|'or 1=1|' or '1'='1|' or \('1'\)=\('1'|' or 'x'='x|\\") or (\\\"1\\\"=\\\"1|\\\") or \(\\"1\\"\)=\(\\"1\\\"|\\\") or \\"x\\"=\\"x|\d+\s\\"\(?:AND|and)\\s1=0\\s(?:UNION|union)\\s(?:ALL|all)\\s(?:SELECT|select)\\s\\"\(?:admin|81dc9bdb52d04dc20036dbd8313ed055)'''
    pattern = r"(?:\b(select|update|delete|insert)\b|'[\s\S]*?('|\"|\`)|\b(like|=|--|#|;|=0|\|\||\%\d\d|@|@@)\b|AND\s(?:[01]|[tf]rue)|\bOR\b|[0-9]*\-|\*\d+|(?:\bGROUP\sBY\b|\bUNION\sSELECT\b|\bHAVING\b|\bWAITFOR\sDELAY\b|\bORDER\sBY\b)[\s\S]*?--\+?|[^\w\s\,]+|(?:[^\w\s])+[=]+(?:[^\w\s]))"

    # pattern = r"""(?:'|\")?[-\s&^*]|(?:'|\")?\sor\s(?:''|\"\")?[-\s&^*]|or\s(?:true--|1=1(?:--|#|\/\*)?)|admin(?:'|"|\)|\))?(?:\s--|\s#|\s\/\*|'or 1=1|' or '1'='1|' or \('1'\)=\('1'|' or 'x'='x|") or ("1"="1|") or \("1"\)=\("1"|") or "x"="x|\d+\s"(?:AND|and)\s1=0\s(?:UNION|union)\s(?:ALL|all)\s(?:SELECT|select)\s"(?:admin|81dc9bdb52d04dc20036dbd8313ed055)"""
    if re.search(pattern, query, re.IGNORECASE):
        return render_template('search_results.html', message="Please be nice :)")

    # Perform the actual search if no payloads are found
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('search_results.html', products=products)


if __name__ == '__main__':
    app.run(debug=True, port=5019)