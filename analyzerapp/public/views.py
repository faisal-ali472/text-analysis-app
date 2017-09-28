# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from analyzerapp.extensions import login_manager
from analyzerapp.public.forms import LoginForm, UserInput
from analyzerapp.user.forms import RegisterForm
from analyzerapp.user.models import User
from analyzerapp.utils import flash_errors

import os
import operator
import re
import requests
import nltk
from nltk.corpus import stopwords
from collections import Counter
from bs4 import BeautifulSoup



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

    errors = []
    results = {}

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


        # Get url that the user has entered
        try:
            url = input_form.input_link.data
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        if r:
            # text processing
            raw = BeautifulSoup(r.text, 'html.parser').get_text()
            nltk.data.path.append(os.getcwd() + '/nltk_data/')  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            # stop words
            no_stop_words = [w.lower() for w in raw_words if w.lower() not in stopwords.words()]
            no_stop_words_count = Counter(no_stop_words)
            # save the results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:20]
            # try:
            #     result = Result(
            #         url=url,
            #         result_all=raw_word_count,
            #         result_no_stop_words=no_stop_words_count
            #     )
            #     db.session.add(result)
            #     db.session.commit()
            # except:
            #     errors.append("Unable to add item to database.")
    return render_template('public/home.html', form=form, input_form=input_form, results=results)


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
