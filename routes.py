from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from app import app, db, login_manager
from models import User, Product
from forms import LoginForm, RegisterForm, SearchForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def index():
    search_form = SearchForm()
    products = Product.query.all()

    if search_form.validate_on_submit():
        search_term = search_form.search.data
        products = Product.query.filter(
            or_(
                Product.name.ilike(f'%{search_term}%'),
                Product.category.ilike(f'%{search_term}%')
            )
        ).all()

    return render_template('index.html', products=products, search_form=search_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# du lieu mau de test
def init_products():
    sample_products = [
        Product(name='Cyberpunk 2077', description='Open-world action RPG', category='RPG', price=59.99),
        Product(name='Fortnite', description='Battle Royale game', category='Battle Royale', price=0),
        Product(name='Red Dead Redemption 2', description='Western action-adventure', category='Action', price=59.99),
        Product(name='Rocket League', description='Soccer with cars', category='Sports', price=19.99),
        Product(name='Valorant', description='Tactical shooter', category='Shooter', price=0)
    ]

    for product in sample_products:
        existing_product = Product.query.filter_by(name=product.name).first()
        if not existing_product:
            db.session.add(product)

    db.session.commit()