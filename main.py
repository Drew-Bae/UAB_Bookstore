import os
from urllib import request
from xmlrpc.client import Boolean
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField,
                     SearchField, SelectMultipleField, SelectField, BooleanField, IntegerField, FloatField)
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'finalprojectsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    total = db.Column(db.Integer)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.total


class Store(db.Model):
    __tablename__ = "available books"

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.Text)
    title = db.Column(db.Text)
    numberAvailable = db.Column(db.Integer)
    cost = db.Column(db.Integer)

    def __init__(self, genre, title, numberAvailable, cost):
        self.genre = genre
        self.title = title
        self.numberAvailable = numberAvailable
        self.cost = cost

    def __repr__(self):
        return self.title


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer)

    def __init__(self, total):
        self.total = total

    def __repr__(self):
        return self.total


class Title(db.Model):
    __tablename__ = "title"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return self.title


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={
                           "placeholder": "Username"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={
                             "placeholder": "Password"})
    login = SubmitField('Login')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={
                           "placeholder": "Username"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={
                             "placeholder": "Password"})
    confirmPassword = PasswordField("Confirm Password", validators=[
                                    DataRequired()], render_kw={"placeholder": "Confirm Password"})
    register = SubmitField('Register Now')


class MainForm(FlaskForm):
    title = SelectField()
    addCart = SubmitField('Add to Cart')

    def __init__(self):
        super(MainForm, self).__init__()
        self.title.choices = Store.query.order_by(Store.title).all()


class ManagerForm(FlaskForm):
    genre = StringField('Genre', render_kw={"placeholder": "Genre"})
    title = StringField('Title', render_kw={"placeholder": "Title"})
    numberAvailable = IntegerField('Number Available', render_kw={
                                   "placeholder": "Number Available"})
    cost = FloatField('Cost', render_kw={"placeholder": "Cost of book"})
    submit = SubmitField('Add')


@app.route('/', methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        session['username'] = form.username.data
        session['password'] = form.password.data
        test = User.query.filter_by(username=session['username']).first()
        if test == None:
            return redirect(url_for('signin'))
        elif test.password == 'pass' and test.username == 'Manager':
            return redirect(url_for('manager'))
        elif test.password == session['password']:
            return redirect(url_for('mainpage', test=session['username']))
        else:
            return redirect(url_for('signin'))
    return render_template('signIn.html', form=form)


@app.route('/signUp.html', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        session['username'] = form.username.data
        session['password'] = form.password.data
        session['confirmPassword'] = form.confirmPassword.data
        new_user = User(session['username'], session['password'])
        test = User.query.filter_by(username=session['username']).first()
        if test != None:
            return redirect(url_for('signup'))
        elif session['password'] != session['confirmPassword']:
            return redirect(url_for('signup'))
        else:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('signin'))
    return render_template('signUp.html', form=form)


@app.route('/main.html', methods=['GET', 'POST'])
def mainpage():
    form = MainForm()
    history = Store.query.filter_by(genre='History').all()
    horror = Store.query.filter_by(genre='Horror').all()
    test = request.args.get('test', None)
    if form.validate_on_submit():
        session['title'] = form.title.data
        book = Store.query.filter_by(title=session['title']).first()
        cost = book.cost
        add = Cart.query.order_by(Cart.id.desc()).first()
        add1 = add.total
        db.session.add(Cart(add1))
        db.session.commit()
        db.session.add(Title(session['title']))
        db.session.commit()
        return redirect(url_for('cart', test=session['title'], cost=cost))
    return render_template('main.html', history=history, horror=horror, test=test, form=form)


@app.route('/cart.html', methods=['GET', 'POST'])
def cart():
    test = request.args.get('test', None)
    cost = request.args.get('cost', None)
    add = Cart.query.order_by(Cart.id.desc()).first()
    add1 = add.total
    db.session.add(Cart(float(cost)+add1))
    db.session.commit()
    add = Cart.query.order_by(Cart.id.desc()).first()
    add1 = add.total
    title = Title.query.order_by(Title.title).all()
    if request.method == 'POST':
        if request.form.get('buy') == 'Buy':
            sendTotal = Cart.query.order_by(Cart.id.desc()).first()
            sendTotal1 = sendTotal.total
            db.session.query(Cart).delete()
            db.session.commit()
            sendTitle = Title.query.order_by(Title.title).all()
            return redirect(url_for('manager', sendTotal1=sendTotal1, sendTitle=sendTitle))
    return render_template('cart.html', test=test, add1=add1, title=title)


@app.route('/manager.html', methods=['GET', 'POST'])
def manager():
    orderTitle = Title.query.order_by(Title.title).all()
    db.session.query(Title).delete()
    db.session.commit()
    form = ManagerForm()
    if form.validate_on_submit():
        session['genre'] = form.genre.data
        session['title'] = form.title.data
        session['available'] = form.numberAvailable.data
        session['cost'] = form.cost.data
        db.session.add(Store(
            session['genre'], session['title'], session['available'], session['cost']))
        db.session.commit()
        return redirect(url_for('manager'))
    return render_template('manager.html', form=form, orderTitle=orderTitle)


if __name__ == '__main__':
    db.create_all()
    db.session.add(Cart(0))
    db.session.add(User('Manager', 'pass'))
    db.session.commit()
    app.run(debug=True)
