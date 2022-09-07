from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from passlib.hash import pbkdf2_sha256
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import TodoForm, RegisterForm, LoginForm
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort
# import os

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SECRET_KEY'] = "q1w2e3r4"
Bootstrap(app)

# CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///todo.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dbu2138581:MMMMMMMM@rdbms.strato.de/dbs8438595'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    todos = relationship("Todo", back_populates="author")


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="todos")

    task = db.Column(db.String(250))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def get_all_todos():
    todos = Todo.query.filter_by(status="Open").all()
    return render_template("index.html", all_todos=todos, logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if User.query.filter_by(email=register_form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        new_user = User(
            email=register_form.email.data,
            password=pbkdf2_sha256.hash(register_form.password.data),
            name=register_form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_todos'))

    return render_template("register.html", form=register_form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()

        if user:
            if pbkdf2_sha256.verify(password, user.password):
                login_user(user)
                return redirect(url_for('get_all_todos'))
            else:
                flash('Invalid password provided')
                return redirect(url_for('login'))
        else:
            flash('Invalid user provided')
            return redirect(url_for('login'))

    return render_template("login.html", form=login_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_todos'))


@app.route("/todo/<int:todo_id>", methods=["GET", "POST"])
def show_todo(todo_id):
    requested_todo = Todo.query.get(todo_id)
    return render_template("todo.html", todo=requested_todo, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)


@app.route("/new-todo", methods=["GET", "POST"])
@admin_only
def add_new_todo():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Todo(
            task=form.task.data,
            due_date=form.due_date.data,
            status=form.status.data,
            author=current_user
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("get_all_todos"))
    return render_template("make-todo.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit-todo/<int:todo_id>", methods=["GET", "POST"])
@admin_only
def edit_todo(todo_id):
    todo = Todo.query.get(todo_id)
    edit_form = TodoForm(
        task=todo.task,
        due_date=todo.due_date,
        status=todo.status,
    )
    if edit_form.validate_on_submit():
        todo.task = edit_form.task.data
        todo.due_date = edit_form.due_date.data
        todo.status = edit_form.status.data
        db.session.commit()
        return redirect(url_for("show_todo", todo_id=todo.id))

    return render_template("make-todo.html", form=edit_form, logged_in=current_user.is_authenticated)


@app.route("/delete/<int:todo_id>")
@admin_only
def delete_todo(todo_id):
    todo_to_delete = Todo.query.get(todo_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_todos'))


if __name__ == "__main__":
    app.run(debug=True)
