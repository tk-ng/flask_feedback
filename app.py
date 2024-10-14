from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Feedback
from forms import LoginForm, RegisterForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedbacks_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "so_damn_cryptic"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Redirects user to the register page."""
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Display the register page or submits the register form to the database."""
    if "username" in session:
        flash("You are currently logged in.", "info")
        return redirect(f"/users/{session["username"]}")

    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_user = User.register(**data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError as err:
            if "users_email_key" in str(err.orig):
                form.email.errors.append(
                    "The email provided already exists in our system. Please login.")
                return render_template("register.html", form=form)
            elif "users_pkey" in str(err.orig):
                form.username.errors.append(
                    f"The username '{form.username.data}' has been taken. Please choose another username.")
                return render_template("register.html", form=form)
        session['username'] = new_user.username
        flash(f"Welcome, {new_user.username}", "success")
        return redirect(f"/users/{new_user.username}")
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display the login page or authenticates the user."""
    if "username" in session:
        flash("You are currently logged in.", "info")
        return redirect(f"/users/{session["username"]}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f"Welcome, {user.username}", "success")
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Incorrect username/password"]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
        flash("You have successfully logged out", "warning")
    return redirect("/login")


@app.route("/users/<username>")
def show_user(username):
    if "username" in session:
        user = User.query.get_or_404(username)
        return render_template("user.html", user=user)
    else:
        flash("Please login first", "danger")
        return redirect("/login")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    user = User.query.get_or_404(username)
    if user.username == session["username"]:
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash("Account has been successfully deleted", "warning")
        return redirect("/")
    elif user.username != session["username"]:
        flash("Action not permitted", "warning")
        return redirect("/")
    else:
        flash("Please login first", "danger")
        return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    user = User.query.get_or_404(username)
    form = FeedbackForm()

    if "username" not in session:
        flash("Please login first", "danger")
        return redirect("/login")
    elif username == session["username"]:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            user.feedbacks.append(
                Feedback(title=title, content=content, username=user.username))
            db.session.commit()
            flash("Feedback submitted", "success")
            return redirect(f"/users/{username}")
    elif username != session["username"]:
        flash("Action not permitted", "warning")
        return redirect("/")

    return render_template("feedback.html", form=form, user=user)


@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback(id):

    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj=feedback)

    if feedback.username == session["username"]:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            return redirect(f"/users/{feedback.user.username}")
        else:
            return render_template("feedback_edit.html", form=form, username=feedback.username)
    elif feedback.username != session["username"]:
        flash("Action not permitted", "warning")
        return redirect("/")


@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete(id):
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(id)
    if feedback.username == session["username"]:
        feedback = Feedback.query.get_or_404(id)
        username = feedback.username
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    elif feedback.username != session["username"]:
        flash("Action not permitted", "warning")
        return redirect("/")
