import os, datetime
from flask import current_app, Blueprint, render_template, abort, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from resumeme import login_manager, flask_bcrypt
from flask.ext.login import (current_user, login_required, login_user, logout_user, confirm_login, fresh_login_required)

import forms
from resumeme.libs.User import User

accounts_flask_login = Blueprint('accounts_flask_login', __name__, template_folder='templates')


@accounts_flask_login.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "email" in request.form:
        email = request.form["email"]
        userObj = User()
        user = userObj.get_by_email_w_password(email)
        if user and flask_bcrypt.check_password_hash(user.password, request.form["password"]) and user.is_active():
            remember = request.form.get("remember", "no") == "yes"

            if login_user(user, remember=remember):
                flash("Logged in!")
                return redirect('/resume/create')
            else:
                flash("unable to log you in")

    return render_template("/accounts/login.html")


#
# user registration.
#
@accounts_flask_login.route("/register", methods=["GET", "POST"])
def register():
    registerForm = forms.SignupForm(request.form)
    current_app.logger.info(request.form)

    if request.method == 'POST' and registerForm.validate() is False:
        current_app.logger.info(registerForm.errors)
        return "uhoh registration error"

    elif request.method == 'POST' and registerForm.validate():
        email = request.form['email']

        # generate password hash
        password_hash = flask_bcrypt.generate_password_hash(request.form['password'])

        # prepare User
        user = User(email, password_hash)
        print user

        try:
            user.save()
            if login_user(user, remember="no"):
                flash("Logged in!")
                return redirect('/')
            else:
                flash("unable to log you in")

        except:
            flash('Registration Error - Use Another Email')
            current_app.logger.error('Registration Error - Use Another Email')

    # prepare registration form
    # registerForm = RegisterForm(csrf_enabled=True)
    templateData = {

        'form': registerForm

    }

    return render_template("/accounts/register.html", **templateData)


@accounts_flask_login.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next") or '/admin')

    templateData = {}
    return render_template("/accounts/reauth.html", **templateData)


@accounts_flask_login.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect('/login')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@login_manager.user_loader
def load_user(id):
    if id is None:
        redirect('/login')
    user = User()
    user.get_by_id(id)
    if user.is_active():
        return user
    else:
        return None
