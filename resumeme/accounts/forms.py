# coding=utf-8
import models
from flask.ext.mongoengine.wtf import model_form
from wtforms.fields import *
from flask.ext.mongoengine.wtf.orm import validators

user_form = model_form(models.User, exclude=['password'])


# Signup Form created from user_form
class SignupForm(user_form):
    password = PasswordField('Password', validators=[validators.DataRequired(),
                                                     validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    location = StringField('Location')
    source = SelectField('source', choices=[('', 'Veuillez sélectionner une source'),
                                            ('searchengine', 'Moteur de recherche'),
                                            ('friend', 'Ami'),
                                            ('website', 'Site web'),
                                            ('print', 'Imprimer l’article / le flyer'),
                                            ('radio', 'Radio'),
                                            ('school', 'École ou recherche scolaire')])

    sourceoptional = StringField()


# Login form will provide a Password field
class LoginForm(user_form):
    password = PasswordField('Password', validators=[validators.DataRequired()])


# Password Forgot Form
class ForgotPasswordForm(user_form):
    email = StringField('Email', validators=[validators.DataRequired()])


# Password Reset Form
class ResetPasswordForm(user_form):
    password = PasswordField('Mot de passe', validators=[validators.DataRequired(),
                                                     validators.EqualTo('confirm')])

    confirm = PasswordField('Répéter le mot de passe', validators=[validators.DataRequired()])


# Change Role Form
class updateProfileForm(user_form):
    role = SelectField('role', validators=[validators.DataRequired()])

    editusername = StringField('Nom d\'utilisateur')


# Password Forgot Form
class ActivateAccountForm(user_form):
    email = StringField('Email', validators=[validators.DataRequired()])
