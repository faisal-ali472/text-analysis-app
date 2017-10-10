# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, current_app
from flask_login import login_required, logout_user

from analyzerapp.extensions import login_manager
from analyzerapp.public.forms import LoginForm, UserInput
from analyzerapp.user.forms import RegisterForm
from analyzerapp.user.models import User
from analyzerapp.utils import flash_errors
from analyzerapp.celery import create_celery


blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    form = LoginForm(request.form)
    input_form = UserInput(request.form)
    results = []
    # Handle logging in
    if request.method == 'POST':
        # Start: Commented by FA; Nav. bar not required, 27/09/17
        # if form.validate_on_submit():
        #     login_user(form.user)
        #     flash('You are logged in.', 'success')
        #     redirect_url = request.args.get('next') or url_for('user.members')
        #     return redirect(redirect_url)
        # else:
        #     flash_errors(form)
        # End

        # celery init
        celery = create_celery(current_app)

        # # get url that the person has entered
        url = input_form.input_link.data
        res = celery.send_task("tasks.count_words", args=(url,30,))

        print("Task ID: ")
        print(res.id)
        return redirect(url_for('public.get_results', job_key=str(res.id)))
    return render_template('public/home.html', form=form, input_form=input_form, results=results)


@blueprint.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    celery = create_celery(current_app)
    job = celery.AsyncResult(job_key)
    if job.state == 'SUCCESS':
        return jsonify(job.get()['results']), 200
    else:
        return job.state, 202


@blueprint.route("/Viz/")
def plot_visualization():
    return render_template("public/visualize.html")


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)
